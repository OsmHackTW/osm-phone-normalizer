import concurrent.futures
import json
import logging
import threading
import time
from pathlib import Path

from overpass.areas import Area
from overpass.config import OUTPUT_DIR, REQUEST_DELAY
from overpass.nominatim import resolve_bbox
from overpass.overpass import fetch_area

log = logging.getLogger(__name__)


def _apply_filters(elements: list[dict], area: Area) -> list[dict]:
    """Filter elements by area.filters using 'if avail' semantics:
    keep elements where each filter tag is absent OR matches the expected value.
    
    For Taiwan, we allow interchange between 臺 and 台 in addr:city.
    """
    if not area.filters:
        return elements

    def matches(elem: dict) -> bool:
        tags = elem.get("tags", {})
        for k, expected in area.filters.items():
            if k not in tags:
                continue
            val = tags[k].strip()
            if val == expected:
                continue
            # Special case for Taiwan: allow 臺/台 interchange for addr:city
            if k == "addr:city" and isinstance(val, str) and isinstance(expected, str):
                if val.replace("台", "臺") == expected.replace("台", "臺"):
                    continue
            return False
        return True

    filtered = [e for e in elements if matches(e)]
    removed = len(elements) - len(filtered)
    if removed:
        log.info("Tag filter: removed %d/%d element(s) from %s", removed, len(elements), area.name)
    return filtered


def batch_fetch(
    areas: list[Area],
    output_dir: Path = OUTPUT_DIR,
    delay: float = REQUEST_DELAY,
    skip_existing: bool = True,
    progress_callback=None,
    max_workers: int = 4,
) -> dict[str, list[dict]]:
    """
    Fetch phone-tagged OSM entities for a list of areas.
    Saves each area's results as a JSON file and returns a combined dict.
    Uses ThreadPoolExecutor for parallel cache loading; Overpass requests are
    serialised (one at a time) to respect the API rate limit.

    Companion areas: some areas declare ``companions`` — other areas whose
    bboxes overlap and must be co-fetched so the dedup pass can correctly
    assign each OSM element to its most-specific area.  Companions are added
    to the fetch list automatically and silently removed from the returned
    dict unless the caller already requested them.

    Args:
        areas:        list of Area objects to query
        output_dir:   directory to save per-area JSON files
        delay:        minimum seconds between Overpass requests
        skip_existing: if True, load from cache instead of re-fetching
        max_workers:  thread pool size (applies to cache loading only)

    Returns:
        dict of {area.name: [elements]}
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Expand companion areas --------------------------------------------
    # Companions must participate in the dedup pass to prevent bbox overlap
    # from leaking foreign elements into the requesting area's results.
    requested_names: set[str] = {a.name for a in areas}
    fetch_areas: list[Area] = list(areas)
    seen_companions: set[str] = set(requested_names)
    for area in areas:
        for comp in area.companions:
            if comp.name not in seen_companions:
                log.info(
                    "Companion: fetching %s alongside %s for accurate dedup "
                    "(their bboxes overlap — co-fetching ensures no elements "
                    "are double-counted)",
                    comp.name,
                    area.name,
                )
                fetch_areas.append(comp)
                seen_companions.add(comp.name)
    # -----------------------------------------------------------------------

    # Resolve missing bboxes via Nominatim, with a persistent cache file
    bbox_cache_file = output_dir / "bbox_cache.json"
    bbox_cache: dict = {}
    bbox_lock = threading.Lock()
    if bbox_cache_file.exists():
        bbox_cache = json.loads(bbox_cache_file.read_text(encoding="utf-8"))

    def resolve_area_bbox(area: Area) -> None:
        if area.bbox is None:
            with bbox_lock:
                bbox = resolve_bbox(area.name, bbox_cache)
                if bbox is not None:
                    area.bbox = bbox
                    bbox_cache_file.write_text(
                        json.dumps(bbox_cache, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                else:
                    raise ValueError(f"Could not resolve bbox for {area.name!r}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(resolve_area_bbox, fetch_areas))

    results: dict[str, list[dict]] = {}
    results_lock = threading.Lock()
    # Overpass requests must be serialised — one in-flight at a time
    overpass_lock = threading.Lock()
    last_request_time = [0.0]
    completed_count = [0]

    def fetch_one(area: Area) -> None:
        cache_file = output_dir / f"{area.name}.json"
        is_companion = area.name not in requested_names
        label = f"{area.name} (companion)" if is_companion else area.name

        if skip_existing and cache_file.exists():
            log.info("%-20s — loading from cache", label)
            elements = json.loads(cache_file.read_text(encoding="utf-8"))
            elements = _apply_filters(elements, area)
            with results_lock:
                results[area.name] = elements
                completed_count[0] += 1
                if progress_callback and not is_companion:
                    progress_callback(completed_count[0], len(fetch_areas), area.name, True)
            return

        with overpass_lock:
            wait = delay - (time.monotonic() - last_request_time[0])
            if wait > 0:
                log.debug("Throttling — waiting %.1fs before %s", wait, label)
                time.sleep(wait)
            log.info("Fetching %s ...", label)
            last_request_time[0] = time.monotonic()
            elements = fetch_area(area)

        cache_file.write_text(
            json.dumps(elements, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        elements = _apply_filters(elements, area)
        with results_lock:
            results[area.name] = elements
            completed_count[0] += 1
            if progress_callback and not is_companion:
                progress_callback(completed_count[0], len(fetch_areas), area.name, False)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(fetch_one, fetch_areas))

    # Dedup by OSM ID — assign each element to the smallest (most specific) bbox.
    # Companions participate in this pass so their elements are correctly claimed
    # before the larger overlapping area processes its results.
    seen: dict[int, str] = {}
    for area in sorted(fetch_areas, key=lambda a: a.bbox_area):
        if area.name not in results:
            continue
        deduped = []
        for elem in results[area.name]:
            eid = elem["id"]
            if eid not in seen:
                seen[eid] = area.name
                deduped.append(elem)
        removed = len(results[area.name]) - len(deduped)
        if removed:
            log.info("Dedup: removed %d duplicate(s) from %s", removed, area.name)
        results[area.name] = deduped
        cache_file = output_dir / f"{area.name}.json"
        cache_file.write_text(
            json.dumps(deduped, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # Strip companions that the caller did not explicitly request
    return {name: elems for name, elems in results.items() if name in requested_names}

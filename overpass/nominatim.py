import logging
import time

import requests

from overpass.config import NOMINATIM_DELAY, NOMINATIM_URL

log = logging.getLogger(__name__)


def resolve_bbox(name: str, cache: dict, country: str = "tw") -> tuple | None:
    if name in cache:
        return tuple(cache[name])
    time.sleep(NOMINATIM_DELAY)
    try:
        r = requests.get(
            NOMINATIM_URL,
            params={"q": name, "countrycodes": country, "format": "json", "limit": 1},
            headers={"User-Agent": "osm-phone-fetcher/1.0"},
            timeout=10,
        )
        r.raise_for_status()
        results = r.json()
    except requests.RequestException as e:
        log.warning("Nominatim lookup failed for %s: %s", name, e)
        return None
    if not results:
        log.warning("Nominatim returned no results for %s", name)
        return None
    bb = results[0]["boundingbox"]  # [south, north, west, east] as strings
    bbox = (float(bb[0]), float(bb[2]), float(bb[1]), float(bb[3]))  # → (s,w,n,e)
    cache[name] = list(bbox)
    return bbox

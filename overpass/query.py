import logging

from overpass.areas import Area
from overpass.config import TIMEOUT
from overpass.nominatim import resolve_bbox

log = logging.getLogger(__name__)

PHONE_KEYS = ["phone", "contact:phone"]
ENTITY_TYPES = ["node", "way", "relation"]

_bbox_cache: dict = {}


def build_query(area: Area, phone_keys=PHONE_KEYS, entity_types=ENTITY_TYPES) -> str:
    if area.use_area_query:
        union_lines = "\n  ".join(
            f'{etype}["{key}"](area.a);'
            for etype in entity_types
            for key in phone_keys
        )
        return f"""[out:json][timeout:{TIMEOUT}];
area["name"="{area.name}"]["admin_level"="{area.admin_level}"]->.a;
(
  {union_lines}
);
out meta center;""".strip()

    if area.bbox is None:
        log.info("No bbox for %s — resolving via Nominatim", area.name)
        bbox = resolve_bbox(area.name, _bbox_cache)
        if bbox is None:
            raise ValueError(f"Could not resolve bbox for '{area.name}' 找不到 '{area.name}' 的範圍")
        area.bbox = bbox
    s, w, n, e = area.bbox
    union_lines = "\n  ".join(
        f'{etype}["{key}"]({s},{w},{n},{e});'
        for etype in entity_types
        for key in phone_keys
    )
    return f"""[out:json][timeout:{TIMEOUT}];
(
  {union_lines}
);
out meta center;""".strip()

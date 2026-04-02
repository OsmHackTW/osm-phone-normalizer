import argparse
import logging
from pathlib import Path

from overpass.areas import Area, resolve_area
from overpass.presets.TW import (
    AREA_ALIASES,
    EN_ALIASES,
    ZH_ALIAS,
    TAIWAN_AREAS,
    PRESETS,
)
from overpass.batch import batch_fetch
from overpass.config import OUTPUT_DIR, REQUEST_DELAY

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

_ALIASES = {**AREA_ALIASES, **EN_ALIASES, **ZH_ALIAS}
_CITY_LOOKUP = {a.name: a for a in TAIWAN_AREAS}

parser = argparse.ArgumentParser(description="Batch fetch OSM phone entities by area")
parser.add_argument(
    "--target",
    choices=list(PRESETS),
    default="taipei",
    help="Which preset area set to fetch (default: taipei)",
)
parser.add_argument(
    "--target",
    metavar="NAME",
    help="Fetch a single named area (alias-resolved, then Nominatim fallback)",
)
parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
parser.add_argument(
    "--delay",
    type=float,
    default=0,
    help="Seconds between requests (default: 0 for single --target, "
    f"{REQUEST_DELAY} for batch targets)",
)
parser.add_argument("--no-cache", action="store_true", help="Re-fetch even if cached")
args = parser.parse_args()

if args.name:
    areas = [resolve_area(args.name, _ALIASES, _CITY_LOOKUP)]
else:
    areas = PRESETS[args.target]
    if args.delay == 0:
        args.delay = REQUEST_DELAY

results = batch_fetch(
    areas,
    output_dir=args.output_dir,
    delay=args.delay,
    skip_existing=not args.no_cache,
)

total = sum(len(v) for v in results.values())
log.info("Done. Total entities: %d across %d areas", total, len(results))

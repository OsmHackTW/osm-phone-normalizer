import os
from pathlib import Path

OVERPASS_URL = os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter")
REQUEST_DELAY = 30  # minimum seconds between requests
TIMEOUT = 90        # overpass query timeout in seconds
OUTPUT_DIR = Path("cache")

NOMINATIM_URL = os.getenv("NOMINATIM_URL", "https://nominatim.openstreetmap.org/search")
NOMINATIM_DELAY = 1  # OSM usage policy: max 1 req/sec

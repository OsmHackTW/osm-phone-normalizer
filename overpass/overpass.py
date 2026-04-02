import logging
import time

import requests

from overpass.areas import Area
from overpass.config import OVERPASS_URL, TIMEOUT
from overpass.query import build_query

log = logging.getLogger(__name__)


def fetch_area(area: Area, retries: int = 3, backoff: int = 15) -> list[dict]:
    query = build_query(area)
    log.debug("Query for %s:\n%s", area.name, query)

    for attempt in range(1, retries + 1):
        try:
            r = requests.post(OVERPASS_URL, data={"data": query}, timeout=TIMEOUT + 10)
            r.raise_for_status()
            elements = r.json().get("elements", [])
            log.info("%-10s — %d entities", area.name, len(elements))
            return elements
        except requests.RequestException as e:
            log.warning(
                "Attempt %d/%d failed for %s: %s", attempt, retries, area.name, e
            )
            if attempt < retries:
                wait = backoff * attempt
                if isinstance(e, requests.HTTPError) and e.response is not None:
                    status = e.response.status_code
                    if status == 429:
                        wait = int(e.response.headers.get("Retry-After", wait))
                        log.info("Rate limited (429) — waiting %ds", wait)
                    elif status == 504:
                        wait = backoff * attempt * 2
                        log.info("Gateway timeout (504) — waiting %ds", wait)
                time.sleep(wait)

    raise ValueError(f"All retries failed for {area.name!r} — check Overpass API availability")

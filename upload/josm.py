"""Push changes to a running JOSM instance via Remote Control (port 8111)."""

import logging
import urllib.parse

import requests

JOSM_RC = "http://localhost:8111"

log = logging.getLogger(__name__)


def open_in_josm(osc_xml: str) -> bool:
    """
    Send OSC XML to JOSM Remote Control, opening it as a new layer.

    JOSM must be running with Remote Control enabled
    (Edit → Preferences → Remote Control → Enable Remote Control).

    Args:
        osc_xml: .osc XML string (as produced by build_osc)
    Returns:
        True if JOSM accepted the data, False if unreachable or rejected.
    """
    url = f"{JOSM_RC}/load_data?new_layer=true&layer_name=phone-normalizer"
    try:
        r = requests.post(url, data=osc_xml.encode(), timeout=5)
        r.raise_for_status()
        log.info("Loaded changes into JOSM (Remote Control)")
        return True
    except requests.RequestException as exc:
        log.warning("JOSM Remote Control not reachable or rejected request: %s", exc)
        return False

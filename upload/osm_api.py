"""Builds an OSM Change (.osc) file and uploads via the OSM API."""

import logging
import xml.etree.ElementTree as ET
from xml.dom import minidom

import requests

GENERATOR = "osmtw-phone-normalizer"
OSM_API = "https://api.openstreetmap.org/api/0.6"

log = logging.getLogger(__name__)


def _build_osc_root(
    diffs: list[tuple[dict, dict]],
    changeset_id: int | None = None,
) -> ET.Element:
    """Build an osmChange XML tree from diffs, optionally stamping a changeset id."""
    root = ET.Element("osmChange", version="0.6", generator=GENERATOR)
    modify = ET.SubElement(root, "modify")

    for elem, changes in diffs:
        etype = elem["type"]           # "node", "way", "relation"
        attribs = {
            "id":      str(elem["id"]),
            "version": str(elem["version"]),
        }
        if changeset_id is not None:
            attribs["changeset"] = str(changeset_id)
        if etype == "node":
            attribs["lat"] = str(elem.get("lat") or elem["center"]["lat"])
            attribs["lon"] = str(elem.get("lon") or elem["center"]["lon"])

        node_el = ET.SubElement(modify, etype, attribs)

        for ref in elem.get("nodes", []):
            ET.SubElement(node_el, "nd", ref=str(ref))

        for member in elem.get("members", []):
            ET.SubElement(node_el, "member",
                          type=member["type"],
                          ref=str(member["ref"]),
                          role=member.get("role", ""))

        updated_tags = {**elem.get("tags", {})}
        for k, v in changes.items():
            if v is None:
                updated_tags.pop(k, None)
            else:
                updated_tags[k] = v
        for k, v in updated_tags.items():
            ET.SubElement(node_el, "tag", k=k, v=v)

    return root


def build_osc(diffs: list[tuple[dict, dict]]) -> str:
    """
    Build a pretty-printed .osc XML string from a list of (element, changes) tuples.

    Args:
        diffs: list of (overpass_element, changes_dict) where
               changes_dict maps tag_key → new_value (None = delete tag)
    Returns:
        Pretty-printed .osc XML string
    """
    root = _build_osc_root(diffs)
    return minidom.parseString(
        ET.tostring(root, encoding="unicode")
    ).toprettyxml(indent="  ")


def _build_osc_xml(diffs: list[tuple[dict, dict]], changeset_id: int) -> str:
    """Like build_osc but stamps changeset="<id>" on every element (required by OSM API)."""
    return ET.tostring(_build_osc_root(diffs, changeset_id), encoding="unicode")


def upload_osm(
    diffs: list[tuple[dict, dict]],
    access_token: str,
    comment: str = "Normalize phone numbers to E.123 format",
    dry_run: bool = False,
) -> int:
    """
    Upload diffs directly to the OSM API using an OAuth2 bearer token.

    Flow: create changeset → upload diff → close changeset.

    Args:
        diffs:        list of (overpass_element, changes_dict)
        access_token: OSM OAuth2 bearer token (set OSM_ACCESS_TOKEN env var)
        comment:      changeset comment tag
        dry_run:      if True, skip actual HTTP calls and log what would happen

    Returns:
        changeset ID (0 if dry_run)

    Raises:
        requests.HTTPError on API failure
    """
    if not diffs:
        log.info("Nothing to upload.")
        return 0

    missing_version = [e for e, _ in diffs if "version" not in e]
    if missing_version:
        raise ValueError(
            f"{len(missing_version)} element(s) missing 'version' — "
            "re-run with --no-cache to fetch metadata"
        )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "text/xml; charset=utf-8",
    }

    # 1. Create changeset
    changeset_xml = (
        '<osm><changeset>'
        f'<tag k="created_by" v="{GENERATOR}"/>'
        f'<tag k="comment" v="{comment}"/>'
        '</changeset></osm>'
    )
    log.info("Creating changeset (comment: %r)…", comment)
    if dry_run:
        log.info("[dry-run] POST %s/changeset/create", OSM_API)
        log.info("[dry-run] Would upload %d element(s)", len(diffs))
        return 0

    r = requests.put(f"{OSM_API}/changeset/create", data=changeset_xml.encode(), headers=headers)
    r.raise_for_status()
    changeset_id = int(r.text.strip())
    log.info("Changeset %d created", changeset_id)

    # 2. Upload diff
    try:
        osc = _build_osc_xml(diffs, changeset_id)
        r = requests.post(
            f"{OSM_API}/changeset/{changeset_id}/upload",
            data=osc.encode("utf-8"),
            headers=headers,
        )
        r.raise_for_status()
        log.info("Uploaded %d change(s) to changeset %d", len(diffs), changeset_id)
    finally:
        # 3. Always close the changeset, even on upload error
        requests.put(f"{OSM_API}/changeset/{changeset_id}/close", headers=headers)
        log.info("Changeset %d closed", changeset_id)

    return changeset_id

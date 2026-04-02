"""Level0 integration — URL generator and text-format builder."""

import urllib.parse

LEVEL0 = "https://level0.osmz.ru/"
OVERPASS_API = "https://overpass-api.de/api/interpreter"


def level0_url(query: str) -> str:
    """
    Build a Level0 URL that loads data directly from Overpass.

    Level0 fetches OSM XML from the encoded URL, so the query must use
    [out:xml].  build_query() emits [out:json]; this function swaps it.

    Args:
        query: Overpass QL string (json or xml output directive)
    Returns:
        https://level0.osmz.ru/?url=<encoded_overpass_url>
    """
    xml_query = query.replace("[out:json]", "[out:xml]", 1)
    overpass_url = f"{OVERPASS_API}?data={urllib.parse.quote(xml_query)}"
    return f"{LEVEL0}?url={urllib.parse.quote(overpass_url)}"


def build_level0(diffs: list[tuple[dict, dict]]) -> str:
    """
    Build Level0 text format from a list of (element, changes) tuples.
    Useful for pasting into http://level0.osmz.ru when a URL isn't enough.

    Args:
        diffs: list of (overpass_element, changes_dict) where
               changes_dict maps tag_key → new_value (None = delete tag)
    Returns:
        Level0 text string
    """
    blocks = []

    for elem, changes in diffs:
        etype = elem["type"]
        lines = [f"{etype} {elem['id']} v{elem['version']}"]

        if etype == "node":
            lat = elem.get("lat") or elem["center"]["lat"]
            lon = elem.get("lon") or elem["center"]["lon"]
            lines.append(f"  lat: {lat}")
            lines.append(f"  lon: {lon}")

        for ref in elem.get("nodes", []):
            lines.append(f"  nd: {ref}")

        for member in elem.get("members", []):
            role = member.get("role", "")
            entry = f"  mbr: {member['type']} {member['ref']}"
            if role:
                entry += f" {role}"
            lines.append(entry)

        updated_tags = {**elem.get("tags", {})}
        for k, v in changes.items():
            if v is None:
                updated_tags.pop(k, None)
            else:
                updated_tags[k] = v
        for k, v in updated_tags.items():
            lines.append(f"  {k} = {v}")

        blocks.append("\n".join(lines))

    return "\n\n".join(blocks) + "\n"

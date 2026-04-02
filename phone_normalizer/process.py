from phonenumbers import PhoneNumberFormat

from phone_normalizer.countries import normalizer_for


_PHONE_KEYS = (
    "phone",
    "contact:phone",
    "fax",
    "contact:fax",
    "phone:mobile",
    "contact:mobile",
    "emergency:phone",
    "phone:delivery",
)


def process_node(
    tags: dict,
    fmt: int = PhoneNumberFormat.INTERNATIONAL,
    region: str = "TW",
) -> dict:
    """
    Given an OSM node's tag dict, return a dict of {tag: new_value} for any
    phone/fax tags that can be normalized.
    Also sanitizes addr:city for Taiwan.
    Uses a 'best effort' approach: if a part cannot be normalized, it's kept as-is.
    """
    normalize = normalizer_for(region)
    changes = {}

    # Data sanitization for Taiwan: normalize addr:city
    if region == "TW" and "addr:city" in tags:
        city = tags["addr:city"]
        if "台" in city:
            new_city = city.replace("台", "臺")
            if new_city != city:
                changes["addr:city"] = new_city

    for key in _PHONE_KEYS:
        if key not in tags:
            continue
        parts = [p.strip() for p in tags[key].split(";")]
        normalized = []
        for p in parts:
            n = normalize(p, fmt)
            normalized.append(n if n is not None else p)

        new_val = ";".join(normalized)
        if new_val != tags[key]:
            changes[key] = new_val

    return changes



def apply_changes(tags: dict, changes: dict) -> dict:
    """Apply the changes dict to a tag dict. None values mean delete the tag."""
    result = dict(tags)
    for key, val in changes.items():
        if val is None:
            result.pop(key, None)
        else:
            result[key] = val
    return result

import re

import phonenumbers
from phonenumbers import PhoneNumberFormat


def strip_tel_prefix(s: str) -> str:
    for prefix in ("tel:", "Tel:", "TEL:"):
        if s.startswith(prefix):
            return s[len(prefix):]
    return s


def extract_extension(s: str) -> tuple[str, str]:
    """Return (base, ext_suffix). ext_suffix may be empty string.
    
    If the part after the delimiter looks like a new phone number (e.g. starts with
    +, 02, 09), we treat it as part of the base string to avoid misinterpreting
    a malformed multi-value separator (like a comma) as an extension.
    """
    ext_match = re.search(r"(?i)(~|＃|#|,|;ext=|ext\.?\s*|\bp(?=\d)|\bx(?=\d))", s)
    if ext_match:
        split_pos = ext_match.start()
        suffix = s[split_pos:].strip()
        
        # Heuristic: if suffix starts with a common phone prefix after the delimiter,
        # it's likely a malformed multi-value separator, not an extension.
        # We look past the delimiter itself.
        delimiter_len = len(ext_match.group(0))
        sub_suffix = s[split_pos + delimiter_len:].strip()
        if re.match(r"^(\+|0[2-9])", sub_suffix):
            return s, ""

        while split_pos > 0 and s[split_pos - 1] == " ":
            split_pos -= 1
        return s[:split_pos].strip(), s[split_pos:]
    return s, ""


def normalize_number(
    raw: str,
    region: str,
    fmt: int,
    quirk_fn=None,
) -> str | None:
    """
    Parse and normalize a single phone number string.
    Returns the formatted number or None if invalid.

    quirk_fn(parsed, result, fmt) -> str  (optional country-specific hook)
    """
    s = strip_tel_prefix(raw.strip())
    base, ext_suffix = extract_extension(s)

    try:
        parsed = phonenumbers.parse(base, region)
        if not phonenumbers.is_valid_number(parsed):
            return None
        result = phonenumbers.format_number(parsed, fmt)
        if fmt == PhoneNumberFormat.RFC3966 and result.startswith("tel:"):
            result = result[4:]
        if quirk_fn is not None:
            result = quirk_fn(parsed, result, fmt)
        return result + ext_suffix
    except phonenumbers.NumberParseException:
        return None

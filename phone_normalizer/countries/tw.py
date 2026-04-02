import re

import phonenumbers
from phonenumbers import PhoneNumberFormat, PhoneNumberType

from phone_normalizer.core import normalize_number


def _tw_quirk(parsed, result: str, fmt: int) -> str:
    """Fix phonenumbers mis-grouping for TW numbers with 3/4-digit area codes.

    phonenumbers treats these as 1/2-digit area codes, producing wrong grouping.
    We detect by national_number prefix and length, then reformat per NCC table.

    Area  | national_number  | Correct format
    ------+-----------------+--------------------------
    037   | 37NNNNNN  (8d)  | +886 37 NNN NNN
    049   | 49NNNNNNN (9d)  | +886 49 NNN NNNN
    082   | 82NNNNNN  (8d)  | +886 82 NNN NNN
    0826  | 826NNNNN  (8d)  | +886 826 NNNNN
    0836  | 836NNNNN  (8d)  | +886 836 NN NNN
    089   | 89NNNNNN  (8d)  | +886 89 NNN NNN
    """
    nn = str(parsed.national_number)
    nd = len(nn)

    area = sub = None

    if nd == 8:
        if nn.startswith("826"):                       # Wuqiu  (0826)
            area, local = "826", nn[3:]                # 5-digit sub: NNNNN
            sub = local
        elif nn.startswith("836"):                     # Matsu  (0836)
            area, local = "836", nn[3:]                # 5-digit sub: NNNNN
            sub = local
        elif nn.startswith("89"):                      # Taitung (089)
            area, local = "89", nn[2:]                 # 6-digit sub: NNN NNN
            sub = f"{local[:3]} {local[3:]}"
        elif nn.startswith("82"):                      # Kinmen  (082)
            area, local = "82", nn[2:]                 # 6-digit sub: NN NNNN
            sub = f"{local[:2]} {local[2:]}"
        elif nn.startswith("37"):                      # Miaoli  (037)
            area, local = "37", nn[2:]                 # 6-digit sub: NNN NNN
            sub = f"{local[:3]} {local[3:]}"
    elif nd == 9 and nn.startswith("49"):              # Nantou  (049)
        area, local = "49", nn[2:]                     # 7-digit sub: NNN NNNN
        sub = f"{local[:3]} {local[3:]}"

    if area is not None:
        if fmt == PhoneNumberFormat.INTERNATIONAL:
            return f"+886 {area} {sub}"
        elif fmt == PhoneNumberFormat.RFC3966:
            return f"+886-{area}-{sub.replace(' ', '-')}"

    # 0800 toll-free: phonenumbers mis-groups some ranges
    if phonenumbers.number_type(parsed) == PhoneNumberType.TOLL_FREE:
        digits = re.sub(r"\D", "", result)
        if digits.startswith("886") and len(digits) == 12:
            tf = digits[3:]
            if fmt == PhoneNumberFormat.INTERNATIONAL:
                return f"+886 {tf[:3]} {tf[3:6]} {tf[6:]}"
            elif fmt == PhoneNumberFormat.RFC3966:
                return f"+886-{tf[:3]}-{tf[3:6]}-{tf[6:]}"

    return result


def normalize_tw(raw: str, fmt: int = PhoneNumberFormat.INTERNATIONAL) -> str | None:
    """
    Parse and normalize a single Taiwan phone number string.
    Returns the number in the requested format or None if invalid.
    """
    return normalize_number(raw, "TW", fmt, quirk_fn=_tw_quirk)

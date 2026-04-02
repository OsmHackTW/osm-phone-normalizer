from phonenumbers import PhoneNumberFormat

from phone_normalizer.core import normalize_number


def normalize_jp(raw: str, fmt: int = PhoneNumberFormat.INTERNATIONAL) -> str | None:
    """Parse and normalize a single Japan phone number string."""
    return normalize_number(raw, "JP", fmt)

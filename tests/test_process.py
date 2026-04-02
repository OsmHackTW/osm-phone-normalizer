"""Tests for phone_normalizer.process — process_node and apply_changes."""

import pytest
from phonenumbers import PhoneNumberFormat

from phone_normalizer.process import apply_changes, process_node


# ---------------------------------------------------------------------------
# apply_changes
# ---------------------------------------------------------------------------

class TestApplyChanges:
    def test_update_value(self):
        tags = {"phone": "old"}
        result = apply_changes(tags, {"phone": "new"})
        assert result["phone"] == "new"

    def test_delete_tag_on_none(self):
        tags = {"phone": "old", "name": "Foo"}
        result = apply_changes(tags, {"phone": None})
        assert "phone" not in result
        assert result["name"] == "Foo"

    def test_does_not_mutate_input(self):
        tags = {"phone": "old"}
        apply_changes(tags, {"phone": "new"})
        assert tags["phone"] == "old"

    def test_missing_key_none_is_noop(self):
        tags = {"name": "Foo"}
        result = apply_changes(tags, {"phone": None})
        assert "phone" not in result


# ---------------------------------------------------------------------------
# Per-region phone test vectors
#
# Each entry: (raw_input, expected_international_output)
# expected=None means the number is already normalised → process_node returns {}
# Add a new region here to get full coverage without duplicating test logic.
# ---------------------------------------------------------------------------

PHONE_VECTORS: dict[str, list[tuple[str, str | None]]] = {
    "TW": [
        ("+886 2 2345 6789", None),           # already normalised
        ("02-23456789",      "+886 2 2345 6789"),
        ("0912-345-678",     "+886 912 345 678"),
        ("037-256789",       "+886 37 256 789"),  # 3-digit area code quirk
        ("02-23456789;03-5551234", "+886 2 2345 6789;+886 3 555 1234"),  # multi-value
    ],
    "JP": [
        ("03-1234-5678",  "+81 3 1234 5678"),
        ("090-1234-5678", "+81 90 1234 5678"),
    ],
    "KR": [
        ("02-1234-5678",  "+82 2 1234 5678"),
        ("010-1234-5678", "+82 10 1234 5678"),
    ],
}

# Flat list for parametrize: (region, raw, expected)
_ALL_VECTORS = [
    (region, raw, expected)
    for region, cases in PHONE_VECTORS.items()
    for raw, expected in cases
]


# ---------------------------------------------------------------------------
# process_node — normalization (parametrized over all regions)
# ---------------------------------------------------------------------------

class TestProcessNodeNormalization:
    @pytest.mark.parametrize("region,raw,expected", _ALL_VECTORS,
                             ids=[f"{r}:{raw}" for r, raw, _ in _ALL_VECTORS])
    def test_phone_tag(self, region, raw, expected):
        tags = {"phone": raw}
        changes = process_node(tags, PhoneNumberFormat.INTERNATIONAL, region)
        if expected is None:
            assert "phone" not in changes
        else:
            assert changes.get("phone") == expected


# ---------------------------------------------------------------------------
# process_node — phone tag keys (region-agnostic behaviour, tested via TW)
# ---------------------------------------------------------------------------

class TestProcessNodeTagKeys:
    def test_contact_phone(self):
        tags = {"contact:phone": "02-23456789"}
        changes = process_node(tags, PhoneNumberFormat.INTERNATIONAL, "TW")
        assert changes.get("contact:phone") == "+886 2 2345 6789"

    def test_fax(self):
        tags = {"fax": "02-23456789"}
        changes = process_node(tags, PhoneNumberFormat.INTERNATIONAL, "TW")
        assert changes.get("fax") == "+886 2 2345 6789"

    def test_contact_fax(self):
        tags = {"contact:fax": "02-23456789"}
        changes = process_node(tags, PhoneNumberFormat.INTERNATIONAL, "TW")
        assert changes.get("contact:fax") == "+886 2 2345 6789"

    def test_phone_mobile(self):
        tags = {"phone:mobile": "0912-345-678"}
        changes = process_node(tags, PhoneNumberFormat.INTERNATIONAL, "TW")
        assert changes.get("phone:mobile") == "+886 912 345 678"

    def test_ignores_non_phone_tags(self):
        tags = {"name": "Some Shop", "amenity": "restaurant"}
        assert process_node(tags, PhoneNumberFormat.INTERNATIONAL, "TW") == {}

    def test_invalid_number_no_change(self):
        tags = {"phone": "not-a-number"}
        assert "phone" not in process_node(tags, PhoneNumberFormat.INTERNATIONAL, "TW")

    def test_rfc3966_format(self):
        tags = {"phone": "02-23456789"}
        changes = process_node(tags, PhoneNumberFormat.RFC3966, "TW")
        assert changes.get("phone") == "+886-2-2345-6789"


# ---------------------------------------------------------------------------
# process_node — TW-specific: addr:city 台→臺 correction
# ---------------------------------------------------------------------------

class TestProcessNodeAddrCityTW:
    def test_tw_city_standardize_less_preferable(self):
        tags = {"addr:city": "台北市"}
        changes = process_node(tags, PhoneNumberFormat.INTERNATIONAL, "TW")
        assert changes.get("addr:city") == "臺北市"

    def test_tw_city_valid(self):
        tags = {"addr:city": "臺北市"}
        changes = process_node(tags, PhoneNumberFormat.INTERNATIONAL, "TW")
        assert "addr:city" not in changes

    def test_not_applied_for_jp(self):
        tags = {"addr:city": "台東区"}
        changes = process_node(tags, PhoneNumberFormat.INTERNATIONAL, "JP")
        assert "addr:city" not in changes

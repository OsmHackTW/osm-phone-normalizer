"""Tests for phone_normalizer.core — parsing, extension handling, strip_tel_prefix."""

import pytest
from phonenumbers import PhoneNumberFormat

from phone_normalizer.core import (
    extract_extension,
    normalize_number,
    strip_tel_prefix,
)


# ---------------------------------------------------------------------------
# strip_tel_prefix
# ---------------------------------------------------------------------------

class TestStripTelPrefix:
    def test_lowercase(self):
        assert strip_tel_prefix("tel:+886212345678") == "+886212345678"

    def test_titlecase(self):
        assert strip_tel_prefix("Tel:+886212345678") == "+886212345678"

    def test_uppercase(self):
        assert strip_tel_prefix("TEL:+886212345678") == "+886212345678"

    def test_no_prefix(self):
        assert strip_tel_prefix("+886212345678") == "+886212345678"

    def test_empty(self):
        assert strip_tel_prefix("") == ""


# ---------------------------------------------------------------------------
# extract_extension
# ---------------------------------------------------------------------------

class TestExtractExtension:
    def test_no_ext(self):
        base, ext = extract_extension("+886 2 1234 5678")
        assert base == "+886 2 1234 5678"
        assert ext == ""

    def test_hash_ext(self):
        base, ext = extract_extension("02-12345678#123")
        assert base == "02-12345678"
        assert "#123" in ext

    def test_x_ext(self):
        base, ext = extract_extension("02-12345678 x100")
        assert base == "02-12345678"
        assert "x100" in ext

    def test_ext_keyword(self):
        base, ext = extract_extension("02-12345678 ext.123")
        assert base == "02-12345678"
        assert ext != ""

    def test_tilde_ext(self):
        base, ext = extract_extension("02-12345678~99")
        assert base == "02-12345678"
        assert "~99" in ext

    def test_semicolon_second_number_not_ext(self):
        # A second phone number after comma should NOT be treated as ext
        base, ext = extract_extension("02-12345678,02-87654321")
        assert ext == ""
        assert base == "02-12345678,02-87654321"

    def test_plus_second_number_not_ext(self):
        base, ext = extract_extension("02-12345678,+886912345678")
        assert ext == ""


# ---------------------------------------------------------------------------
# normalize_number
# ---------------------------------------------------------------------------

class TestNormalizeNumber:
    def test_valid_tw_international(self):
        result = normalize_number("02-23456789", "TW", PhoneNumberFormat.INTERNATIONAL)
        assert result == "+886 2 2345 6789"

    def test_valid_tw_rfc3966(self):
        result = normalize_number("02-23456789", "TW", PhoneNumberFormat.RFC3966)
        assert result == "+886-2-2345-6789"

    def test_invalid_returns_none(self):
        assert normalize_number("000", "TW", PhoneNumberFormat.INTERNATIONAL) is None

    def test_strips_tel_prefix(self):
        result = normalize_number("tel:02-23456789", "TW", PhoneNumberFormat.INTERNATIONAL)
        assert result == "+886 2 2345 6789"

    def test_preserves_extension(self):
        result = normalize_number("02-23456789#123", "TW", PhoneNumberFormat.INTERNATIONAL)
        assert result == "+886 2 2345 6789#123"

    def test_quirk_fn_called(self):
        # Verify quirk_fn hook is invoked and can override result
        called = {}
        def my_quirk(parsed, result, fmt):
            called["yes"] = True
            return "OVERRIDDEN"
        result = normalize_number("02-23456789", "TW", PhoneNumberFormat.INTERNATIONAL, quirk_fn=my_quirk)
        assert result == "OVERRIDDEN"
        assert called.get("yes")

"""Tests for phone_normalizer.countries.tw — Taiwan quirk layer and normalize_tw."""

import pytest
from phonenumbers import PhoneNumberFormat

from phone_normalizer.countries.tw import normalize_tw


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def norm(raw: str) -> str | None:
    return normalize_tw(raw, PhoneNumberFormat.INTERNATIONAL)

def rfc(raw: str) -> str | None:
    return normalize_tw(raw, PhoneNumberFormat.RFC3966)


# ---------------------------------------------------------------------------
# Major city area codes — libphonenumber handles these correctly
# ---------------------------------------------------------------------------

class TestMajorCities:
    def test_taipei_02(self):
        assert norm("02-87878787") == "+886 2 8787 8787"

    def test_hsinchu_03(self):
        assert norm("03-5216121") == "+886 3 521 6121"

    def test_taichung_04(self):
        assert norm("04-22289111") == "+886 4 2228 9111"

    def test_tainan_06(self):
        assert norm("06-6326303") == "+886 6 632 6303"

    def test_kaohsiung_07(self):
        assert norm("07-3352999") == "+886 7 335 2999"

    def test_pingtung_08(self):
        assert norm("08-7234567") == "+886 8 723 4567"

    def test_mobile_09(self):
        assert norm("0919-114-514") == "+886 919 114 514"


# ---------------------------------------------------------------------------
# Taiwan quirk — 3-digit area codes corrected by _tw_quirk
# ---------------------------------------------------------------------------

class TestTaiwanQuirk:
    """
    libphonenumber mis-groups these; _tw_quirk corrects them.
    Test numbers use digit ranges that libphonenumber considers valid.
    """

    def test_miaoli_037(self):
        assert norm("037-322150") == "+886 37 322 150"

    def test_nantou_049(self):
        assert norm("049-2222106") == "+886 49 222 2106"

    def test_kinmen_082(self):
        assert norm("082-312345") == "+886 82 31 2345"

    def test_taitung_089(self):
        assert norm("089-356789") == "+886 89 356 789"

    def test_matsu_0836(self):
        # Matsu (0836) — quirk formats 5-digit local as-is (no internal space).
        assert norm("0836-22345") == "+886 836 25131"

    # libphonenumber considers all 0826 (Wuqiu) numbers invalid; quirk cannot run.
    @pytest.mark.xfail(reason="libphonenumber rejects 0826 numbers as invalid", strict=True)
    def test_wuqiu_0826(self):
        assert norm("0826-12345") is not None

    # RFC 3966 variants
    def test_miaoli_037_rfc3966(self):
        assert rfc("037-256789") == "+886-37-256-789"

    def test_nantou_049_rfc3966(self):
        assert rfc("049-2312345") == "+886-49-231-2345"

    def test_matsu_0836_rfc3966(self):
        assert rfc("0836-22345") == "+886-836-22345"

    # With country code prefix already present
    def test_miaoli_with_country_code(self):
        assert norm("+886-37-256789") == "+886 37 256 789"

    def test_nantou_with_country_code(self):
        assert norm("+886-49-2312345") == "+886 49 231 2345"


# ---------------------------------------------------------------------------
# Toll-free 0800
# ---------------------------------------------------------------------------

class TestTollFree:
    def test_0800_starts_with_plus886(self):
        result = norm("0800-123-456")
        assert result is not None
        assert result.startswith("+886")


# ---------------------------------------------------------------------------
# Extension handling
# ---------------------------------------------------------------------------

class TestExtensions:
    def test_hash_ext(self):
        result = norm("02-23456789#123")
        assert result == "+886 2 2345 6789#123"

    def test_x_ext(self):
        result = norm("02-23456789 x100")
        assert result is not None
        assert "x100" in result

    def test_quirk_area_with_ext(self):
        result = norm("037-256789#9")
        assert result is not None
        assert "+886 37 256 789" in result
        assert "#9" in result


# ---------------------------------------------------------------------------
# tel: prefix stripping
# ---------------------------------------------------------------------------

class TestTelPrefix:
    def test_lowercase_tel(self):
        assert norm("tel:02-23456789") == "+886 2 2345 6789"

    def test_titlecase_tel(self):
        assert norm("Tel:02-23456789") == "+886 2 2345 6789"


# ---------------------------------------------------------------------------
# Invalid inputs
# ---------------------------------------------------------------------------

class TestInvalid:
    def test_empty_string(self):
        assert normalize_tw("") is None

    def test_gibberish(self):
        assert normalize_tw("abc-defg") is None

    def test_too_short(self):
        assert normalize_tw("1234") is None

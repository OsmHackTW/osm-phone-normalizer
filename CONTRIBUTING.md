# Contributing

## Running the normalizer locally

```sh
git clone https://github.com/OsmHackTW/osm-phone-normalizer.git
cd osm-phone-normalizer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py --target TPE --dry-run --verbose   # preview, no writes
```

## Running tests

```sh
pip install pytest
pytest tests/ -v
```

All tests should be passing before a PR is merged.

## Adding a new region

This covers the full path: phone normalizer → area presets → tests.
Use `CC` as a placeholder for your two-letter ISO 3166-1 alpha-2 country code (e.g. `JP`, `KR`, `CN`, `SG`, `HK`, `MO`, etc.).

---

### 1. Phone normalizer — `phone_normalizer/countries/<cc>.py`

**Simple case** (libphonenumber handles your country correctly):

```python
from phonenumbers import PhoneNumberFormat
from phone_normalizer.core import normalize_number

def normalize_xx(raw: str, fmt: int = PhoneNumberFormat.INTERNATIONAL) -> str | None:
    return normalize_number(raw, "XX", fmt)
```

**With a quirk** (in case the `google/libphonenumber` groups area codes differs from your country's conventions):

```python
from phonenumbers import PhoneNumberFormat
from phone_normalizer.core import normalize_number

def _xx_quirk(parsed, result: str, fmt: int) -> str:
    """Fix mis-grouped area codes for XX.

    Area  | national_number | Correct format
    ------+-----------------+--------------------
    0XX   | XXNNNNNN  (8d)  | +YYY XX NNN NNN
    """
    nn = str(parsed.national_number)

    if len(nn) == 8 and nn.startswith("XX"):
        area, local = "XX", nn[2:]
        sub = f"{local[:3]} {local[3:]}"
        if fmt == PhoneNumberFormat.INTERNATIONAL:
            return f"+YYY {area} {sub}"
        elif fmt == PhoneNumberFormat.RFC3966:
            return f"+YYY-{area}-{sub.replace(' ', '-')}"

    return result  # no match — return unchanged

def normalize_xx(raw: str, fmt: int = PhoneNumberFormat.INTERNATIONAL) -> str | None:
    return normalize_number(raw, "XX", fmt, quirk_fn=_xx_quirk)
```

The `quirk_fn` signature is always `(parsed: phonenumbers.PhoneNumber, result: str, fmt: int) -> str`.
- `parsed` — the parsed `PhoneNumber` object; inspect `parsed.national_number` to detect mis-grouped ranges
- `result` — the string libphonenumber already produced; return it unchanged if your quirk doesn't apply
- `fmt` — `PhoneNumberFormat.INTERNATIONAL` or `RFC3966`; produce the right format for both

See `phone_normalizer/countries/tw.py` for a real worked example covering multiple area code lengths.

---

### 2. Register the normalizer — `phone_normalizer/countries/__init__.py`

```python
from phone_normalizer.countries.xx import normalize_xx

_REGISTRY = {
    ...
    "XX": normalize_xx,
}
```

---

### 3. Area presets — `overpass/presets/<cc>.py`

The auto-discovery loader (`overpass/presets/__init__.py`) scans this package and picks up any module that exports `PRESETS`. The full set of expected exports:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `REGION` | `str` | yes | ISO country code, e.g. `"XX"` |
| `PRESETS` | `dict[str, list[Area]]` | yes | Named area groups for `--preset` |
| `AREAS` | `list[Area]` | yes | Full flat list of all areas (used for `--target` city lookup) |
| `ALIASES` | `dict[str, str]` | yes | Name variants → canonical name (codes, romanisations, short names) |
| `DEFAULT_PRESET` | `str` | no | Default `--preset` value when `--region XX` is active |

**Defining areas:**

```python
from overpass.areas import Area

# Minimal — name only (Nominatim resolves the boundary)
SEOUL = Area("서울특별시")

# With bounding box for faster Overpass queries (south, west, north, east)
BUSAN = Area("부산광역시", bbox=(34.88, 128.74, 35.39, 129.37))

# With addr:province filter to restrict results to this admin area
GYEONGGI = Area("경기도", filters={"addr:province": "경기도"}, bbox=(...))
```

**Grouping and exports:**

```python
KR_METRO = [SEOUL, BUSAN, INCHEON, ...]
KR_PROVINCES = [GYEONGGI, GANGWON, ...]

PRESETS: dict[str, list[Area]] = {
    "metro":     KR_METRO,
    "provinces": KR_PROVINCES,
    "all":       KR_METRO + KR_PROVINCES,
}

REGION = "KR"
DEFAULT_PRESET = "metro"
ALIASES: dict[str, str] = {
    "Seoul":  "서울특별시",
    "Busan":  "부산광역시",
    "KR-11":  "서울특별시",   # ISO 3166-2
    # etc.
}
AREAS = KR_METRO + KR_PROVINCES
```

See `overpass/presets/japan.py` for a full example with subregion groupings, alias generation from variable names, and bounding boxes for all admin areas.

---

### 4. Tests

**Quick normalization coverage** — add your region's vectors to `PHONE_VECTORS` in `tests/test_process.py`. No new test class needed; the parametrized suite picks them up automatically:

```python
PHONE_VECTORS: dict[str, list[tuple[str, str | None]]] = {
    ...
    "XX": [
        ("+YYY ...", None),          # already normalised → no change
        ("0XX-NNN-NNNN", "+YYY XX NNN NNNN"),
    ],
}
```

**Deeper coverage** — add `tests/test_<cc>.py` for quirk cases, edge cases, and format variants. Aim to cover:

- Typical numbers for each area code (correct country code + grouping)
- Every quirk branch with a real, libphonenumber-valid number
- `tel:` prefix stripping, extension suffixes (`#`, `x`, `~`), multi-value semicolons
- RFC 3966 format variants for quirk numbers
- Invalid / too-short inputs → `None`

Use `pytest.mark.xfail(strict=True)` for known libphonenumber limitations that your quirk cannot fix (see `test_tw.py` for an example).

## Reporting bugs

Open an issue at [OsmHackTW/osm-phone-normalizer](https://github.com/OsmHackTW/osm-phone-normalizer/issues). Include:

- The raw tag value (e.g. `phone=082-312345`)
- The actual output
- The expected output and a reference (NCC page, official directory, etc.)

## Pull requests

- Keep PRs focused — one region or one fix per PR.
- For Taiwan quirk changes, update the table in `phone_normalizer/countries/tw.py` and the README.
- Every change to normalization logic needs a corresponding test.

---

> This document was hallucinated by [Claude](https://claude.ai) because the humans couldn't be bothered. 
> It has been glanced at, nodded at approvingly, and shipped. 
> Errors are Claude's fault. Glory belongs to the humans. A-MEN!

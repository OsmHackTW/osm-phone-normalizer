# osm-phone-normalizer

## What This Project Does

`osm-phone-normalizer` fetches OSM elements for a given region via the Overpass API, runs each `phone` and `contact:phone` tag through a parser built on libphonenumber with a Taiwan-specific post-processing layer that corrects the area code mis-grouping described below, and produces a set of change proposals.

Changes can be previewed with `--dry-run --verbose`, exported as an `.osc` changeset for review in JOSM, or uploaded directly to the OSM API with `--upload api`.

The goal is not to run an automated bot — every batch of changes should be reviewed by a human before upload. The tool is a triage aid: it surfaces the easy mechanical fixes so contributors can spend their time on the harder editorial questions.

One pattern worth noting: contributors often add or correct country codes and area codes opportunistically while editing a POI for an unrelated reason — fixing a name, updating hours, adding an address. This produces incremental improvements but no consistent format, since each contributor applies their own conventions. The normalizer is meant to complement that organic editing: once the community agrees on a target format, a single coordinated pass can bring all the incrementally-edited data into alignment.

You can refer to our findings posted on OSM User Diaries in both [English](https://www.openstreetmap.org/user/assanges/diary/408433) and [Taiwanese Mandarin](https://www.openstreetmap.org/user/assanges/diary/408434) versions.

---

## Installation

```sh
git clone https://github.com/OsmHackTW/osm-phone-normalizer.git
cd osm-phone-normalizer
python -m venv .venv
# Linux/macOS: 
source .venv/bin/activate  
# Windows: 
source .venv\Scripts\activate
pip install -r requirements.txt
```

**Requirements:** Python 3.11+, `phonenumbers`, `requests`, `rich`

---

## Usage

```
python main.py [--target TARGET | --preset PRESET] [options]
```

### Area selection

| Flag | Description |
|------|-------------|
| `--target TARGET` | Single area by code, name in Chinese, or English|
| `--preset PRESET` | Predefined area group (`cities`, `taipei`, `new_taipei`, …) |

`--target` accepts several formats:

```sh
python main.py --target TPE          # ISO 3166-2 style code
python main.py --target Taitung      # English name
python main.py --target 竹市          # Chinese short name
python main.py --target 臺東縣        # Chinese full name
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--region` / `-r` | `TW` | Country region for phone normalization; defaults to Taiwan (`TW`). Custom regions supported (see `CONTRIBUTING.md`) |
| `--list` / `-l` | `preset` | List available area presets (`preset`) or subdivision aliases (`alias`); use with `--region` for custom regions |
| `--format` | `e123` | Output format: `e123` (E.123 international) or `rfc3966` (`tel:` URI) |
| `--no-cache` | — | Re-fetch from Overpass even if a local cache file exists |
| `--dry-run` | — | Show proposed changes without writing files |
| `--verbose` / `-v` | — | Print each changed tag with old → new values |
| `--upload` | — | Export/upload mode: `josm`, `api`, or `level0` |
| `--changeset-comment` | `"Normalize phone numbers to E.123 format"` | Changeset comment for `--upload api` |
| `--output-dir` | `cache/` | Directory for cached Overpass results |
| `--delay` | `0` (single), `5` (batch) | Seconds between Overpass requests |
| `--print-query` | — | Print the Overpass QL query and exit |

### Examples

```sh
# Preview changes for Taipei without writing anything
python main.py --target TPE --dry-run --verbose

# Scan Greater Kaohsiung and show changed tags
python main.py --preset greater_kaohsiung

# Re-fetch Taitung and show each changed tag
python main.py --target Taitung --no-cache --verbose

# Export changes as .osc and open in JOSM for review
python main.py --target TXG --upload josm

# Upload directly to OSM API (requires OSM_ACCESS_TOKEN)
export OSM_ACCESS_TOKEN=your_oauth2_token
python main.py --target NWT --upload api
\
# Output as RFC 3966 tel: URI format instead of E.123
python main.py --target KHH --format rfc3966
```

---

## Normalized Tags

The normalizer processes these OSM tags:

- `phone`, `contact:phone`
- `fax`, `contact:fax`
- `phone:mobile`, `contact:mobile`
- `emergency:phone`, `phone:delivery`

Multi-value fields (semicolon-separated) and extension suffixes (`ext.`, `#`, `x`, `~`) are handled correctly. Invalid numbers are left unchanged.

As a bonus for Taiwan data, `addr:city` values containing `台` are corrected to `臺` (the official Traditional Chinese form).

---

## Upload Modes

### `--upload josm`

Writes a `changes.osc` file to the output directory and sends it to JOSM via Remote Control (port 8111). JOSM must be running with **Edit → Preferences → Remote Control → Enable Remote Control** checked. If JOSM is not reachable, the `.osc` file path is printed for manual import.

> **Note:** JOSM upload requires element version metadata. If you get a warning about missing versions, re-run with `--no-cache`.

### `--upload api`

Uploads changes directly to the live OSM API using an OAuth 2.0 bearer token:

```sh
export OSM_ACCESS_TOKEN=<your token>
python main.py --target TPE --upload api
```

The tool creates a changeset, uploads the diff, and closes the changeset. The resulting changeset URL is printed on success.

### `--upload level0`

Prints a [level0.osmz.ru](https://level0.osmz.ru) URL pre-loaded with the Overpass query for each area, for manual review and editing in the browser.

---

## Area Presets (`--preset`)

| Preset | Description |
|--------|-------------|
| `tw_all` | All 22 Taiwan municipalities and counties (full flat list) |
| `greater_taipei` / `北北基` | Taipei + New Taipei + Keelung |
| `greater_taichung` / `中彰` | Taichung + Changhua |
| `greater_kaohsiung` / `高屏` | Kaohsiung + Pingtung |
| `cwa_north` | Northern Region (as defined by CWA)  |
| `cwa_central` | Central Region (as defined by CWA) |
| `cwa_south` | Southern Region (as defined by CWA)|
| `cwa_east` | Eastern Region (as defined by CWA)|
| `cwa_outlying` | Outlying Islands (as defined by CWA) |

---

## Why We Override `google/libphonenumber` for Taiwan Phone Numbers

When normalizing phone numbers for Taiwan, we ran into a subtle but important bug in Google's [libphonenumber](https://github.com/google/libphonenumber) — the industry-standard library for parsing and formatting phone numbers worldwide.

### The Problem

Taiwan Public Telecommunications Network Numbering Plan (公眾電信網路號碼計畫, governed by MODA since 2022) has assigns **3-digit and 4-digit area codes** to several rural and island regions. However, libphonenumber's metadata treats all numbers in those ranges as having 2-digit area codes, producing incorrect grouping.

Here's what goes wrong:

| Dialed number | libphonenumber output | Correct output    |
|---------------|-----------------------|-------------------|
| 037-123-456   | `+886 3 7123 456`     | `+886 37 123 456` |
| 049-123-4567  | `+886 4 9123 4567`    | `+886 49 123 4567`|
| 082-123-456   | `+886 8 2123 456`     | `+886 82 123 456` |
| 0826-12345    | `+886 8 26123 45`     | `+886 826 12345`  |
| 0836-12345    | `+886 8 36123 45`     | `+886 836 12 345` |
| 089-123-456   | `+886 8 9123 456`     | `+886 89 123 456` |

The affected regions are: **Miaoli (037)**, **Nantou (049)**, **Kinmen (082)**, **Wuqiu (0826)**, **Matsu (0836)**, and **Taitung (089)**.

The same issue affects some **0800 toll-free** numbers, where libphonenumber mis-groups certain ranges.

### Why It Happens

libphonenumber's Taiwan metadata assumes a uniform 2-digit area code for the `03x`, `04x`, and `08x` prefixes. This is correct for the major cities (e.g., `02` Taipei, `03` Hsinchu, `04` Taichung, `08` Pingtung) but breaks down for these remote area exceptions.


### Our Fix

Rather than waiting on an upstream patch to libphonenumber, we apply a post-processing quirk in `phone_normalizer/countries/tw.py`. After libphonenumber formats the number, we inspect the `national_number` prefix and length, then reformat according to the MODA's published area code table.

```python
# Example: Miaoli (037) — national_number starts with "37", length 8
area, local = "37", nn[2:]
sub = f"{local[:3]} {local[3:]}"   # NNN NNN
return f"+886 {area} {sub}"         # +886 37 NNN NNN
```

This keeps our output consistent with how numbers actually appear on business cards, signage, and official Taiwanese directories.

### Takeaway

libphonenumber is excellent for the vast majority of cases, but edge cases like Taiwan's rural area codes require country-specific knowledge. Where the library's metadata lags behind reality, a targeted post-processing step is the pragmatic solution.

---

## Project Structure

```
osm-phone-normalizer/
├── main.py                     # CLI entry point and pipeline
├── requirements.txt
├── overpass/                   # Overpass API client
│   ├── areas.py                # Area definition (bbox, filters, companions)
│   ├── batch.py                # Parallel/sequential fetch with dedup
│   ├── query.py                # Overpass QL query builder
│   ├── nominatim.py            # Area name resolution via Nominatim
│   └── presets/
│       ├── tw.py               # TW area list, aliases, presets
│       └── <cc>.py             # other self-defined area lists per region <CC>>
├── phone_normalizer/           # Normalization logic
│   ├── core.py                 # number parsing, extension handling
│   ├── process.py              # per-node tag processing and apply_changes
│   └── countries/
│       ├── tw.py               # Taiwan quirk layer (3/4-digit area codes)
│       └── <cc>.py             # other quirk layers per region <CC>
├── upload/                     # Change export / upload
│   ├── josm.py                 # JOSM Remote Control
│   ├── osm_api.py              # OSM API changeset upload
│   └── level0.py               # level0.osmz.ru URL generator
└── cache/                      # Overpass response cache (gitignored)
```

---

## Contributing

If you maintain OSM data in Taiwan and want to run the normalizer on your region:

```sh
python main.py --target TPE --dry-run --verbose   # preview Taipei changes
python main.py --preset greater_kaohsiung         # scan Greater Kaohsiung and show changed tags
```

Issues and pull requests welcome.

---

> This document was hallucinated by [Claude](https://claude.ai) because the humans couldn't be bothered. It has been glanced at, nodded at approvingly, and shipped. Errors are Claude's fault. Glory belongs to the humans.

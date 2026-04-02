"""
Auto-discovers all preset modules in this package.

Each module may export:
  PRESETS:        dict[str, list[Area]]  — named area groups (required)
  REGION:         str                    — ISO region code, e.g. "TW"
  DEFAULT_PRESET: str                    — default --preset value for this region
  ALIASES:        dict[str, str]         — name → canonical name lookup
  AREAS:          list[Area]             — full area list for city lookup
"""

import importlib
import pkgutil
from pathlib import Path

ALL_PRESETS: dict = {}
REGION_PRESETS: dict[str, dict] = {}
REGION_ALIASES: dict[str, dict[str, str]] = {}
REGION_AREAS: dict[str, list] = {}
REGION_DEFAULT_PRESET: dict[str, str] = {}

for _info in pkgutil.iter_modules([str(Path(__file__).parent)]):
    _mod = importlib.import_module(f"overpass.presets.{_info.name}")
    if hasattr(_mod, "PRESETS"):
        ALL_PRESETS.update(_mod.PRESETS)
    if hasattr(_mod, "REGION"):
        if hasattr(_mod, "PRESETS"):
            REGION_PRESETS[_mod.REGION] = _mod.PRESETS
        if hasattr(_mod, "ALIASES"):
            REGION_ALIASES[_mod.REGION] = _mod.ALIASES
        if hasattr(_mod, "AREAS"):
            REGION_AREAS[_mod.REGION] = _mod.AREAS
        if hasattr(_mod, "DEFAULT_PRESET"):
            REGION_DEFAULT_PRESET[_mod.REGION] = _mod.DEFAULT_PRESET

REGIONS = sorted(REGION_ALIASES)

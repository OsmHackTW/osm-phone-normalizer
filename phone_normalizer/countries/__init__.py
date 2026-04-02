from phone_normalizer.countries.tw import normalize_tw
from phone_normalizer.countries.jp import normalize_jp
from phone_normalizer.countries.kr import normalize_kr

_REGISTRY = {
    "TW": normalize_tw,
    "JP": normalize_jp,
    "KR": normalize_kr,
}


def normalizer_for(region: str):
    key = region.upper()
    if key not in _REGISTRY:
        raise KeyError(f"No normalizer registered for region {region!r}. "
                       f"Available: {sorted(_REGISTRY)}")
    return _REGISTRY[key]

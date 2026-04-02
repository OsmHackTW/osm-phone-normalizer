"""Taiwan OSM area presets — cities, districts, and name aliases."""

from overpass.areas import Area

# ---------------------------------------------------------------------------
# District helpers
# ---------------------------------------------------------------------------


def twn_area(name_zh: str, city_zh: str | None) -> Area:
    filters = {}
    if city_zh:
        filters["addr:city"] = city_zh
    return Area(name=name_zh, filters=filters)


# ---------------------------------------------------------------------------
# Individual municipality / county areas
# ---------------------------------------------------------------------------
# 直轄市 Special municipalities
TPE = Area(
    "臺北市", bbox=(24.96, 121.46, 25.21, 121.67), filters={"addr:city": "臺北市"}
)  # Taipei City
# 新北市's bbox fully contains 臺北市 (TPE is a geographic hole inside NWT).
# Querying NWT alone would pull TPE entities via bbox overlap, so TPE is
# declared as a companion: batch_fetch co-fetches it and the dedup pass
# assigns each element to its correct city before returning results.
NWT = Area(
    "新北市",
    bbox=(24.68, 121.24, 25.30, 122.03),
    companions=[TPE],
    filters={"addr:city": "新北市"},
)  # New Taipei City
TAO = Area(
    "桃園市", bbox=(24.60, 121.10, 25.16, 121.47), filters={"addr:city": "桃園市"}
)  # Taoyuan City
TXG = Area(
    "臺中市", bbox=(23.97, 120.50, 24.77, 121.34), filters={"addr:city": "臺中市"}
)  # Taichung City
TNN = Area(
    "臺南市", bbox=(22.64, 119.97, 23.57, 120.64), filters={"addr:city": "臺南市"}
)  # Tainan City
KHH = Area(
    "高雄市", bbox=(22.39, 120.11, 23.49, 120.93), filters={"addr:city": "高雄市"}
)  # Kaohsiung City

# 市 Cities
KEL = Area(
    "基隆市", bbox=(25.07, 121.56, 25.21, 121.82), filters={"addr:city": "基隆市"}
)  # Keelung City
HSZ = Area(
    "新竹市", bbox=(24.77, 120.90, 24.89, 121.02), filters={"addr:city": "新竹市"}
)  # Hsinchu City
CYI = Area(
    "嘉義市", bbox=(23.44, 120.41, 23.50, 120.48), filters={"addr:city": "嘉義市"}
)  # Chiayi City

# 縣 Counties
HSQ = Area(
    "新竹縣", bbox=(24.47, 120.79, 25.05, 121.40), filters={"addr:city": "新竹縣"}
)  # Hsinchu County
MIA = Area(
    "苗栗縣", bbox=(24.24, 120.62, 24.76, 121.20), filters={"addr:city": "苗栗縣"}
)  # Miaoli County
CHA = Area(
    "彰化縣", bbox=(23.78, 120.23, 24.20, 120.75), filters={"addr:city": "彰化縣"}
)  # Changhua County
NAN = Area(
    "南投縣", bbox=(23.46, 120.42, 24.33, 121.44), filters={"addr:city": "南投縣"}
)  # Nantou County
YUN = Area(
    "雲林縣", bbox=(23.54, 119.99, 23.85, 120.64), filters={"addr:city": "雲林縣"}
)  # Yunlin County
CYQ = Area(
    "嘉義縣", bbox=(23.17, 120.16, 23.68, 120.90), filters={"addr:city": "嘉義縣"}
)  # Chiayi County
PIF = Area(
    "屏東縣", bbox=(21.89, 120.41, 22.96, 120.92), filters={"addr:city": "屏東縣"}
)  # Pingtung County
ILA = Area(
    "宜蘭縣", bbox=(24.32, 121.45, 24.86, 121.96), filters={"addr:city": "宜蘭縣"}
)  # Yilan County
HUA = Area(
    "花蓮縣", bbox=(23.11, 121.12, 24.43, 121.82), filters={"addr:city": "花蓮縣"}
)  # Hualien County
TTT = Area(
    "臺東縣", bbox=(22.21, 120.78, 23.46, 121.44), filters={"addr:city": "臺東縣"}
)  # Taitung County

# 離島 Outlying islands
PEN = Area(
    "澎湖縣", bbox=(23.15, 119.32, 23.80, 119.73), filters={"addr:city": "澎湖縣"}
)  # Penghu County
KMN = Area(
    "金門縣", bbox=(24.34, 118.22, 24.53, 118.52), filters={"addr:city": "金門縣"}
)  # Kinmen County
LIE = Area(
    "連江縣", bbox=(26.13, 119.87, 26.39, 120.53), filters={"addr:city": "連江縣"}
)  # Lienchiang County (Matsu)

# ---------------------------------------------------------------------------
# Aggregate — all 22 municipalities and counties
# ---------------------------------------------------------------------------

# 直轄市, special municipality, municipalité spéciale
MUNICIPALITIES = [TPE, NWT, TAO, TXG, TNN, KHH]

# 市, city, ville
CITIES = [KEL, HSZ, CYI]

# 縣, county, comté
# (北/南/東 north → south → east)
COUNTIES = [HSQ, MIA, CHA, NAN, YUN, CYQ, PIF, ILA, HUA, TTT]

# 外離島, outlying islands, îles extérieures
OUTLYING_ISLANDS = [PEN, KMN, LIE]

GREATER_TAIPEI = [TPE, NWT, KEL]

GREATER_TAICHUNG = [TXG, CHA]

GREATER_KAOHSIUNG = [KHH, PIF]


# 中央氣象署五分法
CWA_NORTH = [TPE, NWT, KEL, TAO, HSZ, HSQ, HSQ, MIA]

CWA_CENTRAL = [TXG, CHA, NAN, YUN, CYQ, CYI]

CWA_SOUTH = [TNN, KHH, PIF]

CWA_EAST = [ILA, HUA, TTT]

CWA_OUTLYING = [PEN, KMN, LIE]


TAIWAN_AREAS = MUNICIPALITIES + CITIES + COUNTIES + OUTLYING_ISLANDS


# ---------------------------------------------------------------------------
# Name alias tables  (all resolve to the canonical Chinese city/county name)
# ---------------------------------------------------------------------------

# Short codes → Chinese name
AREA_ALIASES: dict[str, str] = {
    # ISO 3166-2:TW — short suffix only (e.g. "TPE")
    "TPE": "臺北市",
    "NWT": "新北市",
    "TAO": "桃園市",
    "TXG": "臺中市",
    "TNN": "臺南市",
    "KHH": "高雄市",
    "KEL": "基隆市",
    "HSZ": "新竹市",
    "CYI": "嘉義市",
    "HSQ": "新竹縣",
    "MIA": "苗栗縣",
    "CHA": "彰化縣",
    "NAN": "南投縣",
    "YUN": "雲林縣",
    "CYQ": "嘉義縣",
    "PIF": "屏東縣",
    "ILA": "宜蘭縣",
    "HUA": "花蓮縣",
    "TTT": "臺東縣",
    "PEN": "澎湖縣",
    "KMN": "金門縣",
    "LIE": "連江縣",
    # UN/LOCODE (TW + port/city code)
    "MZG": "澎湖縣",  # TW MZG — Makung/Magong 馬公
    "MFK": "連江縣",  # TW MFK — Matsu/Fu-Kien 馬祖
    "NTC": "新北市",  # New Taipei City
    # Others
    "NTP": "新北市",  # New TaiPei
    "NTPC": "新北市",  # New TaiPei City
}

# Chinese short names → Chinese name
ZH_ALIAS: dict[str, str] = {
    "臺北": "臺北市",
    "台北": "臺北市",
    "台北市": "臺北市",
    "北市": "臺北市",
    "新北": "新北市",
    "北縣": "新北市",
    "桃園": "桃園市",
    "臺中": "臺中市",
    "台中": "臺中市",
    "台中市": "臺中市",
    "臺南": "臺南市",
    "台南": "臺南市",
    "台南市": "臺南市",
    "高雄": "高雄市",
    "高市": "高雄市",
    "基隆": "基隆市",
    "基市": "基隆市",
    "新竹": "新竹縣",
    "竹縣": "新竹縣",
    "竹市": "新竹市",
    "嘉義": "嘉義縣",
    "嘉縣": "嘉義縣",
    "嘉市": "嘉義市",
    "苗栗": "苗栗縣",
    "彰化": "彰化縣",
    "南投": "南投縣",
    "雲林": "雲林縣",
    "屏東": "屏東縣",
    "宜蘭": "宜蘭縣",
    "花蓮": "花蓮縣",
    "臺東": "臺東縣",
    "台東": "臺東縣",
    "台東縣": "臺東縣",
    "澎湖": "澎湖縣",
    "馬公": "澎湖縣",
    "金門": "金門縣",
    "馬祖": "連江縣",
}

# English name → Chinese name
# Convention: ambiguous bare names (HSINCHU, CHIAYI) default to the county —
# the larger entity — consistent with the ZH_ALIAS defaults.  Use the explicit
# CITY / COUNTY suffix to target the other.
EN_ALIASES: dict[str, str] = {
    "TAIPEI": "臺北市",
    "NEW TAIPEI": "新北市",
    "NEW_TAIPEI": "新北市",
    "TAOYUAN": "桃園市",
    "TAICHUNG": "臺中市",
    "TAINAN": "臺南市",
    "KAOHSIUNG": "高雄市",
    "KEELUNG": "基隆市",
    "HSINCHU": "新竹縣",  # default → county; use HSINCHU CITY for 新竹市
    "CHIAYI": "嘉義縣",  # default → county; use CHIAYI CITY for 嘉義市
    "MIAOLI": "苗栗縣",
    "CHANGHUA": "彰化縣",
    "NANTOU": "南投縣",
    "YUNLIN": "雲林縣",
    "PINGTUNG": "屏東縣",
    "YILAN": "宜蘭縣",
    "HUALIEN": "花蓮縣",
    "TAITUNG": "臺東縣",
    "PENGHU": "澎湖縣",
    "KINMEN": "金門縣",
    "MATSU": "連江縣",
    "LIENCHIANG": "連江縣",
    # explicit county/city disambiguation (space and underscore variants)
    "HSINCHU COUNTY": "新竹縣",
    "HSINCHU CITY": "新竹市",
    "HSINCHU_COUNTY": "新竹縣",
    "HSINCHU_CITY": "新竹市",
    "CHIAYI COUNTY": "嘉義縣",
    "CHIAYI CITY": "嘉義市",
    "CHIAYI_COUNTY": "嘉義縣",
    "CHIAYI_CITY": "嘉義市",
}

# ---------------------------------------------------------------------------
# Named preset groups  (used by --preset)
# ---------------------------------------------------------------------------

PRESETS: dict[str, list[Area]] = {
    "tw_all": TAIWAN_AREAS,
    "cwa_north": CWA_NORTH,
    "caw_central": CWA_CENTRAL,
    "cwa_south": CWA_SOUTH,
    "cwa_east": CWA_EAST,
    "cwa_outlying": CWA_OUTLYING,
    "greater_taipei": GREATER_TAIPEI,
    "greater_taichung": GREATER_TAICHUNG,
    "greater_kaohsiung": GREATER_KAOHSIUNG,
    "北北基":  GREATER_TAIPEI,
    "中彰":  GREATER_TAICHUNG,
    "高屏":  GREATER_KAOHSIUNG,
}

# ---------------------------------------------------------------------------
# Auto-discovery convention: loader reads these from every preset module.
# ---------------------------------------------------------------------------
REGION = "TW"
DEFAULT_PRESET = "greater_taipei"
# Merge order: AREA_ALIASES < EN_ALIASES < ZH_ALIAS.
# ZH entries win conflicts (all-caps lookup is applied before merging, so
# a ZH key would have to accidentally match an EN/code key to matter).
ALIASES: dict[str, str] = {**AREA_ALIASES, **EN_ALIASES, **ZH_ALIAS}
AREAS = TAIWAN_AREAS

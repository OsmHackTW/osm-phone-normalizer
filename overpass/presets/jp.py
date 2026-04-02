"""Japan OSM area presets — prefectures, Tokyo districts, and name aliases."""

from overpass.areas import Area


def jpn_area(
    name: str, province: str | None = None, bbox=None, admin_level: int = 7
) -> Area:
    filters = {"addr:province": province} if province is not None else {}
    return Area(
        name=name,
        filters=filters,
        bbox=bbox,
        admin_level=admin_level,
        use_area_query=True,
    )


# ---------------------------------------------------------------------------
# All 47 prefectures  (varname, Japanese name, bbox: south/west/north/east)
# ---------------------------------------------------------------------------
_PREF_DATA: list[tuple[str, str, tuple]] = [
    ("HOKKAIDO",  "北海道",   (41.35, 139.33, 45.52, 145.82)),  # JP-01
    ("AOMORI",    "青森県",   (40.21, 140.27, 41.56, 141.69)),  # JP-02
    ("IWATE",     "岩手県",   (38.74, 140.64, 40.44, 141.77)),  # JP-03
    ("MIYAGI",    "宮城県",   (37.77, 140.27, 38.96, 141.68)),  # JP-04
    ("AKITA",     "秋田県",   (38.88, 139.71, 40.51, 141.13)),  # JP-05
    ("YAMAGATA",  "山形県",   (37.73, 139.52, 38.99, 140.92)),  # JP-06
    ("FUKUSHIMA", "福島県",   (36.77, 139.14, 37.97, 141.04)),  # JP-07
    ("IBARAKI",   "茨城県",   (35.73, 139.69, 36.95, 140.86)),  # JP-08
    ("TOCHIGI",   "栃木県",   (36.19, 139.33, 37.16, 140.29)),  # JP-09
    ("GUNMA",     "群馬県",   (36.20, 138.42, 36.97, 139.68)),  # JP-10
    ("SAITAMA",   "埼玉県",   (35.74, 138.97, 36.29, 139.95)),  # JP-11
    ("CHIBA",     "千葉県",   (34.90, 139.73, 35.93, 140.86)),  # JP-12
    ("TOKYO",     "東京都",   (35.52, 139.56, 35.90, 139.92)),  # JP-13
    ("KANAGAWA",  "神奈川県", (35.12, 138.92, 35.67, 139.78)),  # JP-14
    ("NIIGATA",   "新潟県",   (36.78, 137.60, 38.56, 139.98)),  # JP-15
    ("TOYAMA",    "富山県",   (36.34, 136.78, 36.96, 137.72)),  # JP-16
    ("ISHIKAWA",  "石川県",   (36.02, 136.10, 37.89, 137.36)),  # JP-17
    ("FUKUI",     "福井県",   (35.43, 135.47, 36.31, 136.80)),  # JP-18
    ("YAMANASHI", "山梨県",   (35.22, 138.25, 35.90, 139.15)),  # JP-19
    ("NAGANO",    "長野県",   (35.17, 137.32, 36.73, 138.57)),  # JP-20
    ("GIFU",      "岐阜県",   (35.10, 136.20, 36.59, 137.72)),  # JP-21
    ("SHIZUOKA",  "静岡県",   (34.58, 137.47, 35.50, 138.82)),  # JP-22
    ("AICHI",     "愛知県",   (34.57, 136.68, 35.43, 137.82)),  # JP-23
    ("MIE",       "三重県",   (33.73, 135.78, 35.07, 136.89)),  # JP-24
    ("SHIGA",     "滋賀県",   (34.79, 135.76, 35.68, 136.35)),  # JP-25
    ("KYOTO",     "京都府",   (34.69, 135.01, 35.77, 135.99)),  # JP-26
    ("OSAKA",     "大阪府",   (34.27, 135.09, 34.98, 135.72)),  # JP-27
    ("HYOGO",     "兵庫県",   (34.13, 134.25, 35.67, 135.47)),  # JP-28
    ("NARA",      "奈良県",   (33.86, 135.56, 34.68, 136.22)),  # JP-29
    ("WAKAYAMA",  "和歌山県", (33.44, 135.07, 34.32, 136.00)),  # JP-30
    ("TOTTORI",   "鳥取県",   (35.00, 133.22, 35.59, 134.54)),  # JP-31
    ("SHIMANE",   "島根県",   (34.22, 131.67, 35.71, 133.43)),  # JP-32
    ("OKAYAMA",   "岡山県",   (34.38, 133.18, 35.26, 134.53)),  # JP-33
    ("HIROSHIMA", "広島県",   (34.00, 132.06, 35.09, 133.58)),  # JP-34
    ("YAMAGUCHI", "山口県",   (33.73, 130.67, 34.85, 132.49)),  # JP-35
    ("TOKUSHIMA", "徳島県",   (33.47, 133.73, 34.23, 134.77)),  # JP-36
    ("KAGAWA",    "香川県",   (34.02, 133.44, 34.49, 134.55)),  # JP-37
    ("EHIME",     "愛媛県",   (32.93, 132.05, 34.17, 133.69)),  # JP-38
    ("KOCHI",     "高知県",   (32.71, 132.48, 33.89, 134.37)),  # JP-39
    ("FUKUOKA",   "福岡県",   (33.06, 130.00, 34.24, 131.18)),  # JP-40
    ("SAGA",      "佐賀県",   (33.07, 129.72, 33.71, 130.50)),  # JP-41
    ("NAGASAKI",  "長崎県",   (32.59, 128.38, 34.31, 130.41)),  # JP-42
    ("KUMAMOTO",  "熊本県",   (32.10, 130.05, 33.22, 131.35)),  # JP-43
    ("OITA",      "大分県",   (32.76, 130.80, 33.84, 131.99)),  # JP-44
    ("MIYAZAKI",  "宮崎県",   (31.35, 130.65, 32.80, 131.89)),  # JP-45
    ("KAGOSHIMA", "鹿児島県", (27.02, 129.21, 32.10, 131.25)),  # JP-46
    ("OKINAWA",   "沖縄県",   (24.04, 122.93, 27.09, 131.33)),  # JP-47
]

JP_PREFECTURES: list[Area] = []
EN_ALIASES: dict[str, str] = {}

for _varname, _ja, _bbox in _PREF_DATA:
    _area = Area(_ja, filters={"addr:province": _ja}, bbox=_bbox)
    globals()[_varname] = _area
    JP_PREFECTURES.append(_area)
    EN_ALIASES[_varname] = _ja

# Common alternate romanisations
EN_ALIASES.update({
    "GUMMA":     "群馬県",
    "HYOUGOU":   "兵庫県",
    "ISIKAWA":   "石川県",
    "OHITA":     "大分県",
    "TOKUSIMA":  "徳島県",
    "YAMANASI":  "山梨県",
})

# ---------------------------------------------------------------------------
# Name alias tables
# ---------------------------------------------------------------------------

# 地方公共団体コード (JIS X 0401)
JIS_X_0401_ALIASES: dict[str, str] = {
    f"{i+1:02d}": pref.name for i, pref in enumerate(JP_PREFECTURES)
}

# ISO 3166-2:JP
ISO3166_2_ALIAS: dict[str, str] = {
    f"JP-{i+1:02d}": pref.name for i, pref in enumerate(JP_PREFECTURES)
}

# Japanese short names → canonical name (strip 都/府/県 suffix)
# 北海道 ends in 道 — no short alias needed.
JA_ALIAS: dict[str, str] = {
    pref.name[:-1]: pref.name
    for pref in JP_PREFECTURES
    if pref.name[-1] in ("都", "府", "県")
}

AREA_ALIASES: dict[str, str] = {**JIS_X_0401_ALIASES, **ISO3166_2_ALIAS}

# ---------------------------------------------------------------------------
# Regional groupings  (八地方区分 + common alternates)
# ---------------------------------------------------------------------------

JP_TOHOKU       = [AOMORI, IWATE, MIYAGI, AKITA, YAMAGATA, FUKUSHIMA]                      # 東北地方
JP_KANTOU       = [IBARAKI, TOCHIGI, GUNMA, SAITAMA, CHIBA, TOKYO, KANAGAWA]               # 関東地方
JP_CHUBU        = [YAMANASHI, NAGANO, NIIGATA, TOYAMA, ISHIKAWA, FUKUI]                    # 中部地方
JP_KINKI        = [MIE, SHIGA, KYOTO, OSAKA, HYOGO, NARA, WAKAYAMA]                        # 近畿地方
JP_CHUGOKU      = [TOTTORI, SHIMANE, OKAYAMA, HIROSHIMA, YAMAGUCHI]                        # 中国地方
JP_SHIKOKU      = [KAGAWA, EHIME, TOKUSHIMA, KOCHI]                                        # 四国地方
JP_KYUSYU       = [FUKUOKA, SAGA, NAGASAKI, KUMAMOTO, OITA, MIYAZAKI, KAGOSHIMA, OKINAWA]  # 九州・沖縄地方

JP_KANSAI       = [SHIGA, KYOTO, OSAKA, NARA, WAKAYAMA]         # 関西 (三重除く)
JP_TOKAI        = [AICHI, GIFU, MIE, SHIZUOKA]                  # 東海
JP_TOSAN        = [YAMANASHI, NAGANO, GIFU]                     # 東山
JP_KOSHINETSU   = [YAMANASHI, NAGANO, NIIGATA]                  # 甲信越
JP_HOKURIKU     = [TOYAMA, ISHIKAWA, FUKUI]                     # 北陸
JP_KITA_TOHOKU  = [AOMORI, IWATE, MIYAGI]                       # 北東北
JP_MINAMI_TOHOKU= [AKITA, YAMAGATA, FUKUSHIMA]                  # 南東北
JP_KITA_KANTO   = [IBARAKI, TOCHIGI, GUNMA]                     # 北関東
JP_MINAMI_KANTO = [SAITAMA, CHIBA, TOKYO, KANAGAWA]             # 南関東
JP_SANIN        = [TOTTORI, SHIMANE]                            # 山陰
JP_SANYO        = [OKAYAMA, HIROSHIMA, YAMAGUCHI]               # 山陽

# ---------------------------------------------------------------------------
# Hokkaido subprefectures (総合振興局・振興局)
# ---------------------------------------------------------------------------

_SUBPREF_DATA: list[tuple[str, str, tuple, list[str]]] = [
    # (varname, ja_name, bbox, alt_spellings)
    ("SORACHI",    "空知",        (43.00, 141.50, 44.10, 142.90), []),
    ("ISHIKARI",   "石狩",        (42.60, 141.00, 43.60, 141.90), []),           # Sapporo
    ("SHIRIBESHI", "後志",        (42.40, 139.95, 43.40, 141.20), []),           # Otaru/Niseko
    ("IBURI",      "胆振",        (42.20, 140.60, 43.10, 141.90), []),           # Tomakomai/Muroran
    ("HITAKA",     "日高",        (41.95, 141.70, 43.20, 143.30), []),
    ("OSHIMA",     "渡島",        (41.35, 139.85, 42.55, 141.25), ["OSIMA"]),    # Hakodate
    ("HIYAMA",     "檜山",        (41.85, 139.33, 42.70, 140.20), []),
    ("KAMIKAWA",   "上川",        (43.10, 141.85, 44.55, 143.80), []),           # Asahikawa
    ("RUMOI",      "留萌",        (43.45, 141.20, 44.80, 142.15), []),
    ("SOYA",       "宗谷",        (44.50, 141.10, 45.52, 142.80), ["SOUYA"]),    # Wakkanai
    ("OKHOTSK",    "オホーツク",   (43.25, 142.50, 44.90, 145.82), ["OHOTSUKU", "網走"]),  # Abashiri/Kitami
    ("TOKACHI",    "十勝",        (42.15, 142.40, 43.85, 144.60), []),           # Obihiro
    ("KUSHIRO",    "釧路",        (42.75, 143.55, 44.10, 145.40), []),
    ("NEMURO",     "根室",        (43.10, 144.75, 44.50, 145.82), []),           # easternmost
]

HOKKAIDO_SUBPREF: list[Area] = []
HOKKAIDO_SUBPREF_ALIASES: dict[str, str] = {}

for _varname, _ja, _bbox, _alts in _SUBPREF_DATA:
    _area = jpn_area(_ja, "北海道", bbox=_bbox)
    globals()[_varname] = _area
    HOKKAIDO_SUBPREF.append(_area)
    HOKKAIDO_SUBPREF_ALIASES[_varname] = _ja
    for _alt in _alts:
        HOKKAIDO_SUBPREF_ALIASES[_alt] = _ja

# Convenience aliases
OHOTSUKU = OKHOTSK
OSIMA    = OSHIMA
SOUYA    = SOYA

# Hokkaido regional subdivisions
DO_DONAN  = [OSHIMA, HIYAMA]                              # 道南
DO_DOO    = [ISHIKARI, SORACHI, SHIRIBESHI, IBURI, HITAKA] # 道央
DO_DOHOKU = [KAMIKAWA, RUMOI, SOYA]                       # 道北
DO_DOTO   = [TOKACHI, KUSHIRO, NEMURO, OKHOTSK]           # 道東

# ---------------------------------------------------------------------------
# Tokyo districts  (south, west, north, east)
# ---------------------------------------------------------------------------

# 東京都 特別区部 — 23 Special Wards
TOKYO_23_WARD = [
    jpn_area("千代田区", "東京都", bbox=(35.665, 139.730, 35.705, 139.780)),
    jpn_area("中央区",   "東京都", bbox=(35.655, 139.760, 35.700, 139.830)),
    jpn_area("港区",     "東京都", bbox=(35.615, 139.720, 35.680, 139.795)),
    jpn_area("新宿区",   "東京都", bbox=(35.665, 139.680, 35.725, 139.745)),
    jpn_area("文京区",   "東京都", bbox=(35.695, 139.730, 35.740, 139.775)),
    jpn_area("台東区",   "東京都", bbox=(35.695, 139.770, 35.730, 139.810)),
    jpn_area("墨田区",   "東京都", bbox=(35.685, 139.790, 35.740, 139.840)),
    jpn_area("江東区",   "東京都", bbox=(35.620, 139.790, 35.720, 139.930)),
    jpn_area("品川区",   "東京都", bbox=(35.580, 139.695, 35.645, 139.775)),
    jpn_area("目黒区",   "東京都", bbox=(35.605, 139.670, 35.660, 139.725)),
    jpn_area("大田区",   "東京都", bbox=(35.535, 139.665, 35.625, 139.800)),
    jpn_area("世田谷区", "東京都", bbox=(35.595, 139.565, 35.680, 139.695)),
    jpn_area("渋谷区",   "東京都", bbox=(35.640, 139.675, 35.680, 139.730)),
    jpn_area("中野区",   "東京都", bbox=(35.685, 139.635, 35.730, 139.690)),
    jpn_area("杉並区",   "東京都", bbox=(35.665, 139.580, 35.720, 139.675)),
    jpn_area("豊島区",   "東京都", bbox=(35.715, 139.685, 35.760, 139.730)),
    jpn_area("北区",     "東京都", bbox=(35.735, 139.700, 35.790, 139.760)),
    jpn_area("荒川区",   "東京都", bbox=(35.725, 139.770, 35.760, 139.825)),
    jpn_area("板橋区",   "東京都", bbox=(35.735, 139.645, 35.800, 139.730)),
    jpn_area("練馬区",   "東京都", bbox=(35.715, 139.565, 35.795, 139.680)),
    jpn_area("足立区",   "東京都", bbox=(35.745, 139.770, 35.830, 139.905)),
    jpn_area("葛飾区",   "東京都", bbox=(35.720, 139.825, 35.790, 139.935)),
    jpn_area("江戸川区", "東京都", bbox=(35.660, 139.835, 35.745, 139.930)),
]

# 多摩地域 — Tama Area (Western Tokyo)
TOKYO_TAMA = [
    jpn_area("立川市",     "東京都", bbox=(35.665, 139.370, 35.730, 139.435)),
    jpn_area("武蔵野市",   "東京都", bbox=(35.695, 139.540, 35.735, 139.595)),
    jpn_area("三鷹市",     "東京都", bbox=(35.670, 139.530, 35.720, 139.590)),
    jpn_area("府中市",     "東京都", bbox=(35.640, 139.450, 35.700, 139.535)),
    jpn_area("昭島市",     "東京都", bbox=(35.685, 139.330, 35.745, 139.410)),
    jpn_area("調布市",     "東京都", bbox=(35.630, 139.520, 35.680, 139.590)),
    jpn_area("小金井市",   "東京都", bbox=(35.690, 139.490, 35.730, 139.550)),
    jpn_area("小平市",     "東京都", bbox=(35.715, 139.445, 35.750, 139.525)),
    jpn_area("東村山市",   "東京都", bbox=(35.745, 139.465, 35.790, 139.530)),
    jpn_area("国分寺市",   "東京都", bbox=(35.685, 139.440, 35.730, 139.500)),
    jpn_area("国立市",     "東京都", bbox=(35.660, 139.430, 35.700, 139.475)),
    jpn_area("狛江市",     "東京都", bbox=(35.625, 139.560, 35.660, 139.605)),
    jpn_area("東大和市",   "東京都", bbox=(35.730, 139.410, 35.775, 139.475)),
    jpn_area("清瀬市",     "東京都", bbox=(35.760, 139.510, 35.800, 139.565)),
    jpn_area("東久留米市", "東京都", bbox=(35.755, 139.520, 35.795, 139.570)),
    jpn_area("武蔵村山市", "東京都", bbox=(35.735, 139.380, 35.780, 139.445)),
    jpn_area("西東京市",   "東京都", bbox=(35.715, 139.520, 35.760, 139.570)),
    jpn_area("八王子市",   "東京都", bbox=(35.520, 139.270, 35.730, 139.435)),
    jpn_area("町田市",     "東京都", bbox=(35.510, 139.415, 35.620, 139.560)),
    jpn_area("日野市",     "東京都", bbox=(35.635, 139.370, 35.695, 139.435)),
    jpn_area("多摩市",     "東京都", bbox=(35.600, 139.420, 35.660, 139.495)),
    jpn_area("稲城市",     "東京都", bbox=(35.615, 139.480, 35.670, 139.545)),
    jpn_area("青梅市",     "東京都", bbox=(35.740, 139.205, 35.850, 139.325)),
    jpn_area("福生市",     "東京都", bbox=(35.730, 139.320, 35.775, 139.360)),
    jpn_area("羽村市",     "東京都", bbox=(35.745, 139.295, 35.790, 139.350)),
    jpn_area("あきる野市", "東京都", bbox=(35.700, 139.245, 35.785, 139.340)),
    jpn_area("瑞穂町",     "東京都", bbox=(35.770, 139.350, 35.825, 139.415)),
    jpn_area("日の出町",   "東京都", bbox=(35.730, 139.230, 35.790, 139.300)),
    jpn_area("檜原村",     "東京都", bbox=(35.680, 139.085, 35.820, 139.270)),
    jpn_area("奥多摩町",   "東京都", bbox=(35.735, 138.950, 35.960, 139.185)),
]

# 島嶼部 — Insular Area
TOKYO_ISLANDS = [
    jpn_area("大島町",   "東京都", bbox=(34.630, 139.315, 34.800, 139.435)),
    jpn_area("利島村",   "東京都", bbox=(34.510, 139.265, 34.545, 139.295)),
    jpn_area("新島村",   "東京都", bbox=(34.335, 139.105, 34.415, 139.185)),
    jpn_area("神津島村", "東京都", bbox=(34.185, 139.085, 34.240, 139.125)),
    jpn_area("三宅村",   "東京都", bbox=(34.045, 139.490, 34.110, 139.565)),
    jpn_area("御蔵島村", "東京都", bbox=(33.865, 139.570, 33.915, 139.615)),
    jpn_area("八丈町",   "東京都", bbox=(33.065, 139.715, 33.155, 139.840)),
    jpn_area("青ヶ島村", "東京都", bbox=(32.450, 139.750, 32.475, 139.780)),
    jpn_area("小笠原村", "東京都", bbox=(26.530, 141.275, 27.095, 142.280)),
]

# 東京都 全域
TOKYO_ALL = TOKYO_23_WARD + TOKYO_TAMA + TOKYO_ISLANDS

# ---------------------------------------------------------------------------
# Named preset groups  (used by --preset)
# ---------------------------------------------------------------------------

PRESETS: dict[str, list[Area]] = {
    "todofuken":      JP_PREFECTURES,
    "todoufuken":     JP_PREFECTURES,
    "prefectures":    JP_PREFECTURES,
    "hokkaido":       [HOKKAIDO],
    "tohoku":         JP_TOHOKU,
    "kanto":          JP_KANTOU,
    "chubu":          JP_CHUBU,
    "kinki":          JP_KINKI,
    "chugoku":        JP_CHUGOKU,
    "shikoku":        JP_SHIKOKU,
    "kyusyu":         JP_KYUSYU,
    "kansai":         JP_KANSAI,
    "tokai":          JP_TOKAI,
    "tosan":          JP_TOSAN,
    "koshinetsu":     JP_KOSHINETSU,
    "hokuriku":       JP_HOKURIKU,
    "kitatohoku":     JP_KITA_TOHOKU,
    "minamitohoku":   JP_MINAMI_TOHOKU,
    "kitakanto":      JP_KITA_KANTO,
    "minamikanto":    JP_MINAMI_KANTO,
    "sanin":          JP_SANIN,
    "sanyo":          JP_SANYO,
    "hokkaido_subpref": HOKKAIDO_SUBPREF,
    "donan":          DO_DONAN,
    "doo":            DO_DOO,
    "dooh":           DO_DOO,
    "dooou":          DO_DOO,
    "dohoku":         DO_DOHOKU,
    "doto":           DO_DOTO,
    "dootou":         DO_DOTO,
    "tokyo_23":       TOKYO_23_WARD,
    "tokyo_tama":     TOKYO_TAMA,
    "tokyo_islands":  TOKYO_ISLANDS,
    "tokyo_all":      TOKYO_ALL,
    "tokyo_full":     TOKYO_ALL,
}

# ---------------------------------------------------------------------------
# Auto-discovery exports
# ---------------------------------------------------------------------------

REGION = "JP"
DEFAULT_PRESET = "tokyo_23"
ALIASES: dict[str, str] = {**AREA_ALIASES, **EN_ALIASES, **JA_ALIAS, **HOKKAIDO_SUBPREF_ALIASES}
AREAS = JP_PREFECTURES + HOKKAIDO_SUBPREF

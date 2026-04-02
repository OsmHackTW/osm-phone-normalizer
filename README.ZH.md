# osm-phone-normalizer

## 這個專案在做什麼？

`osm-phone-normalizer` 正規化工具透過 Overpass API 抓取指定區域的 OSM 元件，將每個 `phone` 和 `contact:phone` 等標籤送進以 `google/libphonenumber` 為核心的解析器，搭配指定的後處理層修正格式（詳見下文），最後產生一組建議變更集。

變更集可以透過 `--dry-run --verbose` 預覽，也匯出為 `.osc` 變更集以在 JOSM 中檢視，或使用 `--upload api` 直接上傳到 OSM API。

這個正規化工具目標不是跑一個自動化機器人——每批變更上傳前都要人工確認。<s>（BOT也不是不行）</s>
工具目前的定位是前置篩選：把機械式的簡單修正先處理掉，讓貢獻者把力氣留給真正需要判斷的編輯工作。

值得一提的常見情況：貢獻者常在其他原因（改名稱、更新營業時間、補上地址）編輯 POI 時，會順手新增或修正國碼和區碼。這帶來了零星改進，但因為一千個人心中有一千個<s>巴哈姆特</s>哈姆雷特，格式不盡相同。正規化工具就是要補足這塊：社群對目標格式有共識之後，一次有組織的批次處理，就能讓所有資料整齊劃一。

相關文章資訊亦發布於 OSM User Diaries，詳見[臺灣華語版](https://www.openstreetmap.org/user/assanges/diary/408434)與[英文版](https://www.openstreetmap.org/user/assanges/diary/408433)文章。

---

## 安裝

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

**需求：** Python 3.11+、`phonenumbers`、`requests`、`rich`

> 註：個人推薦使用 `uv`

---

## 使用方式

```
python main.py [--target TARGET | --preset PRESET] [options]
```

### 區域選擇

| 參數 | 說明 |
|------|------|
| `--target TARGET` | 以代碼、中文或英文名稱指定單一區域 |
| `--preset PRESET` | 預設區域群組（`cities`、`taipei`、`new_taipei`……） |

`--target` 接受多種格式：

```sh
python main.py --target TPE           # ISO 3166-2 代碼
python main.py --target Taitung       # 英文名稱
python main.py --target 竹市           # 中文簡稱
python main.py --target 臺東縣         # 中文全名
```

### 選項

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `--region` / `-r` | `TW` | 電話解析用的國家代碼，預設為臺灣 (`TW`)，可自訂（另見 `CONTRIBUTING.md`） |
| `--list` / `-l` | `preset` | 列出可用的預設群組集 (`preset`) 或 區域別名 (`alias`)，預設為 `preset`，`TW` 以外需指定 `--region` |
| `--format` | `e123` | 輸出格式：`e123`（E.123 國際格式）或 `rfc3966`（`tel:` URI） |
| `--no-cache` | — | 即使有本地快取也重新從 Overpass 抓取 |
| `--dry-run` | — | 顯示變更建議但不寫入檔案 |
| `--verbose` / `-v` | — | 逐筆印出變更前後的標籤值 |
| `--upload` | — | 匯出／上傳模式：`josm`、`api` 或 `level0` |
| `--changeset-comment` | `"Normalize phone numbers to E.123 format"` | `--upload api` 的變更集說明 |
| `--output-dir` | `cache/` | Overpass 快取目錄 |
| `--delay` | `0`（單筆）、`5`（批次） | Overpass 請求間隔秒數 |
| `--print-query` | — | 印出 Overpass QL 查詢後結束 |

### 範例

```sh
# 預覽「臺北」區域的變更，不寫入任何檔案
python main.py --target TPE --dry-run --verbose

# 掃描「高屏」地區並顯示變更標籤
python main.py --preset greater_kaohsiung

# 重新抓取「臺東」並逐筆顯示變更
python main.py --target Taitung --no-cache --verbose

# 匯出變更 .osc 並在 JOSM 中開啟審閱
python main.py --target TXG --upload josm

# 直接上傳到 OSM API（需設定 OSM_ACCESS_TOKEN）
export OSM_ACCESS_TOKEN=your_oauth2_token
python main.py --target NWT --upload api

# 以 RFC 3966 tel: URI 格式輸出
python main.py --target KHH --format rfc3966
```

---

## 正規化的標籤

正規化工具處理以下 OSM 標籤：

- `phone`、`contact:phone`
- `fax`、`contact:fax`
- `phone:mobile`、`contact:mobile`
- `emergency:phone`、`phone:delivery`

多值欄位（分號分隔）與分機後綴（`ext.`、`#`、`x`、`~`）均正確處理。無效號碼維持原封不動。

> 註：臺灣資料另有加碼，`addr:city` 內含 `台` 者，會自動修正為官方正體 `臺`。

---

## 上傳模式

### `--upload josm`

將 `changes.osc` 寫入輸出目錄，並透過 Remote Control（port 8111）傳送給 JOSM。  
需在 JOSM 啟用：**編輯 → 偏好設定 → 遠端控制 → 啟用遠端控制**。  
若 JOSM 無法連線，會印出 `.osc` 檔案路徑供手動匯入。

> **注意：** JOSM 上傳需要元素的版本資訊。若出現版本缺失警告，請加上 `--no-cache` 重新執行。

### `--upload api`

使用 OAuth 2.0 Bearer Token 直接上傳到正式 OSM API：

```sh
export OSM_ACCESS_TOKEN=<your token>
python main.py --target TPE --upload api
```

工具會自動建立變更集、上傳差異並關閉變更集，成功後印出變更集 URL。

### `--upload level0`

為每個區域印出預載 Overpass 查詢的 level0 URL，可在瀏覽器中手動審閱與編輯。

---

## 區域預設（`--preset`）

| 預設名稱 | 說明 | 備註 |
|----------|------|------|
| `tw_all` | 臺灣所有 22 個縣市（完整清單） |  |
| `greater_taipei` / `北北基` | 臺北市＋新北市＋基隆市 |  |
| `greater_taichung` / `中彰` | 臺中市＋彰化縣 |  |
| `greater_kaohsiung` / `高屏` | 高雄市＋屏東縣 |  |
| `cwa_north` | 北部區域，北北基桃竹苗 | (中央氣象署) |
| `cwa_central` | 中部區域，中彰投雲嘉 | (中央氣象署) |
| `cwa_south` | 南部區域，南高屏東 | (中央氣象署) |
| `cwa_east` | 東部區域，宜花東 | (中央氣象署) |
| `cwa_outlying` | 外島區域，澎金馬 | (中央氣象署) |

---

## 指定的後處理層：為什麼要覆寫 `google/libphonenumber` 的臺灣號碼處理

正規化臺灣電話號碼時，我們發現 Google [libphonenumber](https://github.com/google/libphonenumber)（業界標準的電話號碼解析函式庫）存在一個隱微但重要的問題。

### 問題所在

臺灣的《公眾電信網路號碼計畫》（2022年8月27日起由數位發展部 (MODA) 主管）為偏遠地區及離島配置了 **3 碼和 4 碼區碼**，但 libphonenumber 的資料將這些範圍一律視為 2 碼區碼，導致分組錯誤：

| 撥號號碼 | libphonenumber 輸出 | 正確輸出 |
|----------|---------------------|----------|
| 037-123-456 | `+886 3 7123 456` | `+886 37 123 456` |
| 049-123-4567 | `+886 4 9123 4567` | `+886 49 123 4567` |
| 082-123-456 | `+886 8 2123 456` | `+886 82 123 456` |
| 0826-12345 | `+886 8 26123 45` | `+886 826 12345` |
| 0836-12345 | `+886 8 36123 45` | `+886 836 12 345` |\
| 089-123-456 | `+886 8 9123 456` | `+886 89 123 456` |

受影響地區：**苗栗（037）**、**南投（049）**、**金門（082）**、**烏坵（0826）**、**馬祖（0836）**、**臺東（089）**。

部分 **0800 免付費** 號碼也有同樣的問題。

### 原因

libphonenumber 的臺灣資料假設 `03x`、`04x`、`08x` 前綴一律是 2 碼區碼。這對主要城市（`02` 台北、`03` 新竹、`04` 台中、`08` 屏東）沒問題，但碰到上述地區的例外就對不上了。


### 我們的修正方式

由於等待 libphonenumber 上游修正需時，我們直接在 `phone_normalizer/countries/tw.py` 加了一層後處理。libphonenumber 格式化完成後，檢查 `national_number` 前綴與長度，再按 MODA 公告的區碼表重新格式化：

```python
# 範例：苗栗（037）— national_number 以 "37" 開頭，共 8 碼
area, local = "37", nn[2:]
sub = f"{local[:3]} {local[3:]}"    # NNN NNN
return f"+886 {area} {sub}"         # +886 37 NNN NNN
```

輸出結果與名片、招牌及官方臺灣電話簿的格式一致。

### 小結

libphonenumber 在大多數情況下都很可靠，但臺灣偏遠區碼這種特殊情況需要在地知識。資料庫跟不上現實時，針對性的後處理就是最直接的解法。

---

## 專案結構

```
osm-phone-normalizer/
├── main.py                     # CLI 入口與處理流程
├── requirements.txt
├── overpass/                   # Overpass API 客戶端
│   ├── areas.py                # 區域定義（bbox、篩選條件）
│   ├── batch.py                # 平行／循序抓取與去重
│   ├── query.py                # Overpass QL 查詢產生器
│   ├── nominatim.py            # 透過 Nominatim 解析區域名稱
│   └── presets/
│       ├── tw.py               # TW 區域清單、別名、預設
│       └── <cc>.py             # 其他自訂地區的區域清單
├── phone_normalizer/           # 正規化邏輯
│   ├── core.py                 # 號碼解析、分機處理
│   ├── process.py              # 逐節點標籤處理與 apply_changes
│   └── countries/
│       ├── tw.py               # 臺灣修正層（3/4 碼區碼）
│       └── <cc>.py             # 其他地區的修正層
├── upload/                     # 變更匯出／上傳
│   ├── josm.py                 # JOSM Remote Control
│   ├── osm_api.py              # OSM API 變更集上傳
│   └── level0.py               # level0 URL 產生器
└── cache/                      # Overpass 快取（已 gitignore）
```

---

## 貢獻

想在自己負責的區域試跑看看：

```sh
python main.py --target TPE --dry-run --verbose   # 預覽臺北變更
python main.py --preset greater_kaohsiung         # 掃描大高雄並顯示變更標籤
```

歡迎提出 Issue 和 PR。

---

> 本文件因人類的懶散墮落，由 [Claude](https://claude.ai) 幻覺生成。內容經裝懂的人類長官象徵性審閱後，蓋章出貨。
> 出包錯誤由克氏負責背鍋，成品功勞盡歸人類長官。直到永遠，阿門！
>（Claude：懂的都懂，塊陶！！

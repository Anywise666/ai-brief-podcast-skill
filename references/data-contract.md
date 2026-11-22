# 简报数据契约与数据源适配

页面（`dashboard-template.html`）和音频脚本（`gen_audio.py` / `gen_feed.py`）都只认下面这一种 report 结构。无论原始数据来自哪里，都要先适配成它——不要反过来去改页面和脚本。

## 契约结构（aihot 兼容）

```json
{
  "date": "2026-11-22",
  "lead": {
    "title": "今日头条标题",
    "leadParagraph": "头条正文或摘要",
    "originalTitle": "English headline（可选）",
    "links": { "aihot": "https://.../items/abc123", "original": "https://原文" }
  },
  "sections": [
    {
      "key": "ai-models",
      "label": "模型发布/更新",
      "items": [
        {
          "title": "条目标题",
          "summary": "一到两句摘要",
          "originalTitle": "English title（可选）",
          "id": "abc123（可选，作为音频文件名 key）",
          "links": { "aihot": "https://.../items/abc123", "original": "https://原文" }
        }
      ]
    }
  ],
  "flashes": [],
  "highlights": [],
  "attribution": { "name": "数据来源名" },
  "links": { "aihot": "https://来源首页" }
}
```

字段约定：

- `lead`：今日头条。`title` 必填；`leadParagraph` 或 `summary` 二选一用于朗读。
- `sections[]`：板块。`label` 决定页面上显示的板块名；`key` 决定配色（需在模板 `SITE_CFG.sections` 里登记）。
- `items[]`：`title`、`summary` 用于中文朗读；`originalTitle` 存在时额外生成英文 mp3，缺失则降级为纯中文（这是硬性要求，微信场景依赖预生成音频）。
- `id` / `links.aihot`：用于生成稳定的音频文件名（取 URL 末尾的 item id）。都缺失时用标题哈希兜底。
- `date`：ISO 日期；页面与 RSS 以它为准。

## 数据源模式（`data_mode`）

站点根目录 `site.config.json` 的 `data_mode` 决定数据从哪来，两种模式：

### 模式 A：`aihot`（默认，零配置）

适用于直接用 aihot.news 的用户。`common.fetch_report()` 请求：

- `GET {api_base}/dailies/{date}` → 取 `report`
- `GET {api_base}/items?limit=100` → 取 `originalTitle` 映射

字段天然符合契约，无需适配。模板顶部 `SITE_CFG.apiBase` 填同样的地址。

### 模式 B：`local`（自定义数据源 / 无 API）

把每天的数据写成一个 JSON 文件放到 `data/{date}.json`（如 `data/2026-11-22.json`），内容是上面的契约对象（或包一层 `{"report": {...}}`）。`common.fetch_report()` 直接读取。

适配示例——假设原始数据是 RSS/任意 JSON，用一个小脚本每天生成契约文件：

```python
# tools/make_daily.py —— 把你的原始数据转成契约
import json, datetime, os

def to_contract(raw, date):
    return {
        "date": date,
        "lead": {"title": raw["headline"], "leadParagraph": raw.get("desc", "")},
        "sections": [{
            "key": "industry", "label": "要闻",
            "items": [
                {"title": x["title"], "summary": x.get("body", ""),
                 "originalTitle": x.get("en_title", ""), "id": str(x["id"])}
                for x in raw["articles"]
            ],
        }],
        "attribution": {"name": "我的数据源"},
    }

date = datetime.date.today().isoformat()
raw = json.load(open("raw/latest.json", encoding="utf-8"))
os.makedirs("data", exist_ok=True)
json.dump(to_contract(raw, date), open(f"data/{date}.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
```

对应配置：

```json
{ "data_mode": "local", "local_data_dir": "data", "site_url": "...", "brand_line": "我的简报" }
```

## 模板顶部 SITE_CFG 的生成

`assets/dashboard-template.html` 顶部有一段 `SITE_CFG` 对象，生成站点时按 `site.config.json` 替换它（只需改这一处）：

| SITE_CFG 字段 | 来源（site.config.json） |
|---|---|
| `dataMode` | `data_mode`（`aihot` 或 `local`）— **必填，local 改造依赖它** |
| `apiBase` | `api_base`（local 模式可留空字符串） |
| `brand` | `brand_line` 或 `site_name` |
| `brandEn` | 英文缩写品牌名（可自定义） |
| `dataCredit` | `data_credit` |
| `docTitle` | `site_name + " · 日历档案"` |
| `sections` | 板块列表（`key`/`label`/`color`），需与数据契约里出现的 key 对应 |

## local 模式：页面改造的完整配方（已实测）

模板默认走 aihot API。若用 local 模式，页面必须做以下三处改造，否则会白屏/日历为空。**这是 E2E 实测发现的坑，照此做即可。**

### 1. SITE_CFG 加 `dataMode`

```js
var SITE_CFG = {
  dataMode: "local",   // 新增这一行
  apiBase: "",
  brand: "你的简报", ...
};
```

### 2. 改 `fetchJson()`（`index.html` 约 509 行）

模板里所有取数都走这一个函数，改它即可覆盖日报、索引、英文映射三处：

```js
function fetchJson(path){
  if(SITE_CFG.dataMode === 'local'){
    if(path.indexOf('/dailies?')===0) return fetch('data/index.json',{cache:"no-store"}).then(function(r){return r.ok?r.json():null;}).catch(function(){return null;});
    var m=path.match(/\/dailies\/(\d{4}-\d{2}-\d{2})/);
    if(m) return fetch('data/'+m[1]+'.json',{cache:"no-store"}).then(function(r){return r.ok?r.json():null;}).catch(function(){return null;});
    return Promise.resolve(null);   // /items 等：local 模式下英文原题走契约内联字段
  }
  return fetch(BASE + path, {cache:"no-store"}).then(function(r){return r.ok?r.json():null;}).catch(function(){return null;});
}
```

### 3. 生成 `data/index.json`（日历索引）

`loadIndex()` 需要 `/dailies?limit=` 返回一个带 `items` 的索引。local 模式下要手工维护这个文件：

```json
{ "items": [
    {"date": "2026-11-22", "leadTitle": "头条标题", "leadParagraph": "头条摘要"}
  ]}
```

每新增一天数据，同步往 `data/index.json` 的 `items` 里加一条。

### 关于板块匹配

`matchKey()` 会先用 `SECTIONS_META[i].label === label` 精确匹配 SITE_CFG 里登记的 label，匹配不到才走中文字面量兜底。所以**只要 SITE_CFG.sections 的 label 与数据契约里 sections[].label 一致**（如都是"产业动态"），自定义板块就能正确归组，无需改 matchKey。

> 档位 1/2/3 若都用 aihot 默认链路，以上三处都不用动；只有换成 local 或自有 API 时才需要。改造后务必用 `node --check` 校验内嵌 JS 语法。

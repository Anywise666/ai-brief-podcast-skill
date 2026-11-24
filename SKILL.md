---
name: ai-brief-podcast
version: 1.1.1
display_name: 新闻播客站生成器：AI日报/晨报+双语RSS
display_name_en: News Podcast Site Builder - AI Daily Brief & Bilingual RSS
description: 'Use whenever the user wants to turn a daily brief, morning news digest, industry newsletter or articles into a website people can read, listen to and subscribe to. Builds a self-contained "daily news / morning brief" dashboard site with auto-generated bilingual (Chinese/English) podcast audio and an RSS feed subscribeable in 小宇宙/Apple/Spotify. Covers: single-file HTML dashboard, text-to-speech mp3, RSS feed, and scheduled auto-update. Trigger on phrases like 每日简报站/晨报网站/新闻播客/新闻播客站/播客订阅/日报仪表盘/AI日报/AI晨报/daily brief site/newsletter 转播客/把文章变成播客, even if the user does not say "skill" or "dashboard" explicitly.'
description_zh: '把一份每天更新的简报变成一个可以看网页、可以听的中英双语播客、可以被订阅的 RSS 节目，并配好每日自动更新。用户只需说清内容来源、主题名称和发布方式，剩下的交给这个 skill——单文件 HTML 仪表盘、中英双语 mp3、订阅源、定时上线以及一整套踩过坑才有的容错处理。适合做行业晨报站、把文章转成播客、让内容每天自动发布并被小宇宙或 Apple Podcasts 订阅的人，按需求分三档交付：只想自己看效果、想发链接给别人看、想让别人每天能听能订阅——用户按想要什么结果选档，不按技术能力选。'
description_en: 'Turn any daily brief into a website you can read, a bilingual Chinese-English podcast you can listen to, and an RSS feed people can subscribe to, with automatic daily publishing wired in. Users only specify their content source, topic name and publishing preference; the skill delivers a self-contained HTML dashboard, bilingual mp3 audio, an RSS feed, scheduled publishing and a full set of battle-tested fallbacks. Ideal for industry morning-brief sites, converting articles into podcasts, and recurring content that subscribers follow in 小宇宙 or Apple Podcasts.'
---

# AI 简报播客站生成器

把「一份每天更新的简报」变成一个可以**看**（单文件 HTML 仪表盘）、可以**听**（中英双语 mp3）、可以**订阅**（RSS 播客）的站点，并配好每日自动更新。

这个 skill 的价值不在于生成 HTML——那只是模板。真正的价值是把一条已经验证过的完整链路交付给用户：数据 → 页面 → 音频 → RSS → 定时上线，以及沿途那些踩过坑才有的容错处理。

## 何时使用

- 用户想做一个每日更新的简报 / 晨报 / 行业资讯网站。
- 用户想把文字内容（新闻、文章、日报）变成可订阅的播客。
- 用户提到 RSS 订阅、播客客户端、每天自动生成音频、90 秒速览等需求。
- 用户已有类似站点，想复刻或迁移到新主题 / 新数据源。

## 第一步：确认三个关键输入

在动手前，先问清楚（能从上下文推断的就不要问）：

1. **内容来源**：一个 JSON API、一个 RSS、一个固定格式的文件，还是"先用示例数据"？
   - 这是最关键的决策。音频和页面都依赖结构化数据，必须先定义数据契约（见下）。
2. **站点主题与名称**：中文站名、简介、播客名。
3. **发布方式（想要什么结果）**：按第二步的需求分档——是想自己先看效果、想发链接给别人看，还是想让别人每天能听能订阅。这决定是否要 GitHub 账号和能否长期订阅。别直接问"你会不会用 GitHub"，先问用户想拿它做什么。

如果用户只要一个"能看的 demo"，允许用示例数据先把站点跑起来，别卡在数据源上。

## 第二步：按用户需求分级（拿不准默认最低档）

三个档位，能力递增、门槛递增。**按"用户想要什么结果"选档，不按"用户会不会技术"选**——技术强的人也可能只想本地先看效果，小白也可能就是想要能订阅的播客。拿不准时默认推荐档位 1，用户明确说"要发链接给别人"才上档位 2，明确说"要能听能订阅、每天自动更新"才上档位 3。

| 档位 | 一句话选它（用户需求） | 交付内容 | 播客功能 | 用户需要准备 |
|---|---|---|---|---|
| 1 · 本地站 | "我先自己看看效果" | 单文件 HTML，双击即可看 | 不启用（纯文字） | 什么都不用 |
| 2 · 在线站 | "我要发个链接给别人看" | 发布为可分享链接，每天手动或用 WorkBuddy 定时任务更新数据 | 不启用（纯文字） | 一个 WorkBuddy 账号 |
| 3 · 可订阅站 | "我要别人每天能听、能订阅、自动更新" | GitHub Pages 固定域名 + Actions 每日自动生成音频与重建 RSS + 播客订阅 | 启用（音频 + RSS + 订阅） | GitHub 账号、开 Pages、token 读写权限 |

**问用户时的标准话术**（照着问，别问"你会不会用 GitHub"）：只想自己打开看 → 档位 1；想发链接给别人看 → 档位 2；想让别人在播客 App 里订阅、每天自动更新 → 档位 3。用户没说清就默认档位 1，并明确告知"随时能升级"。

**功能边界要前置讲清**：档位 1/2 只做文字、页面不出现播客/订阅入口；只有档位 3 才有"听"和"订阅"。这句话必须在用户选档时就说，不要等交付后才发现预期不符——这是 v1.0 热搜站"按钮能点没反应"故障的预期管理根源。

**功能与档位严格对应（硬性要求）**：只做当前档位要求的功能，**不显示未启用的功能**。档位 1/2 的播客开关 `podcast=false`，页面不出现"听播客 / 90 秒速览 / 订阅"按钮，只呈现文字内容；档位 3 才设 `podcast=true` 并生成音频链。绝不能留下"按钮能点但没反应"的半成品——这是 v1.0 的真实故障根因。

档位 2 使用平台自带的静态站点发布能力（workbuddy_sites_deploy）；档位 3 需要 GitHub Actions workflow。

## 第三步：定义数据契约（决定后续能否通用化）

现有参考实现硬编码了 `aihot.news` 的接口和字段。要做成通用 skill，**必须把数据源抽象掉**，否则这个 skill 只对一家数据源有用。

约定一个最小数据契约，页面和音频脚本都只认它：

```json
{
  "date": "2026-11-22",
  "title": "今日头条标题",
  "summary": "头条摘要",
  "sections": [
    { "name": "板块名", "items": [
        { "title": "条目标题", "summary": "摘要", "originalTitle": "英文原标题（可选）", "url": "原文链接" }
    ]}
  ]
}
```

- 若用户数据源字段不同，写一个适配层把原始 JSON 映射成上面的结构，**不要改页面和音频脚本**。
- `originalTitle` 缺省时音频降级为中文单朗读，页面不显示英文行——这个降级必须保留。
- 若用户没有数据源，用 3~5 条示例数据填进去，让链路先跑通。

## 第四步：生成单文件 HTML 仪表盘

参考 `assets/dashboard-template.html`（从验证过的实现抽象而来）。必须遵守：

- **单文件自包含**：内联 CSS/JS，无外部依赖、无构建步骤，双击可打开。
- **响应式**：手机端可用（用户在微信里打开是高频场景）。
- **音频优先用预生成 mp3**：页面先尝试 `<audio src="audio/<日期>/brief_zh.mp3">`，加载失败（404）才回退浏览器 `Web Speech API` 朗读。
  - 这一步是硬性要求：**微信内置浏览器不支持 Web Speech API**，没有预生成 mp3 就意味着微信里点"听"没反应。
- **偏好存 localStorage**：收藏、已读、主题、字号、播放倍速（刷新不丢，无需后端）。
- 必备元素：日历/日期切换、卡片列表、收藏/分享、深浅色切换、字号调节。
- **播客相关元素按档位**：模板顶部 `SITE_CFG.podcast` 为总开关。档位 1/2 保持默认 `false`，模板会自动隐藏全部"播放按钮 / 90 秒速览 / 订阅"入口，页面纯文字；档位 3 设为 `true`，这些入口才出现。务必让开关与实际是否生成音频一致——不要只改配置开着开关却不跑音频脚本。

## 第五步：生成双语播客音频（仅档位 3）

> 档位 1/2 跳过本步与第六、七步，不要生成 `audio/`、`feed.xml`，也不要在页面露出播客入口。

调用 `scripts/gen_audio.py <日期>`（依赖 `pip install edge-tts`）：

- 为头条 + 每张卡片生成"中文（标题+摘要）→英文（originalTitle）"串读的 mp3。
- 额外生成 `brief_zh.mp3`：头条 + 各板块首条串读的 90 秒速览。
- 输出 `audio/YYYY-MM-DD/` + `manifest.json`（当天完成标记）。
- 音色默认 `zh-CN-XiaoxiaoNeural` / `en-US-JennyNeural`，允许用户替换。

适配新数据源时，把脚本里 `fetch_json` / 字段解析部分改为读第三步的数据契约；TTS 合成与文件组织逻辑可直接复用。

关键容错（都是踩坑得来的，别删）：

- 条目无 `originalTitle` → 跳过英文段，不要合成空音频。
- 文本先清洗零宽字符和多余空白，否则 TTS 会读出乱码或长停顿。
- 合成网络失败要有重试（参考实现的 `retries=3`）。
- 超过保留期（默认 30 天）的旧音频目录自动清理，避免仓库膨胀。

## 第六步：生成 RSS 订阅源（档位 3）

调用 `scripts/gen_feed.py`：

- 扫描 `audio/YYYY-MM-DD/`，按 `manifest.json` 生成标准 RSS 2.0 + iTunes 命名空间。
- 每期标题=日期，`enclosure` 指向 `brief_zh.mp3`，`pubDate` 用北京时间。
- 保留最近 60 期，输出 `feed.xml`。
- 站点 URL、播客名、描述必须改为用户自己的（参考实现里是硬编码的，记得参数化）。

校验：`feed.xml` 发布后，用播客客户端或 RSS 阅读器确认能拉到、enclosure 链接返回 200 且 `Content-Type` 为 `audio/*`。

## 第七步：配每日自动更新（档位 3）

用 `assets/daily-podcast.yml` 作为 GitHub Actions 基线。要点（每一条都对应一次真实故障，务必保留）：

1. **幂等**：以当天 `manifest.json` 是否存在为"已完成"标记，避免重复生成。
2. **触发时间集中在目标上线时段**：如果用户要求"早上 8:30 上线"，就把三个 cron 全放在 08:0x~08:2x 窗口（如 `08/16/24 0 * * *`），**不要**为了防丢弃而把时点散布到午后/晚上——那会让"早上能听"的初衷落空。

   **北京时间 → UTC cron 换算规则（务必按此算，别照抄模板里的示例分钟）**：
   - cron 格式为 `分 时 日 月 周`，只认 UTC；北京时间 = UTC + 8，所以 **UTC 时 = 北京时 − 8**。
   - 取 `site.config.json` 的 `cron_minutes`（三个错峰分钟），减去 `pub_hour` 后若 < 0，则 UTC 小时 = `pub_hour − 8`，用前一天（但 cron 是每天循环，`分 时 * * *` 无需写日期，直接写该 UTC 时刻即可）。
   - 换算公式：`utc_hour = pub_hour − 8`。若 `utc_hour < 0`，加 24（如北京 7 点 → UTC 前一天 23 点，cron 写 `M 23 * * *`）。分钟直接用 `cron_minutes` 的三个值。
   - 例：`pub_hour=8, cron_minutes=[8,16,24]` → `08 0 * * *` / `16 0 * * *` / `24 0 * * *`。
   - 例：`pub_hour=7, cron_minutes=[12,20,28]` → utc_hour=23 → `12 23 * * *` / `20 23 * * *` / `28 23 * * *`。
   - 兜底任务时间用 `fallback_hour:fallback_minute`（北京时间，交给 WorkBuddy 调度器，它按本地时区，无需换算）。
3. **避开整点/半点**：GitHub 云端 cron 在这些时刻拥堵，可能被延迟甚至丢弃。
4. **push 兜底**：加 `push` 触发（排除 `audio/**`、`feed.xml` 自身防递归），让日常提交也能补上当天生成，同时规避"公共仓库 60 天无提交自动停用定时任务"。
5. **最后防线**：在 WorkBuddy 建一个定时兜底任务（脚本 `scripts/ensure_today.sh`），检查线上当天 mp3 是否存在，缺失才本地补跑。时间同样设在目标上线窗口内（如 08:40），确保不破坏"早上上线"的承诺。
6. **权限**：workflow 需要 `contents: write`，仓库 Settings → Actions → Workflow permissions 设为 Read and write。

Windows 本地环境注意：代理可能间歇性拦截 `github.com` 的 git 传输（SSL 握手失败 / CONNECT 502），push 要带 `GIT_HTTP_VERSION=HTTP/1.1` 并重试。**当 `github.com` 完全不通时，`api.github.com` 往往仍可用**——`scripts/ensure_today.sh` 已内置降级：`git push` 失败后自动调用 `scripts/push_via_api.py`，用 `git credential fill` 取本地凭据走 GitHub REST API 推送（支持二进制 mp3），再 `git reset --soft` 对齐本地。不要删这个兜底：实测过 git push 连续 14 次 502、API 一次成功的场景。

## 第八步：交付与验证（强制门禁，未通过不算交付完成）

**这一步是硬性门禁，不是建议。** 每次交付前必须实际执行下列验证命令并确认输出，禁止仅凭"脚本写了应该没问题"就交付——v1.0 的热搜站正是因为跳过这步，交付了一个播客按钮点了没反应的半成品，几天后才被发现。

先跑统一样机脚本（随包附带，按档位自检）：

```bash
bash scripts/verify_delivery.sh <档位 1|2|3> [站点根目录]
```

脚本会检查：页面存在且 `SITE_CFG.podcast` 与档位一致、数据文件齐全；档位 3 还会实际调用一次音频脚本生成当天音频、检查 `manifest.json` 有条目、重建 feed 并校验 enclosure 文件存在。**脚本报 FAIL 就必须修到 PASS 才能交付。**

交付后再做人工确认：

- 档位 1：给出 HTML 路径，双击打开确认页面正常、无播客按钮。
- 档位 2：发布链接 + 说明如何手动更新或在 WorkBuddy 建定时任务；确认页面无播客按钮。
- 档位 3：固定站点地址 + RSS 订阅地址 + 让用户在播客 App 里订阅测试的 steps；确认页面有播客按钮且能播放、feed 的 enclosure 链接线上返回 200 且 `Content-Type` 为 `audio/*`、定时 workflow 语法正确且触发键包含 schedule/push/workflow_dispatch。

**档位与功能一致性复述**：交付时用"你想要的结果"向用户确认本档位包含/不包含哪些功能（尤其档位 1/2 明确告知"本站在文字模式，不含播客/订阅；想要能听能订阅可随时升级到档位 3"），让用户预期与实际交付一致。

## 参考资源

- `assets/site.config.example.json` — 站点配置样例（所有可变参数的单一来源）
- `assets/dashboard-template.html` — 单文件仪表盘模板（已参数化，顶部 `SITE_CFG` 一处替换）
- `assets/daily-podcast.yml` — GitHub Actions 基线（含多重防线）
- `scripts/common.py` — 公共模块：配置读取 + 数据契约解析
- `scripts/gen_audio.py` — 双语音频生成（配置驱动）
- `scripts/gen_feed.py` — RSS 生成（配置驱动）
- `scripts/ensure_today.sh` — 定时兜底检查（WorkBuddy 定时任务用；git push 失败自动降级 API）
- `scripts/push_via_api.py` — GitHub REST API 推送助手（github.com 被代理阻断时的兜底）
- `scripts/verify_delivery.sh` — 交付前强制自检脚本（按档位验证，第八步门禁）
- `references/data-contract.md` — 数据契约 + aihot / 本地 JSON 适配示例

> 资源状态：以上 bundled 资源均已从参考项目 `ai-news-dashboard` 抽取并完成参数化（2026-11-22）。脚本已通过冒烟测试、陌生主题 E2E 实测与功能 A/B 基准（带 skill 100% vs 裸模型 30%），本 SKILL.md 通过 skill-creator 结构校验，已打包为 `.skill` 可直接安装。
>
> 代用户生成站点时的操作顺序：
> 1. 把 `assets/site.config.example.json` 复制为站点根目录的 `site.config.json`，按用户填写。字段分组：`site_name`/`brand_line`/`site_desc`/`site_url`/`data_credit` 是品牌；**`podcast` 是档位总开关（档位 3=true，档位 1/2=false，须与 `index.html` 顶部 `SITE_CFG.podcast` 一致）**；`data_mode`（`aihot`|`local`）+ `api_base`/`local_data_dir` 是数据源；`voice_zh`/`voice_en`/`keep_days` 是音频；`podcast_category`/`podcast_author`/`max_episodes` 是 RSS；`pub_hour`/`cron_minutes`/`fallback_hour`/`fallback_minute` 是上线时间（北京时间）。
> 2. 把 `assets/dashboard-template.html` 复制为 `index.html`，按 `site.config.json` 替换文件顶部的 `SITE_CFG` 对象。**注意 `data_mode` 要写成 SITE_CFG 的 `dataMode` 字段**——`local` 模式必须做三处页面改造，完整配方见 `references/data-contract.md` 的「local 模式」小节（E2E 实测验证过，别漏 `data/index.json`）。
> 3. 复制 `scripts/` 到站点根目录同级；复制 `assets/daily-podcast.yml` 到 `.github/workflows/daily-podcast.yml`，按第七步的换算规则把 `pub_hour`/`cron_minutes` 换成 UTC cron 行（模板里示例是 8 点的，**不是所有站点都照抄**）。
> 4. 档位 3 另需在 WorkBuddy 建定时任务调用 `scripts/ensure_today.sh`（用配置的 `fallback_hour/minute`）。
> 5. 用示例/当天数据跑一遍脚本验证，再交付。

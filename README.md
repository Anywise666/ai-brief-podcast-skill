# AI 简报播客站生成器（ai-brief-podcast）

把「一份每天更新的简报」变成一个**可以看的网页**、**可以听的中英双语播客**、**可以订阅的 RSS 节目**，并配好每日自动更新。

你只需说清内容来源、主题名称和发布方式，剩下的交给这个 skill：单文件 HTML 仪表盘、中英双语 mp3、RSS 订阅源、GitHub Actions 定时上线，以及一整套踩过坑才有的容错处理。

> 这个 skill 的价值不在生成 HTML（那只是模板），而在把一条已经验证过的完整链路交付给用户：**数据 → 页面 → 音频 → RSS → 定时上线**，以及沿途那些踩过坑才有的容错处理。

## 三档交付（默认推荐最低档）

| 档位 | 交付内容 | 用户需要准备 | 适合 |
|---|---|---|---|
| 1 · 本地站 | 单文件 HTML，双击可看 | 一个浏览器 | 零门槛、先看效果 |
| 2 · 在线站 | HTML 托管到 GitHub Pages，可分享链接 | GitHub 账号 | 想发给别人看 |
| 3 · 可订阅站 | 在线站 + 双语播客 mp3 + RSS feed + 每日自动更新 | GitHub 账号 + token + 数据源 | 想让人用播客 App 订阅 |

## 目录结构

```
SKILL.md                          完整工作流（三档分级 + 8 步 + 排障经验）
README.md                         本文件
assets/site.config.example.json   站点配置样例（单一参数源）
assets/dashboard-template.html    参数化单文件仪表盘
assets/daily-podcast.yml          GitHub Actions 基线（多重触发防线）
scripts/common.py                 配置 + 数据契约公共模块
scripts/gen_audio.py              双语音频生成（edge-tts）
scripts/gen_feed.py               RSS 生成
scripts/ensure_today.sh           定时兜底检查
references/data-contract.md       数据契约 + 两种数据源适配示例
evals/                            触发率与功能 A/B 评测资产（迭代用）
listing/                          WorkBuddy 灵感社区上架材料与文案
```

## 安装

### 方式一：在 WorkBuddy 里安装（推荐）

在 WorkBuddy 灵感社区搜索「AI 简报播客站生成器」，点安装；或下载 release 里的 `.skill` 包导入。

### 方式二：作为本地 skill 使用

把本仓库 clone 到用户级技能目录：

```bash
git clone https://github.com/Anywise666/ai-brief-podcast-skill.git ~/.workbuddy/skills/ai-brief-podcast
```

重启 WorkBuddy 或新开任务即可识别。

## 调用

- **自动触发**：直接用大白话说需求，如「帮我做一个光伏行业晨报网站，能听能订阅」。skill 的 `description` 里写了触发词（晨报网站 / 新闻播客 / 日报仪表盘 / 把文章变成播客 等），WorkBuddy 会自动加载。
- **显式指定**：`@skill:ai-brief-podcast` 后接需求，确保一定走这个 skill。

调用后会先确认三个关键输入：**内容来源、站点名称、发布方式**（能从上下文推断的就不问），再按技术能力分档交付。

## 数据源

支持两种模式，配置集中在 `site.config.json`：

- `aihot` 模式：拉取 aihot.news 公开日报接口，适合 AI 类日报。
- `local` 模式：读本地 `data/<date>.json` + `data/index.json`，可适配任意数据源（详见 `references/data-contract.md`）。

## 质量验证

| 项 | 结果 |
|---|---|
| 结构校验 | skill-creator `quick_validate` 通过 |
| 触发率评测 | 20/20 = 100%（80 次独立判定，near-miss 全对） |
| 功能 A/B | 带 skill 100% vs 裸模型 30%（Delta +0.70） |
| E2E | 陌生主题「光储晨报」从零复现成功，并修复 3 个文档缺陷 |

## 外部依赖与免责

- `edge-tts`（微软非官方 TTS 接口）与 `aihot.news`（第三方数据源）均为外部依赖，任一变动可能影响功能。
- 本 skill 交付的是「方法论 + 自动化脚本」，用户仍需自备 GitHub 账号 / token（档位 3）与数据源。

## License

MIT

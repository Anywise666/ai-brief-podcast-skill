# AI 简报播客站生成器 · 上架准备包

本目录是把 skill `ai-brief-podcast` 上架到 **WorkBuddy 灵感社区** 的全部准备材料。
状态（2026-11-22）：**技能本体已提交审核**（技能 ID `os_4553ac6add300c57`，审核中最晚 12-01），社区作品草稿待技能通过后发布。社区作品文案已按检索优化重写，见 `listing-draft.json`。

---

## 一、上架渠道与机制

- 渠道：WorkBuddy 灵感社区，通过创作发布接口提交。
- 机制：创建作品后进入 `pending` 待审，审核通过才公开可见；被拒（`rejected`）可编辑重审；正常态可自主下架。
- 参照样本：官方「自定义 Skill 开发教程」（`cnb-custom-skill-development`），分类 `智能体能力 / 开发工具`，`creationKind=1`。

## 二、文案（可直接用，见 listing-draft.json）

> 2026-11-22 按社区检索机制重写文案，提升被搜索到的概率。平台全文检索命中「标题+副标题+描述+prompt」四字段；描述内 `#{话题}` 命中可见话题会自动收录。对标官方爆款「今日 AI 日报一键生成」（使用 856 次），其做法是在描述里明写"触发关键词"句、副标题塞高频词、分类选「信息与资讯+办公协同」。本技能差异化是"播客+订阅"（搜"播客"仅 77 条，竞争小于"日报"203 条），文案已放大该点。

| 字段 | 优化后内容摘要 |
|---|---|
| 标题 | AI 日报/晨报一键生成播客站：网页能看、双语能听、RSS 可订阅，每日自动上线（高频词前置） |
| 副标题 | 一句话做出可看·可听·可订阅的行业晨报站，中英双语播客+RSS+每日自动更新，小白零门槛 |
| 描述 | 讲清做什么/适合谁/三档分级；新增「触发关键词：AI 日报 / 晨报网站 / 新闻播客 / 日报仪表盘 / 把文章变成播客」；话题标签改为 `#{播客} #{日报} #{自动化}`（去掉存疑的 `#{skill}`） |
| prompt（别人点"使用"时填入的引导语） | 改为 6 条可复制即跑的完整指令（HTML 看板/五版块编号/双语音频/RSS/自动更新/三档交付） |
| 分类 | 信息与资讯、办公协同（真实流量类目，非样本的"智能体能力/开发工具"） |
| creationKind | 1 |
| 语言 | zh（另附英文 translations，覆盖英文搜索） |
| 预览 | previewUrl = 在线成品站 https://anywise666.github.io/ai-news-dashboard/；artifacts 加了在线演示链接 |

## 三、待办卡点（需你在平台侧完成，我无对应工具）

1. **`assetRef`（关键）**：可安装 skill 的资产 ID，形如 `skill_2053082698440450048`。
   必须先把代码包上传到平台、由平台生成该 ID，才能填进 `assets[].assetRef`；
   没有它，作品能被看见但不能"一键安装"。
   - **入口已确认（2026-11-22）**：WorkBuddy 客户端左侧菜单 →「技能」→「发布技能」→ 第①步"配置技能"，
     上传 `ai-brief-podcast-skill.zip`（页面仅支持 zip，≤30MB；`.skill` 本质是 zip，已另存一份标准 `.zip`）。
   - 上传后第②步"确认信息"里填标题/描述/封面（用 `cover.png`），第③步"提交审核"。
   - 发布通过后平台分配的资产 ID 即 `assetRef`，回填 `listing-draft.json`。
   - 若发布遇阻，可退而求其次：不填 `assets`，把 `.skill` 作为附件（artifact）提供下载安装。
2. **封面图**：`coverUrl` 需是先上传得到的最终 URL。已用 AI 生成横版封面 `cover.png`（1536×1024），
   需通过上传凭证传到平台资源位后拿到 `finalUrl`。
3. **附件 URL**：SKILL.md、README、data-contract.md 同样需上传后填 `finalUrl`。

## 四、上架前已完成的质量准备

- 结构校验通过（skill-creator `quick_validate`）。
- 触发率评测 20/20=100%（80 次独立判定，near-miss 全对）→ description 维持原样。
- 功能 A/B 基准：带 skill 100% vs 裸模型 30%（Delta +0.70）。
- E2E：陌生主题「光储晨报」从零复现成功，并修复 3 个文档缺陷。
- 已清理 SKILL.md 里过时的"待抽取/待补"状态标注，避免误导安装者。

## 五、发布包内容（ai-brief-podcast-skill.skill，约 41KB）

```
SKILL.md                          完整工作流（三档分级 + 8 步 + 排障经验）
assets/site.config.example.json   站点配置样例（单一参数源）
assets/dashboard-template.html    参数化单文件仪表盘
assets/daily-podcast.yml          GitHub Actions 基线（四重防线）
scripts/common.py                 配置 + 数据契约公共模块
scripts/gen_audio.py              双语音频生成
scripts/gen_feed.py               RSS 生成
scripts/ensure_today.sh           定时兜底检查
references/data-contract.md       数据契约 + 两种数据源适配示例
```

> eval 资产（evals/）按 skill-creator 规范不随发布包分发，仅在源目录保留供迭代复现。

## 六、推荐发布步骤

1. 在 WorkBuddy 导入 `.skill`，拿到平台的 `assetRef`。
2. 上传 `cover.png` 拿封面 `finalUrl`；上传 SKILL.md / README / data-contract 拿附件 `finalUrl`。
3. 用 `listing-draft.json` 的文案，填好 `assetRef` 与各 `finalUrl`。
4. 提交创作 → 进入 pending → 等待审核。
5. 审核通过后如需下架/重上架，用对应平台操作。

## 七、外部依赖与免责（建议写进商品详情或 README）

- edge-tts 为微软非官方接口、aihot.news 为第三方数据源，任一变动可能影响功能。
- skill 交付的是"方法论 + 自动化脚本"，用户仍需自备 GitHub 账号/token（档位 3）与数据源。

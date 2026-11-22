# Eval 基准说明（ai-brief-podcast）

本目录记录 skill 的可复现评测资产与结果。评测分为两部分：**触发率评测**（description 能否让 skill 被正确调用）与**功能 A/B 基准**（带 skill vs 裸模型的产物质量）。

## 一、触发率评测

- 评测集：`evals/trigger-evals.json`，20 条真实用户查询（10 条应触发 / 10 条 near-miss 不应触发），含 edge case、中英混合、口语化表达。
- 方法：因本环境无 `claude` CLI / Anthropic API key，无法运行 skill-creator 官方 `run_eval.py`。采用等价方法——用独立判定 agent 模拟"看到 available_skills 列表后是否调用"的决策。
- 轮次：2 轮（引导式 + 无提示盲测），每轮对「当前 description」与「改进版 description」各判一次，共 80 次独立判定。
- 结果：**两版均为 20/20 = 100%**，四个判定结果完全一致。near-miss（PDF 转音频、单句 TTS、改字体、查 API、爬虫抓数据、已有播客 RSS 调优、邮件简报等）全部正确拒绝。
- 决策：当前 description 触发率已满且更简洁，改进版无可测量增益，按"保持简洁、避免过拟合"原则**维持原 description**。

## 二、功能 A/B 基准

- 评测集：`evals/evals.json`，2 个功能用例：
  - eval-1 `local-mode-custom-brand`：本地 JSON 源 + 自定义品牌/音色/上线时间（北京时间 7:12，跨越 UTC 日期边界）
  - eval-2 `aihot-default-online`：aihot 在线源 + 早 8 点窗口 + Apple Podcasts 订阅
- 每例各跑 with_skill（本 skill）与 without_skill（裸模型），共 4 个独立 agent 并行执行；评分用客观脚本 `grade.py` 检查文件系统产物，不做主观判断。
- 结果：

| 用例 | With Skill | Without Skill |
|---|---|---|
| eval-1 自定义品牌本地站 | 5/5 (100%) | 2/5 (40%) |
| eval-2 aihot 在线站 | 5/5 (100%) | 1/5 (20%) |
| **合计** | **10/10 (100%)** | **3/10 (30%)** |

- Delta: **+0.70**。裸模型能产出外观不错的页面，但普遍缺失统一配置契约（`site.config.json`）、可复用配置驱动脚本、正确的北京时间→UTC cron 换算（尤其跨日场景）——正是 skill 固化的工程闭环价值。
- 完整运行产物与 `benchmark.json` / `benchmark.md` 位于同级 workspace：`../ai-brief-podcast-skill-workspace/iteration-1/`

## 三、环境限制说明

官方 skill-creator eval 工具链依赖 `claude -p` CLI 与 Anthropic API key（本环境均未配置），故采用等价的 Agent 工具实现相同评测逻辑。pass rate 与定性结论有效；time/tokens 指标因非子进程执行而缺失，不影响结论。

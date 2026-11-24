# 发版说明（Release Guide）

这份文档说明如何把本仓库打包成可分发的 `.skill`，并发布为 GitHub Release 和灵感社区更新。

## 一、版本号规则

版本号写在 **`SKILL.md` frontmatter 的 `version:` 字段**（如 `1.0.0`），它同时决定打包文件名。遵循语义化版本：

| 变更类型 | 递增位 | 例子 |
|---|---|---|
| 修文档错字、补注释 | patch | 1.0.0 → 1.0.1 |
| 新增功能/新档位/适配新数据源 | minor | 1.0.0 → 1.1.0 |
| 工作流或数据契约破坏性改动 | major | 1.0.0 → 2.0.0 |

发版前先改 `SKILL.md` 的 `version`，提交，再走下面流程。

## 二、打包（生成 .skill / .zip）

一条命令：

```bash
python scripts/build_skill.py
```

产出到 `dist/`：

```
dist/ai-brief-podcast-skill-v1.0.0.skill   # 灵感社区/本地导入用
dist/ai-brief-podcast-skill-v1.0.0.zip     # 平台上传用（部分页面只收 zip）
```

两个文件内容完全相同——`.skill` 本质就是 zip，只是扩展名不同。

### 打包配方（脚本已固化，此处备查）

- **包含**：`SKILL.md`、`assets/`、`references/`、`scripts/`（构建脚本自身除外）
- **排除**：`evals/`（评测资产，终端用户不需要）、`listing/`（上架文案）、`README.md`、`.gitignore`
- **包内顶层目录**：`ai-brief-podcast-skill/`
- **文本统一 LF 行尾**：保证 Windows/Linux/Mac 打包结果一致

### 为什么不用 skill-creator 自带的 package_skill.py

发布包必须在 SKILL.md frontmatter 带上平台要求的五个字段：`version` / `display_name` / `display_name_en` / `description_zh` / `description_en`。而 skill-creator 本地的 `quick_validate` 白名单不含这些字段，会判为 `unexpected key` 并拒绝打包。**以平台要求为准，用本仓库的标准库脚本打包**，不要改用官方打包器。

## 三、发版前检查清单

```bash
python scripts/build_skill.py          # 打包
python -c "import zipfile; z=zipfile.ZipFile('dist/ai-brief-podcast-skill-v1.0.0.skill'); print(z.testzip()); print(len(z.namelist()),'files')"
```

- [ ] `SKILL.md` 的 `version` 已按规则递增并已提交
- [ ] 打包脚本输出 9 个文件、`testzip()` 返回 `None`
- [ ] 包内 SKILL.md 的五个平台字段齐全
- [ ] 触发率评测仍通过（改动 description 时必须重跑 `evals/`）
- [ ] `git status` 干净，`dist/` 已在 `.gitignore` 忽略（不入库）

## 四、发布到 GitHub Release

仓库：`https://github.com/Anywise666/ai-brief-podcast-skill`

**方式 A — 网页（推荐）**：仓库页 → Releases → Draft a new release → 选/建 tag `v1.0.0` → 填标题和变更说明 → 上传 `dist/` 里的 `.skill` 和 `.zip` → Publish。

**方式 B — 命令行**：本机无 `gh` CLI，用 API（凭证从本地 git 取，不回显）：

```bash
TOKEN=$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill 2>/dev/null | grep '^password=' | cut -d= -f2-)
curl -s -X POST -H "Authorization: token $TOKEN" \
  https://api.github.com/repos/Anywise666/ai-brief-podcast-skill/releases \
  -d '{"tag_name":"v1.0.0","name":"v1.0.0","body":"变更说明","draft":false,"prerelease":false}'
# 然后按返回的 upload_url 上传 dist/ 里的两个产物
```

README 里的安装说明指向 release 附件，发版后确认链接可下载。

## 五、发布到灵感社区（如适用）

技能本体审核通过后，若功能有实质更新：

1. 用新打的 `.zip` 覆盖平台上的技能包，重新提交审核（**才会改变用户安装到的版本**）。
2. 社区作品（标题/描述/话题）与技能包是两层：只改文案不需要重传包；改了功能才需要重传。

技能 ID / 资产 ID 记在 `listing/README-上架说明.md`，回填字段名见 `listing/listing-draft.json`。

## 六、历史版本

每次发版的 tag 和附件都留在 GitHub Releases，可随时回退。

| 版本 | 说明 |
|---|---|
| v1.1.0 | 功能与档位严格对应（档位 1/2 纯文字、不露播客入口）；`SITE_CFG.podcast` 总开关；`verify_delivery.sh` 交付强制门禁；`push_via_api.py` 推送兜底；兜底脚本数据就绪重试 + git/API 双通道 |
| v1.0.1 | 搜索优化（展示名/描述/触发词）+ 图标素材，无功能变更 |
| v1.0.0 | 初始版本，含三档交付 + 双语播客 + RSS + 定时兜底 + 完整评测 |

当前最新：**v1.1.0**。

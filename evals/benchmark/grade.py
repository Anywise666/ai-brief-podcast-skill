#!/usr/bin/env python3
"""客观评分器：按 evals.json 的 expectations 检查各 run 的产物文件系统。"""
import os, json, re, sys
from pathlib import Path

W = Path("D:/Python Work/AI汇报/ai-brief-podcast-skill-workspace/iteration-1")

def read(p):
    try: return Path(p).read_text(encoding="utf-8")
    except Exception: return ""

def all_files(root):
    out = []
    for dp, _, fs in os.walk(root):
        for f in fs: out.append(os.path.join(dp, f))
    return out

def find(root, name):
    """按文件名（含扩展名）在 root 下递归找第一个匹配路径。"""
    for p in all_files(root):
        if os.path.basename(p) == name: return p
    return None

def has(root, name): return find(root, name) is not None

def grade_eval1(root):
    cfg_p = find(root, "site.config.json")
    cfg = read(cfg_p) if cfg_p else ""
    idx_p = find(root, "index.html")
    idx = read(idx_p) if idx_p else ""
    wf = ""
    for p in all_files(root):
        if p.endswith(("daily-podcast.yml", ".github/workflows/daily-podcast.yml")) or "workflow" in p.replace("\\","/") and p.endswith((".yml",".yaml")):
            wf += read(p)
    ga = find(root, "gen_audio.py"); gf = find(root, "gen_feed.py")
    ga_txt = read(ga) if ga else ""

    checks = []
    # E1-1: site.config.json local 模式 + 光储晨报
    ok1 = bool(cfg) and '"local"' in cfg and ('光储晨报' in cfg or '光储' in cfg)
    checks.append(("生成 site.config.json，data_mode=local 且品牌含光储晨报", ok1,
                   f"cfg存在={bool(cfg)}, local={'local' in cfg}, 品牌={'光储' in cfg}"))
    # E1-2: index.html SITE_CFG 品牌注入且无 AI 晨报/aihot 残留
    brand_ok = '光储晨报' in idx
    residue = ('AI 晨报' in idx) or ('aihot.news' in idx)
    ok2 = bool(idx) and brand_ok and not residue
    checks.append(("index.html 注入光储晨报且无 AI晨报/aihot 残留", ok2,
                   f"品牌注入={brand_ok}, 残留={'AI 晨报' in idx or 'aihot.news' in idx}"))
    # E1-3: 音色 YunxiNeural
    ok3 = 'YunxiNeural' in cfg or 'YunxiNeural' in idx
    checks.append(("音色为 zh-CN-YunxiNeural", ok3, f"YunxiNeural出现={ok3}"))
    # E1-4: cron 按北京7:12 = UTC 23:12
    ok4 = bool(re.search(r"23\s+12|\b12\s+23\b", wf)) and bool(wf)
    checks.append(("workflow cron 按北京时间7:12(UTC 23:12)换算", ok4, f"找到23:12或12 23={ok4}, wf长度={len(wf)}"))
    # E1-5: 配置驱动的 gen_audio/gen_feed
    ok5 = bool(ga) and bool(gf) and ('config' in ga_txt.lower() or 'common' in ga_txt.lower())
    checks.append(("scripts 含配置驱动的 gen_audio.py 与 gen_feed.py", ok5,
                   f"gen_audio={bool(ga)}, gen_feed={bool(gf)}, 配置驱动={'config' in ga_txt.lower() or 'common' in ga_txt.lower()}"))
    return checks

def grade_eval2(root):
    cfg_p = find(root, "site.config.json")
    cfg = read(cfg_p) if cfg_p else ""
    idx_p = find(root, "index.html")
    idx = read(idx_p) if idx_p else ""
    wf = ""
    for p in all_files(root):
        if p.endswith((".yml", ".yaml")):
            wf += read(p)
    ga = find(root, "gen_audio.py"); gf = find(root, "gen_feed.py")

    checks = []
    # E2-1: aihot 模式 + api_base
    ok1 = bool(cfg) and 'aihot' in cfg and 'aihot.news' in cfg
    checks.append(("site.config.json data_mode=aihot 且 api_base 指向 aihot.news", ok1,
                   f"cfg存在={bool(cfg)}, aihot={'aihot' in cfg}, url={'aihot.news' in cfg}"))
    # E2-2: index.html 保留 aihot 在线取数 BASE + SITE_CFG
    ok2 = bool(idx) and ('fetchJson' in idx or 'aihot.news' in idx) and 'SITE_CFG' in idx
    checks.append(("index.html 保留 aihot 在线取数且 SITE_CFG 完整", ok2,
                   f"fetchJson/aihot={'fetchJson' in idx or 'aihot.news' in idx}, SITE_CFG={'SITE_CFG' in idx}"))
    # E2-3: cron 落早8点窗口 UTC 00:xx
    ok3 = bool(re.search(r"\b0[0-9]?\s+0\s+\*\s+\*\s+\*", wf)) or ("00:" in wf) or bool(re.search(r"'\d{1,2} 0 \* \* \*'", wf))
    checks.append(("workflow cron 落在北京时间早8点窗口(UTC 00:xx)", ok3, f"匹配UTC00点={ok3}, wf长度={len(wf)}"))
    # E2-4: gen_audio/gen_feed
    ok4 = bool(ga) and bool(gf)
    checks.append(("scripts 含 gen_audio.py 与 gen_feed.py", ok4, f"gen_audio={bool(ga)}, gen_feed={bool(gf)}"))
    # E2-5: 三要素 HTML+音频脚本+RSS
    feed_exists = has(root, "feed.xml") or gf is not None
    ok5 = bool(idx) and bool(ga) and feed_exists
    checks.append(("产物含三要素:HTML仪表盘+双语音频脚本+RSS能力", ok5,
                   f"HTML={bool(idx)}, 音频={bool(ga)}, RSS={feed_exists}"))
    return checks

def main():
    result = {}
    for eid, grader in [(1, grade_eval1), (2, grade_eval2)]:
        for cfg in ("with_skill", "without_skill"):
            root = W / f"eval-{eid}" / cfg / "outputs"
            checks = grader(root)
            passed = sum(1 for _, ok, _ in checks if ok)
            key = f"eval{eid}_{cfg}"
            result[key] = {
                "passed": passed, "total": len(checks),
                "pass_rate": round(passed/len(checks), 3),
                "checks": [{"text": t, "passed": ok, "evidence": ev} for t, ok, ev in checks],
            }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # 写 grading.json 到各 run 目录
    for key, v in result.items():
        eid = 1 if "eval1" in key else 2
        cfg = "with_skill" if "with_skill" in key else "without_skill"
        gd = W / f"eval-{eid}" / cfg
        json.dump({"expectations": v["checks"],
                   "summary": {"passed": v["passed"], "failed": v["total"]-v["passed"],
                               "total": v["total"], "pass_rate": v["pass_rate"]}},
                  open(gd/"grading.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

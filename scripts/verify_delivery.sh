#!/usr/bin/env bash
# 交付前强制自检（v1.1.0 新增）：按档位验证站点交付是否完整、功能与档位是否一致。
# v1.0 的真实故障：档位1/2 页面露出播客按钮却没生成音频，点了没反应，几天后才被发现。
# 本脚本把「交付前跑一遍」变成可执行的门禁：FAIL 必须修到 PASS 才能交付。
#
# 用法： bash verify_delivery.sh <档位 1|2|3> [站点根目录，默认当前目录]
# 输出： PASS <档位> ... / FAIL <原因>，最后一行给出退出码语义（PASS=0）。
set -uo pipefail

TIER="${1:-}"
WORK="${2:-.}"
WORK=$(cd "$WORK" && pwd)
FAIL=0
fail(){ echo "FAIL $*"; FAIL=1; }
pass(){ echo "PASS $*"; }

case "$TIER" in
  1|2|3) ;;
  *) echo "FAIL 档位参数必须是 1|2|3（收到: '${TIER}'）"; exit 1 ;;
esac

cd "$WORK" || { echo "FAIL 无法进入站点目录 $WORK"; exit 1; }
echo "=== 交付自检 档位 $TIER | $WORK ==="

# ---- 通用：页面存在 ----
[ -f index.html ] || fail "缺少 index.html"
[ -s index.html ] || fail "index.html 为空"

# ---- 数据文件 ----
[ -d data ] || fail "缺少 data/ 目录"
if [ -d data ]; then
  n=$(ls data/20*.json 2>/dev/null | wc -l)
  [ "$n" -ge 1 ] || fail "data/ 下无日期报告文件（data/20*.json）"
  [ -f data/index.json ] || fail "缺少 data/index.json（日历/历史依赖）"
  echo "  数据文件: $n 个日期报告"
fi

# ---- 播客开关与档位一致性 ----
# 从 index.html 的 SITE_CFG 读取 podcast 值（模板已参数化，默认 false）
podcast_val=$(python -c "
import re,sys
s=open('index.html',encoding='utf-8').read()
m=re.search(r'var\\s+SITE_CFG\\s*=\\s*\{', s)
if not m:
    print('MISSING'); sys.exit(0)
seg=s[m.end():m.end()+2000]
pm=re.search(r'podcast\\s*:\\s*(true|false)', seg)
print(pm.group(1) if pm else 'DEFAULT_FALSE')
" 2>/dev/null || echo "ERR")
echo "  SITE_CFG.podcast = $podcast_val"

has_audio=0
[ -d audio ] && has_audio=$(ls -d audio/20* 2>/dev/null | wc -l)
has_feed=0
[ -s feed.xml ] && has_feed=1

if [ "$TIER" = "3" ]; then
  [ "$podcast_val" = "true" ] || fail "档位3 要求 SITE_CFG.podcast=true（当前=$podcast_val）"
  # 实际跑一次音频生成，确认整条链路能跑通
  echo "  档位3：实跑音频生成 ..."
  python scripts/gen_audio.py 2>&1 | tail -3
  [ "${PIPESTATUS[0]}" = "0" ] || fail "gen_audio.py 执行失败"
  TODAY=$(python -c "from datetime import datetime,timedelta,timezone; print(datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'))")
  m="audio/$TODAY/manifest.json"
  [ -s "$m" ] || fail "档位3 缺少当天 manifest.json（音频未生成）: $m"
  if [ -s "$m" ]; then
    cnt=$(python -c "
import json
d=json.load(open('$m',encoding='utf-8'))
items=d.get('items') or {}
print(sum(1 for v in items.values() if isinstance(v,dict) and (v.get('zh') or v.get('en'))))
" 2>/dev/null || echo 0)
    [ "$cnt" -ge 1 ] || fail "manifest.json 无任何有效音轨"
    echo "  当天音轨条目: $cnt"
  fi
  echo "  档位3：重建 feed ..."
  python scripts/gen_feed.py 2>&1 | tail -2
  [ -s feed.xml ] || fail "档位3 缺少 feed.xml"
  grep -q "<enclosure" feed.xml || fail "feed.xml 无 enclosure 节点"
  echo "  feed 期数: $(grep -c '<item>' feed.xml)"
else
  # 档位 1/2：播客必须关闭，且不应有播客产物
  if [ "$podcast_val" = "true" ]; then
    fail "档位$TIER 但 SITE_CFG.podcast=true —— 页面会露出播客按钮却无音频（半成品）"
  fi
  [ "$has_audio" = "0" ] || fail "档位$TIER 不应存在 audio/ 音频目录（发现 $has_audio 个日期目录）"
  [ "$has_feed" = "0" ] || fail "档位$TIER 不应存在 feed.xml"
  if [ "$FAIL" = "0" ]; then pass "档位$TIER 纯文字模式：无播客开关、无音频、无 feed"; fi
fi

if [ "$FAIL" = "0" ]; then
  pass "档位 $TIER 交付自检全部通过"
else
  echo "请修复上述 FAIL 项后重新运行，全部 PASS 才算交付完成。"
fi
exit "$FAIL"

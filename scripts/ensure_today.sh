#!/usr/bin/env bash
# 简报播客「本机兜底主力」：检查线上当天音频是否存在，缺失则本地补跑并推送。
# 由 WorkBuddy 定时任务在目标上线时段调用（时间见 site.config.json 的 fallback_*）。
# 事实源：线上 audio/YYYY-MM-DD/brief_zh.mp3 的 HTTP 状态。
# 推送：git push（HTTP/1.1 + 重试）优先，失败自动降级 GitHub REST API（push_via_api.py）。
set -uo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
WORK=$(cd "$SCRIPT_DIR/.." && pwd)
cd "$WORK" || { echo "PUSH_FAILED 无法进入站点目录"; exit 1; }
# 用相对路径读取配置：避免 Git Bash 的 /d/... 路径传给 Windows Python 无法识别
SITE=$(python -c "import json; c=json.load(open('site.config.json',encoding='utf-8')); print(c.get('site_url','').rstrip('/'))")
if [ -z "$SITE" ]; then echo "PUSH_FAILED site_url 未配置"; exit 1; fi

TODAY=$(python -c "from datetime import datetime,timedelta,timezone; print(datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'))")
CHECK_URL="$SITE/audio/$TODAY/brief_zh.mp3"
echo "=== 简报兜底检查: $TODAY ==="
echo "检查线上音频: $CHECK_URL"

status=$(curl -sL -o /dev/null -w "%{http_code}" --max-time 20 "$CHECK_URL" || echo "000")
echo "HTTP 状态: $status"
if [ "$status" = "200" ]; then
  echo "ALREADY_OK 当天音频已在线，无需补跑"
  exit 0
fi

echo "当天音频缺失，开始本地补跑 ..."

# 1) 数据就绪等待：数据源偶发延迟时不要一次扑空就放弃（最多 5 次 × 60s）
GEN_LOG=$(mktemp 2>/dev/null || echo /tmp/_ga_$$.log)
for i in 1 2 3 4 5; do
  python "$SCRIPT_DIR/gen_audio.py" "$TODAY" 2>&1 | tee "$GEN_LOG"
  if grep -q "该日期无 report" "$GEN_LOG"; then
    echo "  数据未就绪，等待重试 $i/5 ..."; sleep 60
  else
    break
  fi
done
rm -f "$GEN_LOG"
[ -s "audio/$TODAY/manifest.json" ] || { echo "GEN_FAILED"; exit 1; }
python "$SCRIPT_DIR/gen_feed.py" || { echo "FEED_FAILED"; exit 1; }

# 2) 提交音频与 feed
git add "audio/$TODAY" feed.xml
if git diff --cached --quiet; then
  echo "NO_CHANGES_SKIP 生成后无变化"
  exit 0
fi
git commit -m "Fallback podcast audio + feed: $TODAY (local)" >/dev/null 2>&1 || true

# 3) 推送：git 优先（HTTP/1.1 + 重试），失败降级 GitHub API
pushed=0
for i in 1 2 3; do
  out=$(GIT_HTTP_VERSION=HTTP/1.1 git push origin HEAD:main 2>&1)
  echo "  git push try $i: $(echo "$out" | tail -1)"
  if echo "$out" | grep -qE "up-to-date|HEAD -> main|main -> main"; then pushed=1; break; fi
done
if [ "$pushed" != "1" ]; then
  echo "git push 不通，降级 GitHub API ..."
  api_out=$(python "$SCRIPT_DIR/push_via_api.py" 2>&1)
  echo "  $api_out"
  if echo "$api_out" | grep -qE "PUSH_OK|NO_CHANGES"; then pushed=1; fi
fi
if [ "$pushed" != "1" ]; then echo "PUSH_FAILED 推送未成功"; exit 1; fi

# 4) 复核上线
for i in $(seq 1 15); do
  sleep 6
  s=$(curl -sL -o /dev/null -w "%{http_code}" --max-time 15 "$CHECK_URL" || echo "000")
  echo "复核 $i: HTTP $s"
  if [ "$s" = "200" ]; then echo "PUSH_OK 当天音频已上线: $CHECK_URL"; exit 0; fi
done
echo "PUSH_OK_PENDING Pages 部署延迟，稍后请手动复核"
exit 0

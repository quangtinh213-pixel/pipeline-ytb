#!/usr/bin/env bash
# Render một bản dựng HyperFrames ra MP4. Dùng: scripts/render.sh <composition_dir> <out.mp4> [draft|delivery]
set -euo pipefail
here=$(cd "$(dirname "$0")/.." && pwd)
dir=$1; mkdir -p "$(dirname "$2")"; out=$(cd "$(dirname "$2")" && pwd)/$(basename "$2"); q=${3:-delivery}
cd "$dir"
hf=/tmp/hf-check-$$.txt
rc=0; npx hyperframes check >"$hf" 2>&1 || rc=$?
# cổng: check phải thoát 0, có dòng "Check passed" và không có ✗; check crash (thiếu dòng pass) cũng dừng
if [ "$rc" -ne 0 ] || grep -q "✗" "$hf" || ! grep -q "Check passed" "$hf"; then
  grep "✗" "$hf" || tail -20 "$hf" >&2 || true
  echo "check có lỗi (thoát $rc), dừng render" >&2; exit 1
fi
# tham số mã hóa: HF_RENDER_ARGS (kể cả rỗng) thắng cấu hình; không đặt thì lấy config.json:render
args=${HF_RENDER_ARGS-$(cd "$here" && uv run python -m tttc.dung render-args 2>/dev/null || true)}
npx hyperframes render --output "$out" --quality "$q" --fps 30 --skill hyperframes --quiet $args
echo "$out"

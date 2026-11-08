#!/usr/bin/env bash
# Render một bản dựng HyperFrames ra MP4. Dùng: scripts/render.sh <composition_dir> <out.mp4> [draft|delivery]
set -euo pipefail
dir=$1; out=$(cd "$(dirname "$2")" && pwd)/$(basename "$2"); q=${3:-delivery}
cd "$dir"
npx hyperframes check >/tmp/hf-check-$$.txt 2>&1 || true
if grep -q "✗" /tmp/hf-check-$$.txt; then grep "✗" /tmp/hf-check-$$.txt; echo "check có lỗi, dừng render" >&2; exit 1; fi
npx hyperframes render --output "$out" --quality "$q" --fps 30 --skill hyperframes --quiet
echo "$out"

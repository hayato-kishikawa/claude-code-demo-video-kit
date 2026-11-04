#!/usr/bin/env bash
# site/ の画面を 1920×1080・2 倍解像度で assets/ui/ に撮る（Chrome のヘッドレス撮影。追加の依存なし）
# 既定は HyperFrames が初回の check/render で落とす chrome-headless-shell。
# 通常の google-chrome --headless=new はウィンドウ枠のぶんビューポートが縮み、下端が欠ける。
set -euo pipefail
cd "$(dirname "$0")/.."
CHROME="${CHROME:-$(ls -d ~/.cache/hyperframes/chrome/chrome-headless-shell/*/*/chrome-headless-shell 2>/dev/null | tail -1)}"
[ -x "$CHROME" ] || { echo "chrome-headless-shell が見つかりません。先に npm run check を 1 回実行するか、CHROME= で指定してください"; exit 1; }
mkdir -p assets/ui
for page in index app-availability app-booked app-usage; do
  "$CHROME" --disable-gpu --hide-scrollbars --allow-file-access-from-files \
    --window-size=1920,1080 --force-device-scale-factor=2 --virtual-time-budget=3000 \
    --screenshot="assets/ui/${page}.png" "file://$PWD/site/${page}.html" 2>/dev/null
  echo "assets/ui/${page}.png"
done

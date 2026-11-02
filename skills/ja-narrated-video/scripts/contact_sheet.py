"""画像フォルダを一覧のコンタクトシートにする（選定は Read で画像を見る）。
使い方: python3 contact_sheet.py <dir> [name_filter] [out.jpg] [cols=3]
例: python3 contact_sheet.py assets/gen w_ /tmp/sheet.jpg   → w_ を含む画像だけ"""
import sys, glob, os
from PIL import Image, ImageDraw
d = sys.argv[1]; sel = sys.argv[2] if len(sys.argv) > 2 else ""
out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(d, f"_contact_{sel or 'all'}.jpg")
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 3
files = sorted(f for f in glob.glob(os.path.join(d, "*.png")) + glob.glob(os.path.join(d, "*.jpg")) if sel in os.path.basename(f) and not os.path.basename(f).startswith("_contact"))
W, H = 640, 360
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (W * cols, H * max(rows, 1)), "white"); dr = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((W, H), Image.LANCZOS)
    x, y = (i % cols) * W, (i // cols) * H
    sheet.paste(im, (x, y)); dr.rectangle([x, y, x + 260, y + 22], fill="black"); dr.text((x + 4, y + 4), os.path.basename(f), fill="white")
sheet.save(out, quality=85); print(out, len(files))

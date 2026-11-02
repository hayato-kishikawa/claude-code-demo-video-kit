"""レンダ済み mp4 から指定秒のコマを抜いて 1 枚のシートにする（Read で見て目視検証する）。
使い方: python3 sample_frames.py renders/x.mp4 out.jpg 2 14 21 28 36 ...
コツ: 各コマの中盤＋転換直後＋吹き出し・カバー剥がしの直後＋締めのロゴを選ぶ。3 列で 9〜15 枚が見やすい。"""
import subprocess, sys, os, tempfile
from PIL import Image, ImageDraw
if len(sys.argv) < 4: print(__doc__); sys.exit(1)
video, out, ts = sys.argv[1], sys.argv[2], [float(t) for t in sys.argv[3:]]
W, H, cols = 640, 360, 3
rows = (len(ts) + cols - 1) // cols
sheet = Image.new("RGB", (W * cols, H * rows), "white"); d = ImageDraw.Draw(sheet)
tmp = tempfile.mkdtemp()
for i, t in enumerate(ts):
    f = os.path.join(tmp, f"f_{i}.jpg")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", video, "-frames:v", "1", "-vf", f"scale={W}:{H}", f], check=True)
    im = Image.open(f); x, y = (i % cols) * W, (i // cols) * H
    sheet.paste(im, (x, y)); d.rectangle([x, y, x + 70, y + 20], fill="black"); d.text((x + 4, y + 3), f"{t}s", fill="white")
sheet.save(out, quality=85); print(out, len(ts))

# -*- coding: utf-8 -*-
"""ヘヤマド 30 秒のコマ（compositions/frames/*.html）と index_config.json を作る。
使い方（プロジェクト直下）: python3 .hyperframes/build_frames_meetroom.py
尺は assets/voice/voice_meta.json の実尺から決める：コマ尺 = LEAD + ナレーション + TAIL。"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "skills", "ja-narrated-video", "scripts"))
import build_frames as bf
from build_frames import build_frame

bf.ACCENT = (15, 123, 95)            # 深緑 #0F7B5F（BRIEF の palette）
LEAD, TAIL = 0.4, 0.35               # コマ頭からナレーションまで／ナレーション後の余白
GROUND = "#F6F8F7"
NOTE = "架空のサービスのデモ画面"
# 注記ピルは既定で右上。実画面は右上にボタンやユーザー名があるので、左下（字幕帯の外）に置く
def note_css(fid):
    return f".{fid}-note{{top:auto;right:auto;left:40px;bottom:24px;font-size:18px;}}"

vm = json.load(open("assets/voice/voice_meta.json"))
def dur(vid, minimum=0.0):
    return round(max(LEAD + vm[vid]["duration_s"] + TAIL, minimum), 2)

os.makedirs("compositions/frames", exist_ok=True)
F = []

# c01 朝のオフィス。ガラス張りの会議室（＝窓）を見せて、c03 の「窓が灯る」につなぐ
d = dur("c01"); F.append(("c01-morning", d))
build_frame("c01-morning", d, [
    {"img": "gen/flare/c01_corridor_b.png", "s": 0, "e": d, "kb": (1.0, 1.06, -24, -6)},
])

# c02 サービス名。LP をゆっくり寄せる
d = dur("c02", 3.0); F.append(("c02-name", d))
build_frame("c02-name", d, [
    {"img": "ui/index.png", "s": 0, "e": d, "kb": (1.0, 1.05, 24, 0)},
], note=(NOTE, 0.0, d), extra_css=note_css("c02-name"))

# c03 探す。条件のチップ（時間・人数）を枠で示し、灯った窓へパンチイン（1.4 倍）
d = dur("c03"); F.append(("c03-find", d))
build_frame("c03-find", d, [
    {"img": "ui/app-availability.png", "s": 0, "e": d,
     "hls": [{"box": (506, 124, 180, 72), "at": 0.55, "off": 1.9},
             {"box": (700, 124, 180, 72), "at": 0.85, "off": 1.9}],
     "punch": {"s": 1.4, "tx": 0, "ty": -20, "at": 1.9, "d": 1.3}},   # 中心 (960,560)。左端のサイドバーを画角から外す
], note=(NOTE, 0.0, d), extra_css=note_css("c03-find"))

# c04 予約する。完了カードに寄せ、「予定表に招待」の行を示す
d = dur("c04"); F.append(("c04-book", d))
build_frame("c04-book", d, [
    {"img": "ui/app-booked.png", "s": 0, "e": d,
     "punch": {"s": 1.3, "tx": -132, "ty": -68, "at": 0.2, "d": 1.4},
     "hls": [{"box": (712, 657, 760, 68), "at": 2.1, "r": 14}]},
], note=(NOTE, 0.0, d), extra_css=note_css("c04-book"))

# c05 回る。「自動で解放した予約」→ 解放ログ
d = dur("c05"); F.append(("c05-loop", d))
build_frame("c05-loop", d, [
    {"img": "ui/app-usage.png", "s": 0, "e": d, "kb": (1.0, 1.03, 0, 0),
     "hls": [{"box": (838, 122, 508, 182), "at": 0.5, "off": 2.7, "r": 16},
             {"box": (1352, 327, 522, 538), "at": 2.9, "r": 16}]},
], note=(NOTE, 0.0, d), extra_css=note_css("c05-loop"))

# c06 会議が始まる
d = dur("c06", 3.0); F.append(("c06-talk", d))
build_frame("c06-talk", d, [
    {"img": "gen/flare/c06_meeting_a.png", "s": 0, "e": d, "kb": (1.0, 1.05, 0, -10)},
])

# c07 締め。ロゴ（2×2 の窓のうち 1 つが灯る）とサービス名
d = dur("c07", 2.6); F.append(("c07-close", d))
fid = "c07-close"
build_frame(fid, d, [], extra_css=f"""
.{fid}-ground{{background:{GROUND};}}
.{fid}-lockup{{position:absolute;left:0;right:0;top:380px;display:flex;align-items:center;justify-content:center;gap:40px;}}
.{fid}-mark{{display:grid;grid-template-columns:repeat(2,92px);gap:18px;padding:26px;border-radius:36px;background:#1C2B25;}}
.{fid}-mark i{{display:block;height:92px;border-radius:14px;background:#33453E;}}
.{fid}-name{{font-family:"Noto Sans JP",sans-serif;font-weight:700;font-size:120px;letter-spacing:0.02em;color:#14211C;}}
""", extra_html=f"""
  <div class="{fid}-lockup">
    <div class="{fid}-mark" id="{fid}-mark"><i></i><i id="{fid}-lit"></i><i></i><i></i></div>
    <div class="{fid}-name" id="{fid}-name">ヘヤマド</div>
  </div>""", extra_js=f"""
  tl.fromTo(q("mark"), {{opacity:0,scale:0.92}}, {{opacity:1,scale:1,duration:0.5,ease:"back.out(1.6)"}}, 0.15);
  tl.fromTo(q("lit"), {{backgroundColor:"#33453E"}}, {{backgroundColor:"#7FD3B4",duration:0.35,ease:"power2.out"}}, 0.55);
  tl.fromTo(q("name"), {{opacity:0,x:-16}}, {{opacity:1,x:0,duration:0.5,ease:"power3.out"}}, 0.4);""")

# index_config.json（開始秒は累積）
frames, t = [], 0.0
for fid, d in F:
    frames.append([fid, round(t, 2), d]); t += d
total = round(t, 2)
cfg = {"frames": frames, "total": total, "voice_dir": "assets/voice", "voice_id": "prefix3",
       "pre": 0.4, "lead": LEAD, "bgm": f"assets/bgm/bed_{int(round(total))}.mp3",
       "bgm_keys": [[0, 0.2], [frames[2][1], 0.16], [frames[6][1] - 0.5, 0.26]],
       "fonts": "assets/fonts/NotoSansJP-Medium.ttf"}
json.dump(cfg, open("index_config.json", "w"), ensure_ascii=False, indent=1)
print("total", total, "turn(c03)", frames[2][1])

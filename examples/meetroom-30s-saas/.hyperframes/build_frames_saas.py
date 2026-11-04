# -*- coding: utf-8 -*-
"""ヘヤマド 30 秒・SaaS 版のコマ（compositions/frames/*.html）と index_config.json を作る。
使い方（プロジェクト直下）: python3 .hyperframes/build_frames_saas.py
落ち着いた版（../meetroom-30s）と同じ画面・同じ主張のまま、テイストだけを変える：
白地＋ミントと空色の光、傾いて浮かぶ画面カード、ばねの動き、大きな文字、カウントアップ、横に押し出す転換。"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "skills", "ja-narrated-video", "scripts"))
import build_frames as bf
from build_frames import build_frame

bf.ACCENT = (16, 185, 129)            # エメラルド #10B981
LEAD, TAIL = 0.35, 0.3                # 落ち着いた版（0.4 / 0.35）より詰める
NOTE = "架空のサービスのデモ画面"
INK, ACC, DEEP = "#14211C", "#10B981", "#0F7B5F"

vm = json.load(open("assets/voice/voice_meta.json"))
caps = json.load(open("assets/voice/captions.json"))
def dur(vid, minimum=0.0):
    return round(max(LEAD + vm[vid]["duration_s"] + TAIL, minimum), 2)

def base_css(fid):
    """白地にミントと空色の光。注記ピルは左下"""
    return f"""
.{fid}-ground{{background:radial-gradient(60% 70% at 12% 18%,#DDF7EC 0%,rgba(221,247,236,0) 62%),
  radial-gradient(55% 65% at 88% 82%,#DCEEFF 0%,rgba(220,238,255,0) 62%),#FFFFFF;}}
.{fid}-note{{top:auto;right:auto;left:40px;bottom:24px;font-size:18px;}}
.{fid}-card{{position:absolute;border-radius:22px;overflow:hidden;background:#fff;border:0;
  box-shadow:0 40px 90px rgba(16,70,52,.18),0 10px 24px rgba(16,70,52,.10);will-change:transform,opacity;}}
.{fid}-card img{{position:absolute;left:0;top:0;width:100%;height:100%;display:block;transform-origin:50% 50%;}}
.{fid}-kt{{position:absolute;left:120px;font-family:"Noto Sans JP",sans-serif;font-weight:700;font-size:86px;
  line-height:1.15;letter-spacing:-0.02em;color:{INK};white-space:nowrap;opacity:0;}}
.{fid}-kt em{{font-style:normal;color:{DEEP};}}
"""

def float_card(fid, cid, img, x, y, w, at=0.1):
    """傾いたカードが起き上がって浮かぶ。画面は 16:9"""
    h = round(w * 9 / 16)
    html = f'<div class="{fid}-card" id="{fid}-{cid}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;"><img id="{fid}-{cid}i" src="assets/{img}" alt=""></div>'
    js = (f'  tl.fromTo(q("{cid}"), {{opacity:0,y:90,scale:0.9,rotationX:16,rotationY:-12,transformPerspective:1800}},'
          f' {{opacity:1,y:0,scale:1,rotationX:0,rotationY:0,duration:0.75,ease:"back.out(1.4)"}}, {at:g});\n')
    return html, js, h

def kinetic(fid, lines, top, gap=128):
    """lines=[(html, at)]。下から出る大きな文字"""
    html, js = [], []
    for i, (t, at) in enumerate(lines):
        html.append(f'<div class="{fid}-kt" id="{fid}-k{i}" style="top:{top + i * gap}px;">{t}</div>')
        js.append(f'  tl.fromTo(q("k{i}"), {{opacity:0,y:40}}, {{opacity:1,y:0,duration:0.45,ease:"power3.out"}}, {at:g});')
    return "\n".join(html), "\n".join(js) + "\n"

def cue_start(vid, k, fallback):
    """k 番目の字幕キューの開始（コマ内秒）。台本を変えてキューが足りなければ fallback（音声内の秒）を使う"""
    cs = caps.get(vid, [])
    return round(LEAD + (cs[k]["start"] if len(cs) > k else fallback), 2)

def at_char(vid, n):
    """ナレーションの n 文字目が読まれるおよその時刻（コマ内秒）"""
    text = vm[vid]["text"]
    return round(LEAD + vm[vid]["duration_s"] * n / len(text), 2)

os.makedirs("compositions/frames", exist_ok=True)
F = []

# c01 大きな文字＋窓が灯るビル（このコマの字幕は出さない）
fid, vid = "c01-hook", "c01"; d = dur(vid); F.append((fid, d))
kh, kj = kinetic(fid, [("会議室は、", LEAD), ("探すものから、", at_char(vid, 5)),
                       ("<em>すぐ見つかる</em>ものへ。", at_char(vid, 12))], top=320, gap=112)
build_frame(fid, d, [{"img": "gen/flare/s01_building_a.png", "s": 0, "e": d, "kb": (1.0, 1.05, -10, 0)}],
            extra_css=base_css(fid), extra_html=kh, extra_js=kj)

# c02 サービス名：LP のカードが起き上がる
fid, vid = "c02-name", "c02"; d = dur(vid, 3.0); F.append((fid, d))
ch, cj, _ = float_card(fid, "lp", "ui/index.png", 320, 96, 1280)
cj += '  tl.to(q("lp"), {scale:1.03,duration:%g,ease:"none"}, 0.85);\n' % (d - 0.85)
build_frame(fid, d, [], note=(NOTE, 0.0, d), extra_css=base_css(fid), extra_html=ch, extra_js=cj)

# c03 探す：空き状況のカード → 「空いている部屋が」で窓に寄る
fid, vid = "c03-find", "c03"; d = dur(vid); F.append((fid, d))
ch, cj, _ = float_card(fid, "av", "ui/app-availability.png", 320, 96, 1280)
zoom_at = round(cue_start(vid, 1, vm[vid]["duration_s"] * 0.45) - 0.1, 2)
cj += ('  tl.set(q("avi"), {transformOrigin:"38% 52%"}, 0);\n'
       f'  tl.to(q("avi"), {{scale:1.75,duration:1.0,ease:"power3.inOut"}}, {zoom_at:g});\n')
build_frame(fid, d, [], note=(NOTE, 0.0, d), extra_css=base_css(fid), extra_html=ch, extra_js=cj)

# c04 予約する：予約完了のカード → 「予定表にも」でカレンダーと紙飛行機
fid, vid = "c04-book", "c04"; d = dur(vid); F.append((fid, d))
cal_at = round(cue_start(vid, 1, vm[vid]["duration_s"] * 0.4) - 0.15, 2)
ch, cj, _ = float_card(fid, "bk", "ui/app-booked.png", 120, 150, 1120)
cj += ('  tl.set(q("bki"), {transformOrigin:"57% 50%"}, 0);\n'
       '  tl.to(q("bki"), {scale:1.6,duration:0.9,ease:"power3.inOut"}, 0.75);\n')   # 中央のダイアログに寄せる
build_frame(fid, d, [{"img": "gen/flare/s04_calendar_b.png", "s": cal_at, "e": d, "fade_in": 0.35, "kb": (0.94, 1.0, 0, 0)}],
            note=(NOTE, 0.0, d), extra_css=base_css(fid) + f"#{fid}-L1{{transform-origin:82% 50%;}}",
            extra_html=ch, extra_js=cj)

# c05 回る：利用状況のカード＋解放した予約の件数をカウントアップ
fid, vid = "c05-loop", "c05"; d = dur(vid, 3.2); F.append((fid, d))
ch, cj, _ = float_card(fid, "us", "ui/app-usage.png", 110, 170, 1040)
ch += f'''
<div id="{fid}-num" style="position:absolute;left:1240px;top:300px;font-family:'Noto Sans JP',sans-serif;font-weight:700;font-size:200px;line-height:1;letter-spacing:-0.03em;color:{DEEP};opacity:0;"><span id="{fid}-n">0</span><span style="font-size:72px;margin-left:8px;">件</span></div>
<div id="{fid}-lab" style="position:absolute;left:1248px;top:540px;font-family:'Noto Sans JP',sans-serif;font-weight:500;font-size:40px;color:{INK};opacity:0;">の予約を自動で解放<br><span style="font-size:28px;color:#4F5B6E;">10 月・架空のデータ</span></div>'''
cj += f'''  tl.fromTo(q("num"), {{opacity:0,y:30}}, {{opacity:1,y:0,duration:0.4,ease:"power3.out"}}, 0.45);
  tl.fromTo(q("lab"), {{opacity:0,y:20}}, {{opacity:1,y:0,duration:0.4,ease:"power3.out"}}, 0.65);
  var cnt = {{v:0}}, nEl = document.querySelector(q("n"));
  tl.to(cnt, {{v:124,duration:1.3,ease:"power2.out",onUpdate:function(){{ nEl.textContent = Math.round(cnt.v); }}}}, 0.5);
'''
build_frame(fid, d, [], note=(NOTE, 0.0, d), extra_css=base_css(fid), extra_html=ch, extra_js=cj)

# c06 話す：明るいオフィスのチーム
fid, vid = "c06-talk", "c06"; d = dur(vid, 3.0); F.append((fid, d))
build_frame(fid, d, [{"img": "gen/flare/s06_team_a.png", "s": 0, "e": d, "kb": (1.0, 1.06, -10, -6)}])

# c07 締め：ロゴがばねで出て、窓が 1 つ灯る（このコマの字幕は出さない）
fid, vid = "c07-close", "c07"; d = dur(vid, 2.6); F.append((fid, d))
build_frame(fid, d, [], extra_css=base_css(fid) + f"""
.{fid}-lockup{{position:absolute;left:0;right:0;top:390px;display:flex;align-items:center;justify-content:center;gap:44px;}}
.{fid}-mark{{display:grid;grid-template-columns:repeat(2,96px);gap:18px;padding:26px;border-radius:38px;background:{DEEP};
  box-shadow:0 30px 70px rgba(16,70,52,.25);}}
.{fid}-mark i{{display:block;height:96px;border-radius:16px;background:#2E8C70;}}
.{fid}-name{{font-family:"Noto Sans JP",sans-serif;font-weight:700;font-size:140px;letter-spacing:0.02em;color:{INK};}}
.{fid}-fict{{position:absolute;left:0;right:0;top:700px;text-align:center;font-family:"Noto Sans JP",sans-serif;font-weight:500;font-size:28px;color:#4F5B6E;opacity:0;}}
""", extra_html=f"""
  <div class="{fid}-lockup">
    <div class="{fid}-mark" id="{fid}-mark"><i></i><i id="{fid}-lit"></i><i></i><i></i></div>
    <div class="{fid}-name" id="{fid}-name">ヘヤマド</div>
  </div>
  <div class="{fid}-fict" id="{fid}-fict">架空のサービスです（デモ用）</div>""", extra_js=f"""
  tl.fromTo(q("fict"), {{opacity:0}}, {{opacity:1,duration:0.4,ease:"power1.out"}}, 0.8);
  tl.fromTo(q("mark"), {{opacity:0,scale:0.6,rotation:-8}}, {{opacity:1,scale:1,rotation:0,duration:0.6,ease:"back.out(2)"}}, 0.1);
  tl.fromTo(q("lit"), {{backgroundColor:"#2E8C70"}}, {{backgroundColor:"#A7F3D0",duration:0.3,ease:"power2.out"}}, 0.5);
  tl.fromTo(q("name"), {{opacity:0,x:-24}}, {{opacity:1,x:0,duration:0.45,ease:"power3.out"}}, 0.3);""")

frames, t = [], 0.0
for fid, d in F:
    frames.append([fid, round(t, 2), d]); t += d
total = round(t, 2)
cfg = {"frames": frames, "total": total, "voice_dir": "assets/voice", "voice_id": "prefix3",
       "pre": 0.35, "lead": LEAD, "bgm": f"assets/bgm/bed_{int(round(total))}.mp3",
       "bgm_keys": [[0, 0.3], [frames[1][1], 0.24], [frames[6][1] - 0.4, 0.4]],
       "fonts": "assets/fonts/NotoSansJP-Medium.ttf",
       "transition": "push", "trans_dur": 0.35, "ground": "#FFFFFF", "caption_skip": ["c01", "c07"]}
json.dump(cfg, open("index_config.json", "w"), ensure_ascii=False, indent=1)
print("total", total, "turn(c02)", frames[1][1])

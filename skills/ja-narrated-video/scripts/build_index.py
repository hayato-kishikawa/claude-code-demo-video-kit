"""index.html（root コンポ）を設定 JSON から生成する: コマのスロット、blur crossfade、ナレーション <audio>、字幕トラック、BGM。
使い方: python3 build_index.py index_config.json   （プロジェクト直下で実行）
index_config.json の例:
{
  "frames": [["e01-question",0,6.0],["e02-pain",6.0,12.5],["e08-close",93.0,7.5]],   # [id, 開始秒, 尺]
  "total": 100.5,
  "voice_dir": "assets/voice_v2",        # lines.json / voice_meta.json / captions.json
  "voice_id": "prefix3",                 # コマ id → 音声 id の対応。"prefix3"=先頭 3 文字（e01-question→e01）
  "pre": 0.5,                            # 前のコマを延長して重ねる秒（転換用）
  "lead": 0.6,                           # コマ開始からナレーション開始までの間
  "bgm": "assets/bgm/bed_101.mp3",
  "bgm_keys": [[0,0.26],[18,0.22],[21,0.15],[96,0.24]],   # [秒, 音量]。先頭は set、以降は 2 秒の to
  "fonts": "assets/fonts/NotoSansJP-Medium.ttf"
}
字幕は下中央（left/right 240px, bottom 62px）、44px/500 の白ピル。1 行 30 字以内は build_captions.py 側で保証する。"""
import json, sys
if len(sys.argv) < 2: print(__doc__); sys.exit(1)
C = json.load(open(sys.argv[1]))
FRAMES = [tuple(f) for f in C["frames"]]; TOTAL = C["total"]; PRE = C.get("pre", 0.5); LEAD = C.get("lead", 0.6)
VD = C["voice_dir"].rstrip("/")
caps = json.load(open(f"{VD}/captions.json")); vm = json.load(open(f"{VD}/voice_meta.json"))
vid_of = (lambda fid: fid[:3]) if C.get("voice_id", "prefix3") == "prefix3" else (lambda fid: fid)

slots, tl, audio, capdivs, capjs = [], [], [], [], []
for i, (fid, start, dur) in enumerate(FRAMES):
    s = start if i == 0 else start - PRE
    d = dur if i == 0 else dur + PRE
    slots.append(f'      <div id="el-{fid}" class="scene" style="z-index:{i+1}" data-composition-id="{fid}" '
                 f'data-composition-src="compositions/frames/{fid}.html" data-start="{s:g}" data-duration="{d:g}" '
                 f'data-track-index="{i%2}" data-width="1920" data-height="1080"></div>')
    if i > 0:
        prev = FRAMES[i - 1][0]; T = start
        tl.append(f'      tl.to("#el-{prev}", {{ filter: "blur(14px)", scale: 1.03, opacity: 0, duration: 0.5, ease: "power2.inOut" }}, {T-PRE:g});')
        tl.append(f'      tl.fromTo("#el-{fid}", {{ filter: "blur(14px)", scale: 0.97, opacity: 0 }}, {{ filter: "blur(0px)", scale: 1, opacity: 1, duration: 0.5, ease: "power2.inOut" }}, {T-PRE+0.08:g});')
    vid = vid_of(fid)
    if vid in vm:
        audio.append(f'      <audio id="el-vo-{vid}" src="{vm[vid]["path"]}" data-start="{start+LEAD:g}" '
                     f'data-duration="{vm[vid]["duration_s"]}" data-track-index="20" data-volume="1"></audio>')
        for k, c in enumerate(caps.get(vid, [])):
            cid = f"cap-{vid}-{k}"; a = start + LEAD + c["start"]; b = start + LEAD + c["end"]
            capdivs.append(f'      <div class="cap" id="{cid}"><span>{c["text"]}</span></div>')
            capjs.append(f'      tl.set("#{cid}", {{ opacity: 0 }}, 0);')
            capjs.append(f'      tl.fromTo("#{cid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.14, ease: "power1.out" }}, {a:g});')
            capjs.append(f'      tl.to("#{cid}", {{ opacity: 0, duration: 0.14, ease: "power1.in" }}, {max(a+0.3, b-0.14):g});')
audio.append(f'      <audio id="el-bgm" src="{C["bgm"]}" data-start="0" data-duration="{TOTAL:g}" data-track-index="30" data-volume="1"></audio>')
bgm = []
for j, (t, v) in enumerate(C.get("bgm_keys", [[0, 0.24]])):
    bgm.append(f'      tl.set("#el-bgm", {{ volume: {v} }}, 0);' if j == 0 else
               f'      tl.to("#el-bgm", {{ volume: {v}, duration: 2, ease: "power1.inOut" }}, {t:g});')

html = f'''<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1920, height=1080">
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face{{font-family:"Noto Sans JP";font-weight:500;src:url("{C.get("fonts","assets/fonts/NotoSansJP-Medium.ttf")}") format("truetype");}}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #F5F7FB; }}
      #root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #F5F7FB; }}
      #root > .scene {{ position: absolute; inset: 0; width: 1920px; height: 1080px; overflow: hidden; transform-origin: 50% 50%; }}
      /* 字幕：ナレーション全文。位置は全編固定 */
      .cap {{ position: absolute; left: 240px; right: 240px; bottom: 62px; text-align: center; z-index: 50; opacity: 0; }}
      .cap span {{ display: inline-block; background: rgba(245,247,251,0.94); border-radius: 14px;
        padding: 16px 32px; font-family: "Noto Sans JP", sans-serif; font-weight: 500; font-size: 44px;
        line-height: 1.45; letter-spacing: -0.01em; color: #16202E; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:g}" data-width="1920" data-height="1080">
{chr(10).join(slots)}
{chr(10).join(capdivs)}
{chr(10).join(audio)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      var tl = gsap.timeline({{ paused: true }});
      // 場面転換：blur crossfade（calm）で統一
{chr(10).join(tl)}
      // 字幕（無音検出で境界を音声に合わせてある）
{chr(10).join(capjs)}
      // BGM：絶対値キーフレーム
{chr(10).join(bgm)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
open("index.html", "w").write(html)
print("index.html written:", len(FRAMES), "frames,", len(capdivs), "captions,", TOTAL, "s")

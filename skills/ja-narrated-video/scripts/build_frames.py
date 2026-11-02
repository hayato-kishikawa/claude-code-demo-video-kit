# -*- coding: utf-8 -*-
"""コマ（サブコンポジション）生成ライブラリ。プロジェクト直下で import して使う。座標は 1920x1080 系。
使い方: build_frames.py と同じ引数で build_frame() を呼ぶ .hyperframes/build_frames_<video>.py をプロジェクトに作る（references/worked-example.md 参照）。
    import sys; sys.path.insert(0, "<repo>/skills/ja-narrated-video/scripts")  # 相対または絶対パス
    import build_frames as bf; bf.ACCENT = (15, 123, 95)   # 任意：枠の色
    from build_frames import build_frame
    build_frame("e01-question", 6.0, [{"img":"gen/a1.jpg","s":0,"e":6.0,"kb":(1.0,1.05,-30,-18)}])
レイヤのキー: img s e kb fade_in fade_out_prev punch covers hls paints labels says ground nohl card / note=(text,s,e) / extra_css extra_html extra_js
"""
import json, os
from PIL import Image

ASSETS = "assets"
ACCENT = (67, 83, 216)   # ハイライト枠・カード枠の色（RGB）。ブランド色に合わせて import 後に上書きする
def ground(path, x, y):
    im = Image.open(os.path.join(ASSETS, path)).convert("RGB")
    k = im.width / 1920.0
    return "#%02X%02X%02X" % im.getpixel((int(x * k), int(y * k)))

FONTS = """
@font-face{font-family:"Noto Sans JP";font-weight:400;src:url("assets/fonts/NotoSansJP-Regular.ttf") format("truetype");}
@font-face{font-family:"Noto Sans JP";font-weight:500;src:url("assets/fonts/NotoSansJP-Medium.ttf") format("truetype");}
@font-face{font-family:"Noto Sans JP";font-weight:700;src:url("assets/fonts/NotoSansJP-Bold.ttf") format("truetype");}
@font-face{font-family:"IBM Plex Mono";font-weight:500;src:url("assets/fonts/IBMPlexMono-Medium.ttf") format("truetype");}
"""

def frame_css(fid):
    r, g, b = ACCENT; acc = "#%02X%02X%02X" % ACCENT
    return FONTS + f"""
#root{{position:absolute;inset:0;width:1920px;height:1080px;overflow:hidden;font-family:"Noto Sans JP",sans-serif;font-feature-settings:"palt" 1;color:#16202E;}}
.{fid}-ground{{background:#F5F7FB;}}
.{fid}-layer{{position:absolute;inset:0;overflow:hidden;}}
.{fid}-outer{{position:absolute;inset:0;transform-origin:50% 50%;will-change:transform;}}
.{fid}-inner{{position:absolute;inset:0;will-change:transform;}}
.{fid}-img{{position:absolute;left:0;top:0;width:1920px;height:1080px;display:block;}}
.{fid}-cover{{position:absolute;box-sizing:border-box;}}
.{fid}-hl{{position:absolute;box-sizing:border-box;border:3px solid {acc};border-radius:12px;background:rgba({r},{g},{b},0.06);transform-origin:50% 50%;opacity:0;will-change:transform,opacity;}}
.{fid}-card{{position:absolute;overflow:hidden;border-radius:16px;border:1.5px solid rgba({r},{g},{b},0.22);background:#FFFFFF;transform-origin:50% 50%;will-change:transform,opacity;}}
.{fid}-paint{{position:absolute;}}
.{fid}-say{{position:absolute;background:rgba(255,255,255,0.96);border-radius:16px;padding:18px 28px;font-family:"Noto Sans JP",sans-serif;font-weight:500;color:#16202E;line-height:1.4;letter-spacing:-0.01em;transform-origin:50% 50%;opacity:0;box-sizing:border-box;}}
.{fid}-label{{position:absolute;text-align:center;font-family:"Noto Sans JP",sans-serif;font-weight:700;color:#16202E;letter-spacing:-0.01em;}}
.{fid}-note{{position:absolute;right:56px;top:46px;text-align:right;line-height:1.5;font-family:"IBM Plex Mono","Noto Sans JP",monospace;font-weight:500;font-size:22px;letter-spacing:0.06em;color:#4F5B6E;background:rgba(255,255,255,0.94);padding:7px 16px;border-radius:100px;white-space:nowrap;opacity:0;}}
"""

def build_frame(fid, dur, layers, note=None, extra_html="", extra_css="", extra_js=""):
    html = [f'<template>', '<style>', frame_css(fid) + extra_css, '</style>', '',
            f'<div id="root" data-composition-id="{fid}" data-width="1920" data-height="1080">',
            f'  <div class="clip {fid}-ground" id="{fid}-ground" data-start="0" data-duration="{dur:g}" data-track-index="0"></div>']
    js = ['<script>', '(function(){', f'  var ID="{fid}";',
          '  var q=function(k){return "#"+ID+"-"+k;};',
          '  var tl=gsap.timeline({paused:true});']
    for i, L in enumerate(layers, start=1):
        s, e = L["s"], L["e"]
        cd = L.get("card")
        if cd:
            z = cd["zoom"]
            html.append(f'  <div class="clip {fid}-layer" id="{fid}-L{i}" data-start="{s:g}" data-duration="{(e-s):g}" data-track-index="{i}">')
            html.append(f'    <div class="{fid}-card" id="{fid}-L{i}c" style="left:{cd["x"]}px;top:{cd["y"]}px;width:{cd["w"]}px;height:{cd["h"]}px;">')
            html.append(f'      <img src="assets/{L["img"]}" alt="" style="position:absolute;left:{-cd["sx"]*z:g}px;top:{-cd["sy"]*z:g}px;width:{1920*z:g}px;height:{1080*z:g}px;display:block;">')
            html.append('    </div>')
            html.append('  </div>')
            js.append(f'  tl.fromTo(q("L{i}c"), {{opacity:0,scale:0.97}}, {{opacity:1,scale:1,duration:0.5,ease:"power3.out"}}, {s:g});')
            if L.get("fade_out_prev") and i > 1:
                js.append(f'  tl.to(q("L{i-1}"), {{opacity:0,duration:0.5,ease:"power1.inOut"}}, {s:g});')
                js.append(f'  tl.set(q("L{i-1}"), {{opacity:0}}, {s+0.5:g});')
            continue
        html.append(f'  <div class="clip {fid}-layer" id="{fid}-L{i}" data-start="{s:g}" data-duration="{(e-s):g}" data-track-index="{i}">')
        html.append(f'    <div class="{fid}-outer" id="{fid}-L{i}o"><div class="{fid}-inner" id="{fid}-L{i}i">')
        html.append(f'      <img class="{fid}-img" src="assets/{L["img"]}" alt="">')
        for j, pt in enumerate(L.get("paints", []), start=1):
            x, y, w, h = pt["box"]
            col = pt.get("color") or L.get("ground") or ground(L["img"], 960, 1020)
            html.append(f'      <div class="{fid}-paint" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{col};"></div>')
        for j, lb in enumerate(L.get("labels", []), start=1):
            x, y, w, fs = lb["box"]
            html.append(f'      <div class="{fid}-label" style="left:{x}px;top:{y}px;width:{w}px;font-size:{fs}px;line-height:1.2;">{lb["text"]}</div>')
        for j, sy in enumerate(L.get("says", []), start=1):
            x, y, w, fs = sy["box"]
            html.append(f'      <div class="{fid}-say" id="{fid}-s{i}{j}" style="left:{x}px;top:{y}px;width:{w}px;font-size:{fs}px;">{sy["text"]}</div>')
        for j, c in enumerate(L.get("covers", []), start=1):
            x, y, w, h = c["box"]
            col = c.get("color") or L.get("ground") or ground(L["img"], 960, 1020)
            html.append(f'      <div class="{fid}-cover" id="{fid}-c{i}{j}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{col};"></div>')
            if not L.get("nohl"):
                html.append(f'      <div class="{fid}-hl" id="{fid}-h{i}{j}" style="left:{x-6}px;top:{y-6}px;width:{w+12}px;height:{h+12}px;"></div>')
        for j, g in enumerate(L.get("hls", []), start=1):
            x, y, w, h = g["box"]
            r = g.get("r", 12)
            html.append(f'      <div class="{fid}-hl" id="{fid}-g{i}{j}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:{r}px;"></div>')
        html.append('    </div></div>')
        html.append('  </div>')
        # --- motion ---
        if L.get("fade_in"):
            js.append(f'  tl.fromTo(q("L{i}"), {{opacity:0}}, {{opacity:1,duration:{L["fade_in"]:g},ease:"power1.inOut"}}, {s:g});')
        if L.get("fade_out_prev") and i > 1:
            js.append(f'  tl.to(q("L{i-1}"), {{opacity:0,duration:{L["fade_in"]:g},ease:"power1.inOut"}}, {s:g});')
            js.append(f'  tl.set(q("L{i-1}"), {{opacity:0}}, {s + L["fade_in"]:g});')
        kb = L.get("kb")
        if kb:
            s0, s1, dx, dy = kb
            js.append(f'  tl.fromTo(q("L{i}o"), {{scale:{s0:g}}}, {{scale:{s1:g},duration:{(e-s):g},ease:"none"}}, {s:g});')
            if dx or dy:
                js.append(f'  tl.fromTo(q("L{i}i"), {{x:0,y:0}}, {{x:{dx:g},y:{dy:g},duration:{(e-s):g},ease:"none"}}, {s:g});')
        p = L.get("punch")
        if p:
            js.append(f'  tl.fromTo(q("L{i}o"), {{scale:1}}, {{scale:{p["s"]:g},duration:{p.get("d",1.0):g},ease:"power3.inOut"}}, {p["at"]:g});')
            js.append(f'  tl.fromTo(q("L{i}i"), {{x:0,y:0}}, {{x:{p["tx"]:g},y:{p["ty"]:g},duration:{p.get("d",1.0):g},ease:"power3.inOut"}}, {p["at"]:g});')
        for j, sy in enumerate(L.get("says", []), start=1):
            js.append(f'  tl.fromTo(q("s{i}{j}"), {{opacity:0,scale:0.94,y:10}}, {{opacity:1,scale:1,y:0,duration:0.5,ease:"power3.out"}}, {sy["at"]:g});')
        for j, c in enumerate(L.get("covers", []), start=1):
            at = c["at"]
            js.append(f'  tl.set(q("c{i}{j}"), {{opacity:1}}, 0); tl.set(q("c{i}{j}"), {{opacity:0}}, {at:g});')
            if not L.get("nohl"):
                js.append(f'  tl.fromTo(q("h{i}{j}"), {{scale:0.9,opacity:0}}, {{scale:1,opacity:1,duration:0.4,ease:"power3.out"}}, {at:g});')
                js.append(f'  tl.to(q("h{i}{j}"), {{opacity:0,duration:0.4,ease:"power1.inOut"}}, {at+1.1:g});')
        for j, g in enumerate(L.get("hls", []), start=1):
            at = g["at"]
            js.append(f'  tl.fromTo(q("g{i}{j}"), {{scale:0.94,opacity:0}}, {{scale:1,opacity:1,duration:0.45,ease:"power3.out"}}, {at:g});')
            if g.get("off"):
                js.append(f'  tl.to(q("g{i}{j}"), {{opacity:0,duration:0.4,ease:"power1.inOut"}}, {g["off"]:g});')
    if note:
        txt, ns, ne = note
        html.append(f'  <div class="clip" id="{fid}-noteclip" data-start="{ns:g}" data-duration="{(ne-ns):g}" data-track-index="9">')
        html.append(f'    <div class="{fid}-note" id="{fid}-note">{txt}</div>')
        html.append('  </div>')
        js.append(f'  tl.fromTo(q("note"), {{opacity:0}}, {{opacity:1,duration:0.35,ease:"power1.out"}}, {ns+0.35:g});')
    html.append(extra_html)
    html.append('</div>')
    js.append(extra_js)
    js.append('  window.__timelines=window.__timelines||{};')
    js.append('  window.__timelines[ID]=tl;')
    js.append('})();')
    js.append('</script>')
    html.append('')
    html.extend(js)
    html.append('</template>')
    out = "\n".join(html)
    open(f"compositions/frames/{fid}.html", "w").write(out)
    json.dump({"scene": fid, "duration_s": dur, "rules": ["viewport-change", "spring-pop-entrance", "discrete-text-sequence"],
               "exit": {"vector": "slow ken-burns push, <10 px/s", "still_moving": True},
               "entry": {"vector": "from rest", "from_rest": True}},
              open(f"compositions/frames/{fid}.motion.json", "w"), ensure_ascii=False, indent=1)
    print("wrote", fid, f"{dur}s", len(out), "bytes")


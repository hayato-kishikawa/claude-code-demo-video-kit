"""字幕チャンクを作り、音声の無音（＝句読点の間）に境界を合わせる。決定論的。
使い方: python3 build_captions.py <voice_dir> [--hard 30] [--minlen 8]
  入力: <voice_dir>/lines.json（id,text,caption?）, voice_meta.json（duration_s）, <id>.wav
  出力: <voice_dir>/captions.json  {id: [{text,start,end}]}（start/end はその音声ファイル内の秒）
規則: 「。」で文に割る → hard 字を超える文だけ中央に最も近い「、」で再帰的に割る → minlen 字未満の欠片は前に寄せる
      → 文字数（、+2.5 。+4.0 の重み）で見込み境界を出し、±0.7s 以内の無音中心にスナップ。
hard=30 で 44px・幅 1376px の字幕帯に 1 行で収まる。"""
import json, os, sys
import numpy as np, soundfile as sf

args = [a for a in sys.argv[1:] if not a.startswith("--")]
opt = {sys.argv[i].lstrip("-"): float(sys.argv[i + 1]) for i in range(1, len(sys.argv) - 1) if sys.argv[i].startswith("--")}
if not args: print(__doc__); sys.exit(1)
here = os.path.abspath(args[0]); HARD = int(opt.get("hard", 30)); MINLEN = int(opt.get("minlen", 8))
lines = json.load(open(os.path.join(here, "lines.json")))
meta = json.load(open(os.path.join(here, "voice_meta.json")))

def chunk(text, hard=HARD, minlen=MINLEN):
    parts, buf = [], ""
    for ch in text:
        buf += ch
        if ch == "。": parts.append(buf); buf = ""
    if buf.strip(): parts.append(buf)
    def split_mid(p):
        if len(p) <= hard: return [p]
        pos = [i for i, c in enumerate(p) if c == "、"]
        if not pos: return [p]
        cut = min(pos, key=lambda i: abs(i - len(p) / 2)) + 1
        return split_mid(p[:cut]) + split_mid(p[cut:])
    out = []
    for p in parts: out.extend(split_mid(p))
    merged = []
    for c in out:
        if merged and len(c) < minlen: merged[-1] += c
        else: merged.append(c)
    return merged

def silences(path, min_len=0.09):
    y, sr = sf.read(path, dtype="float32")
    if y.ndim > 1: y = y.mean(axis=1)
    win = int(0.02 * sr); n = len(y) // win
    rms = np.array([np.sqrt(np.mean(y[i * win:(i + 1) * win] ** 2)) for i in range(n)])
    thr = max(rms.max() * 0.06, 1e-4); quiet = rms < thr
    out, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            a, b = i * win / sr, j * win / sr
            if i > 3 and j < n - 3 and (b - a) >= min_len: out.append(((a + b) / 2, b - a))
            i = j
        else: i += 1
    return out

def expected(chunks, dur):
    w = [len(c) + 2.5 * c.count("、") + 4.0 * c.count("。") for c in chunks]
    tot = sum(w); acc, out = 0.0, []
    for x in w[:-1]: acc += x; out.append(acc / tot * dur)
    return out

def boundaries(path, chunks, dur, tol=0.7):
    exp = expected(chunks, dur)
    if not exp: return []
    sil = silences(path); got, prev = [], 0.0
    for e in exp:
        cands = [c for c, _ in sil if abs(c - e) <= tol and c > prev + 0.25 and c < dur - 0.2]
        b = min(cands, key=lambda c: abs(c - e)) if cands else max(e, prev + 0.25)
        got.append(b); prev = b
    return got

caps = {}
for ln in lines:
    cid = ln["id"]; path = os.path.join(here, f"{cid}.wav"); dur = meta[cid]["duration_s"]
    ch = chunk(ln.get("caption", ln["text"]))
    t = [0.0] + boundaries(path, ch, dur) + [dur]
    caps[cid] = [{"text": c, "start": round(t[i], 3), "end": round(t[i + 1], 3)} for i, c in enumerate(ch)]
json.dump(caps, open(os.path.join(here, "captions.json"), "w"), ensure_ascii=False, indent=1)
over = 0
for cid, cs in caps.items():
    print(cid, meta[cid]["duration_s"])
    for c in cs:
        mark = "  ← 30 字超え。台本に読点を足すか文を割る" if len(c["text"]) > HARD else ""
        over += bool(mark)
        print(f"   {c['start']:6.2f}–{c['end']:6.2f}  ({len(c['text'])}字) {c['text']}{mark}")
if over: print(f"WARN: {over} 件のキューが {HARD} 字を超えています（読点のない長い文は割れません）")

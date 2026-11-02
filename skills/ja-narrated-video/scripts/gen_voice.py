"""gpt-realtime-2 を日本語 TTS として使い、lines.json の各行を <voice_dir>/<id>.wav にする。
使い方: python3 gen_voice.py <voice_dir> [voice=marin] [id ...]
  <voice_dir>/lines.json : [{"id":"e01","text":"読み上げ文","caption":"字幕表記(省略可)"}]
  出力: <voice_dir>/<id>.wav（無音カット, atempo, loudnorm I=-16, 44.1k mono）と voice_meta.json
  話速: 環境変数 ATEMPO（既定 1.15）。1.06 だと遅く感じるという声が多かった。CM 調なら 1.2〜1.25
前提: .env を読み込んであること（接続先は _client.py の PROVIDER を参照）。
transcript（realtime が返す読み上げ内容）を正規化して原文と照合し、3 回までリトライする。"""
import asyncio, json, os, re, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_tts import tts

if len(sys.argv) < 2:
    print(__doc__); sys.exit(1)
here = os.path.abspath(sys.argv[1])
voice = sys.argv[2] if len(sys.argv) > 2 else "marin"
only = set(sys.argv[3:])
lines = json.load(open(os.path.join(here, "lines.json")))
if only: lines = [l for l in lines if l["id"] in only]
norm = lambda s: re.sub(r"[\s、。・,.!?！？「」]", "", s).replace("AI", "エーアイ").replace("ＡＩ", "エーアイ")
metap = os.path.join(here, "voice_meta.json")
meta = json.load(open(metap)) if (only and os.path.exists(metap)) else {}
rel = os.path.relpath(here, os.getcwd())  # index.html から見た相対パス（プロジェクト直下で実行する）
ATEMPO = float(os.environ.get("ATEMPO", "1.15"))
AF = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.15,areverse,"
      "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.25,areverse,"
      f"atempo={ATEMPO},loudnorm=I=-16:TP=-1.5:LRA=11")

async def main():
    for ln in lines:
        raw = os.path.join(here, f"{ln['id']}_{voice}.raw.wav")
        out = os.path.join(here, f"{ln['id']}.wav")
        ok = False
        for attempt in range(3):
            r = await tts(ln["text"], raw, voice)
            if norm(r["transcript"]) == norm(ln["text"]) and r["seconds"] > 1.0:
                ok = True; break
            print("  retry", ln["id"], attempt, r["transcript"], flush=True)
        if not ok: print("  WARN mismatch kept", ln["id"], flush=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", AF, "-ar", "44100", "-ac", "1", out], check=True)
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]).decode().strip())
        meta[ln["id"]] = {"path": f"{rel}/{ln['id']}.wav", "duration_s": round(dur, 3), "text": ln["text"], "atempo": ATEMPO}
        print(ln["id"], round(dur, 2), flush=True)
    json.dump(meta, open(metap, "w"), ensure_ascii=False, indent=1)

asyncio.run(main())

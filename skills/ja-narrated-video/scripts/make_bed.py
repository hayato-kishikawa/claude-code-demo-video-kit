# -*- coding: utf-8 -*-
"""seed_a（単音ピアノ）→ seed_b（主旋律）の BGM ベッドを numpy で組む。
使い方: python3 make_bed.py index_config.json   （推奨。コマを組んだあとに実行し、総尺と切替秒を設定から読む）
        python3 make_bed.py <total_s> <turn_s>
  プロジェクト直下で実行する。assets/bgm/seed_a.wav, seed_b.wav が要る。切替秒は bgm_keys の 2 番目の秒（無ければ総尺の 3 割）
  0..turn は seed_a をループ（1.5s クロスフェード）、turn で 3s かけて seed_b ループに切り替え、末尾 5.5s フェードアウト。
  出力 assets/bgm/bed_<total>.mp3"""
import sys, subprocess, numpy as np, soundfile as sf
if sys.argv[1].endswith(".json"):
    import json
    cfg = json.load(open(sys.argv[1])); total = float(cfg["total"])
    keys = cfg.get("bgm_keys") or []
    turn = float(keys[1][0]) if len(keys) > 1 else round(total * 0.3, 2)
else:
    total, turn = float(sys.argv[1]), float(sys.argv[2])
a, sr = sf.read("assets/bgm/seed_a.wav", dtype="float32"); b, sr2 = sf.read("assets/bgm/seed_b.wav", dtype="float32")
assert sr == sr2
if a.ndim > 1: a = a.mean(axis=1)
if b.ndim > 1: b = b.mean(axis=1)
def loop(seed, length_s, xf=1.5):
    n = int(length_s * sr); x = int(xf * sr); out = np.zeros(n + len(seed), dtype="float32"); pos = 0
    ramp_in = np.linspace(0, 1, x, dtype="float32"); ramp_out = 1 - ramp_in
    while pos < n:
        seg = seed.copy()
        if pos > 0: seg[:x] *= ramp_in; out[pos:pos + x] *= ramp_out
        out[pos:pos + len(seg)] += seg; pos += len(seg) - x
    return out[:n]
A = loop(a, turn + 3.0); B = loop(b, total - turn)
out = np.zeros(int(total * sr) + sr, dtype="float32")
out[:len(A)] += A
x = int(3.0 * sr); t0 = int(turn * sr)
out[t0:t0 + x] *= np.linspace(1, 0, x, dtype="float32")   # A fades over 3s at turn
Bx = B.copy(); Bx[:x] *= np.linspace(0, 1, x, dtype="float32")
out[t0:t0 + len(Bx)] += Bx
out = out[:int(total * sr)]
f = int(5.5 * sr); out[-f:] *= np.linspace(1, 0, f, dtype="float32")
peak = np.max(np.abs(out)); out = out * (0.89 / peak)
sf.write("assets/bgm/_bed_tmp.wav", out, sr)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "assets/bgm/_bed_tmp.wav", "-af", "loudnorm=I=-23:TP=-2:LRA=9", "-ar", "44100", "-b:a", "192k", f"assets/bgm/bed_{int(round(total))}.mp3"], check=True)
print("wrote", f"assets/bgm/bed_{int(round(total))}.mp3", total, "turn", turn)

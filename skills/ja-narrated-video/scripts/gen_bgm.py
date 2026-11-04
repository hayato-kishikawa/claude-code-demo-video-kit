"""MusicGen small（CPU 可）で BGM の素材 2 本（seed_a 静かな単音ピアノ／seed_b 明るい主旋律、各 28 秒）を作る。
使い方: python3 gen_bgm.py [out_dir=assets/bgm] [preset=calm|upbeat]
  calm  : 静かな単音ピアノ → 温かいピアノと弦（説明・展示向け）
  upbeat: 軽いシンセのイントロ → 明るいポップなビート（SaaS のローンチ・広告向け）
注意: facebook/musicgen-small の重みは CC-BY-NC 4.0（非商用）。商用の動画ではロイヤリティフリー音源を
      assets/bgm/seed_a.wav / seed_b.wav に置き換えるか、ベッドそのもの（bed_<尺>.mp3）を差し替える。"""
import math, os, sys, time, traceback
import numpy as np, soundfile as sf
from transformers import MusicgenForConditionalGeneration, AutoProcessor
out_dir = sys.argv[1] if len(sys.argv) > 1 else "assets/bgm"
os.makedirs(out_dir, exist_ok=True)
t_start = time.time()
PRESETS = {
  "calm": {
    "seed_a": "gentle minimal solo piano, sparse single notes, quiet, slightly tense, warm room reverb, slow 70 bpm, corporate documentary underscore, no drums",
    "seed_b": "hopeful cinematic corporate underscore, warm piano melody with soft strings and light pads, steady 90 bpm, uplifting and clear, no drums, no vocals",
  },
  "upbeat": {
    "seed_a": "light plucky synth arpeggio intro, bright and airy, soft claps, modern tech product launch, 118 bpm, minimal, no vocals",
    "seed_b": "bright upbeat modern pop beat for a tech startup product video, punchy kick, crisp claps, plucky synth melody, warm bass, optimistic and energetic, 118 bpm, no vocals",
  },
}
seeds = PRESETS[sys.argv[2] if len(sys.argv) > 2 else "calm"]
try:
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small"); model.eval()
    sr = int(model.config.audio_encoder.sampling_rate)
    for name, prompt in seeds.items():
        path = os.path.join(out_dir, f"{name}.wav")
        if os.path.exists(path): print("skip", path, flush=True); continue
        tokens = int(math.ceil(28 * 50))
        print(f"[musicgen] {name} tokens={tokens}", flush=True)
        inputs = processor(text=[prompt], padding=True, return_tensors="pt")
        audio = model.generate(**inputs, max_new_tokens=tokens, do_sample=True, guidance_scale=3.0)
        seed = audio[0, 0].detach().cpu().numpy().astype("float32")
        peak = float(np.max(np.abs(seed)));
        if peak > 1e-6: seed = seed * (0.89 / peak)
        sf.write(path, seed, sr); print("wrote", path, seed.shape[0]/sr, flush=True)
    print(f"done {time.time()-t_start:.0f}s", flush=True)
except Exception:
    traceback.print_exc(); sys.exit(1)

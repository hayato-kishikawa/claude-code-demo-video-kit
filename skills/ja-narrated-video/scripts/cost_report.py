"""costs.jsonl（run_images.py / rt_tts.py / 各工程の時刻）から、工程別の費用と時間の表を Markdown で出す。
使い方: python3 cost_report.py [costs.jsonl] > docs/costs.md
単価は 100 万トークンあたりの米ドル。Azure（Global 標準）と OpenAI API は同額だった（下の出典・取得日を参照）。
値が変わったら PRICES を直す。"""
import json, sys
from collections import defaultdict

PRICES = {  # USD / 1M tokens
    "gpt-image-2":    {"text_in": 5.00, "image_in": 8.00, "image_out": 30.00},
    "gpt-realtime-2": {"text_in": 4.00, "text_cached_in": 0.40, "audio_in": 32.00, "text_out": 24.00, "audio_out": 64.00},
}
SOURCES = ("Azure: https://prices.azure.com/api/retail/prices（Azure OpenAI Media, eastus, Global, 2026-05-01 発効）／"
           "OpenAI: https://developers.openai.com/api/docs/pricing（2026-11-02 取得）")

def image_cost(u):
    p = PRICES["gpt-image-2"]; it = u.get("input_tokens_details", {}); ot = u.get("output_tokens_details", {})
    return (it.get("text_tokens", u.get("input_tokens", 0)) * p["text_in"] + it.get("image_tokens", 0) * p["image_in"]
            + ot.get("image_tokens", u.get("output_tokens", 0)) * p["image_out"]) / 1e6

def tts_cost(u):
    p = PRICES["gpt-realtime-2"]; it = u.get("input_token_details", {}); ot = u.get("output_token_details", {})
    cached = it.get("cached_tokens", 0)
    return ((it.get("text_tokens", 0) - cached) * p["text_in"] + cached * p["text_cached_in"]
            + it.get("audio_tokens", 0) * p["audio_in"]
            + ot.get("text_tokens", 0) * p["text_out"] + ot.get("audio_tokens", 0) * p["audio_out"]) / 1e6

path = sys.argv[1] if len(sys.argv) > 1 else "costs.jsonl"
recs = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
agg = defaultdict(lambda: {"n": 0, "usd": 0.0, "detail": ""})
for r in recs:
    if r["kind"] == "image" and r.get("usage"):
        a = agg["画像生成（gpt-image-2）"]; a["n"] += 1; a["usd"] += image_cost(r["usage"])
        a["detail"] = f'{r["size"]}・quality {r["quality"]}'
    elif r["kind"] == "tts" and r.get("usage"):
        a = agg["ナレーション（gpt-realtime-2）"]; a["n"] += 1; a["usd"] += tts_cost(r["usage"])
        a["detail"] = f'計 {sum(x.get("chars", 0) for x in recs if x["kind"] == "tts")} 字（再試行を含む）'
steps = [(r["step"], r.get("wall_s")) for r in recs if r["kind"] == "step" and r.get("wall_s") is not None]

print("| 工程 | 回数 | 費用（USD） | 条件 |\n|---|---:|---:|---|")
total = 0.0
for k, a in agg.items():
    total += a["usd"]; print(f'| {k} | {a["n"]} | ${a["usd"]:.3f} | {a["detail"]} |')
print(f"| **合計** | | **${total:.3f}** | |\n")
print("| 工程 | 実時間（秒） |\n|---|---:|")
for s, w in steps: print(f"| {s} | {w} |")
print(f"\n単価の出典: {SOURCES}")

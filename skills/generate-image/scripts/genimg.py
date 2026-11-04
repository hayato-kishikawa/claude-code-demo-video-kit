#!/usr/bin/env python3
"""gpt-image-2.5 / gpt-image-2（Azure OpenAI または OpenAI API）で画像生成。単発 or JSONジョブでバッチ。429リトライ・任意アップスケール対応。

使い方:
  # 単発
  python genimg.py --prompt "..." --name hero --out-dir ./out [--size 2048x1152] [--quality high] [--style "..."]
  # バッチ（JSONジョブ）
  python genimg.py --job job.json [name1 name2 ...]   # 末尾に名前を並べると対象を絞れる

環境変数:
  PROVIDER                azure（既定）| openai
  AZURE_OPENAI_BASE_URL   例: https://<resource>.openai.azure.com/openai/v1（PROVIDER=azure）
  AZURE_OPENAI_API_KEY
  OPENAI_API_KEY          PROVIDER=openai のとき。OPENAI_BASE_URL 省略時 https://api.openai.com/v1
  IMAGE_DEPLOYMENT        省略時 gpt-image-2.5-flare（Azure ではデプロイ名）。精度優先なら gpt-image-2.5-sunburst

サイズ: gpt-image-2 系はネイティブで最大3840pxまで可（16の倍数・比率≤3:1・総ピクセル 655,360〜8,294,400）。
  よく使う: 1024x1024 / 1536x1024 / 1024x1536 / 2048x1152(2K横) / 2048x2048 / 3840x2160(4K横)
  ヒーロー等で2000px+が要るときは 2048x1152 等で直接生成する（upscale_width での拡大は補間なので非推奨・保険）。
quality: low | medium | high | auto。文字の多い図/最終版は high、下書きは low（速い）。

JSONジョブ形式:
  {
    "out_dir": "生成先ディレクトリ",
    "size": "2048x1152",            // 任意
    "quality": "high",              // 任意: low|medium|high|auto（images側で個別指定も可）
    "upscale_width": null,           // 任意: PIL拡大（基本不要。ネイティブ大サイズを優先）
    "deployment": "gpt-image-2.5-flare",  // 任意
    "style": "共通スタイル接頭辞 …", // 任意: 各 prompt の先頭に付与
    "images": [ {"name": "kv1", "prompt": "…", "quality": "high"}, … ]
  }
"""
import argparse, base64, io, json, os, sys, time, urllib.error, urllib.request


def _env():
    if os.environ.get("PROVIDER", "azure").lower() == "openai":
        base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        key = os.environ.get("OPENAI_API_KEY", "")
    else:
        base = os.environ.get("AZURE_OPENAI_BASE_URL", "").rstrip("/")
        key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    if not base or not key:
        sys.exit("ERROR: 接続先と鍵を環境変数に設定してください（.env.example を参照し "
                 "`set -a; . ./.env; set +a`）")
    return base, key


def _post(url, body, key):
    auth = ({"Authorization": "Bearer " + key} if os.environ.get("PROVIDER", "azure").lower() == "openai"
            else {"api-key": key})
    req = urllib.request.Request(url, data=body, method="POST",
        headers={**auth, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def generate(name, prompt, out_dir, size, deployment, upscale_width, base, key, quality=None):
    payload = {"model": deployment, "prompt": prompt, "size": size, "n": 1}
    if quality:                      # low | medium | high | auto（文字の多い図は high、下書きは low）
        payload["quality"] = quality
    body = json.dumps(payload).encode()
    url = f"{base}/images/generations"
    data = None
    for attempt in range(6):
        try:
            data = _post(url, body, key); break
        except urllib.error.HTTPError as e:
            if e.code == 429:                     # レート制限 → 指数バックオフ
                w = 20 * (attempt + 1)
                print(f"  429 {name}: backoff {w}s (attempt {attempt+1})", flush=True)
                time.sleep(w); continue
            # v1エンドポイントで api-version が要る場合の一度きりリトライ
            data = _post(url + "?api-version=preview", body, key); break
    if data is None:
        raise RuntimeError("429 exhausted")
    raw = base64.b64decode(data["data"][0]["b64_json"])
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name + ".png")
    if upscale_width:
        from PIL import Image
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        if im.width < upscale_width:
            im = im.resize((upscale_width, round(im.height * upscale_width / im.width)), Image.LANCZOS)
        im.save(path, "PNG")
        w, h = im.width, im.height
    else:
        with open(path, "wb") as f:
            f.write(raw)
        w = h = "?"
    print(f"OK {path} {w}x{h} {os.path.getsize(path)//1024}KB", flush=True)
    return {"path": path, "size": size, "quality": quality, "model": deployment, "usage": data.get("usage")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job")
    ap.add_argument("--prompt")
    ap.add_argument("--name", default="image")
    ap.add_argument("--out-dir", default="./out")
    ap.add_argument("--size", default="1536x1024")
    ap.add_argument("--quality", default=None, choices=["low", "medium", "high", "auto"])
    ap.add_argument("--upscale-width", type=int, default=0)
    ap.add_argument("--style", default="")
    ap.add_argument("--deployment", default=os.environ.get("IMAGE_DEPLOYMENT", "gpt-image-2.5-flare"))
    ap.add_argument("only", nargs="*", help="JSONジョブで生成対象を名前で絞る（任意）")
    a = ap.parse_args()
    base, key = _env()

    if a.job:
        spec = json.load(open(a.job, encoding="utf-8"))
        out_dir = spec["out_dir"]
        size = spec.get("size", "1536x1024")
        up = spec.get("upscale_width") or 0
        dep = spec.get("deployment", a.deployment)
        style = spec.get("style", "")
        quality = spec.get("quality")
        targets = set(a.only) if a.only else None
        for it in spec["images"]:
            if targets and it["name"] not in targets:
                continue
            try:
                generate(it["name"], style + it["prompt"], out_dir, size, dep, up, base, key,
                         quality=it.get("quality", quality))
            except Exception as e:
                print(f"FAIL {it['name']}: {e}", flush=True)
            time.sleep(8)   # レート制限回避のため間隔を空ける
    else:
        if not a.prompt:
            sys.exit("ERROR: --prompt か --job のどちらかが必要です")
        generate(a.name, a.style + a.prompt, a.out_dir, a.size, a.deployment, a.upscale_width,
                 base, key, quality=a.quality)


if __name__ == "__main__":
    main()

---
name: generate-image
description: Generate images with gpt-image-2.5 (flare / sunburst) or gpt-image-2 via Azure OpenAI or the OpenAI API (single or batch). Use whenever the user wants to create/generate images, illustrations, hero/key visuals, article挿絵, diagrams, infographics, mockups, or icons from a text description — including Japanese-labeled figures and wide hero banners. Handles structured prompt design, quality/size selection, 429 retry, and native high-resolution output. Do NOT use for simple shapes/diagrams/icons that are better authored directly as SVG/HTML/CSS, or for extending an existing repo SVG/vector icon system.
---

# generate-image

`gpt-image-2.5-flare`（既定）／`gpt-image-2.5-sunburst`（精度優先）／`gpt-image-2`（Azure OpenAI または OpenAI API）で画像を生成するスキル。2.5 は単価が同じで 1 枚の出力トークンが 2 の約 4 分の 1（費用も 4 分の 1）、生成も約 2.5 倍速かった（2048×1152・high で実測）。記事の挿絵・図版・インフォグラフィック・ヒーロー(キービジュアル)・モックアップ・アイコンなどをテキストから作る。

## 使う / 使わない

**使う**: 写真調・イラスト・インフォグラフィック・バナー/ヒーロー・製品モックアップ・多数バリエーション。ビットマップ資産が欲しいとき。
**使わない**:
- 単純な図形・ワイヤーフレーム・アイコンで **SVG/HTML/CSS で直接描いた方が正確**なもの。
- リポジトリ既存の SVG/ベクターのアイコン/ロゴ体系を拡張・整合させる作業（元ファイルを直接編集）。
- **長文・長いラベルが主役**の図（段落や長い説明文が多いもの）。長文は化けやすく SVG/mermaid の方が確実。
  ※「箱数が多い密なインフォグラフィック」でも**各ラベルが短ければ** gpt-image-2 で十分実用（下記「実績」参照）。**密＝不可ではなく、長文＝不可**。密な図はラベルを単語〜短句に割れば通る。

## 前提（初回だけ）

1. **Azure の場合は画像デプロイ** `gpt-image-2.5-flare` が要る（OpenAI API なら不要）。無ければ作る:
   ```bash
   az cognitiveservices account list-models -n <resource> -g <rg> \
     --query "[?contains(name,'image')].{name:name,version:version}" -o table
   az cognitiveservices account deployment create -n <resource> -g <rg> \
     --deployment-name gpt-image-2.5-flare --model-name gpt-image-2.5-flare --model-version 2026-09-08 \
     --model-format OpenAI --sku-name GlobalStandard --sku-capacity 10
   ```
   容量が小さい(1)と 429 が多発 → 10 程度に。
2. **認証**はリポ直下の `.env`（`.env.example` を参照）。`PROVIDER=azure` なら `AZURE_OPENAI_BASE_URL`(`.../openai/v1`) と `AZURE_OPENAI_API_KEY`、`PROVIDER=openai` なら `OPENAI_API_KEY`。実行前に読む:
   ```bash
   set -a; . ./.env; set +a
   ```
3. `Pillow` は upscale 時のみ必要（基本ネイティブ大サイズで不要）。

## サイズと quality（重要）

- **サイズ**: gpt-image-2 はネイティブ最大 **3840px**（gpt-image-2 で確認。2.5 は 2048×1152 だけ確認）（各辺16の倍数・長短比≤3:1・総ピクセル 655,360〜8,294,400）。
  - 記事図版: `1536x1024`
  - ヒーロー/2K: `2048x1152`（横2000px超が要るときはこれで**直接生成**。PIL拡大より高品質）
  - 4K: `3840x2160`
  - 正方形の下書き: `1024x1024`（最速）
- **quality**: `low`|`medium`|`high`|`auto`。
  - `low` … 下書き・サムネ・素早い反復（速い / 実測 ~12s）
  - `high` … 最終版・**文字の多い図/ダイアグラム**・高解像度（実測 ~64s）
- 透過PNGは gpt-image-2 非対応（2.5 は未確認）（`background=transparent` 不可）。必要なら「単色クロマキー背景で生成→ローカルで透過化」か、`gpt-image-1.5` を要相談。

## 使い方

スクリプト: `scripts/genimg.py`。

### 単発
```bash
set -a; . ./.env; set +a
python3 skills/generate-image/scripts/genimg.py \
  --prompt "<英語で構図・スタイル、日本語ラベルは短く正確に>" \
  --name my_image --out-dir out/images --size 1536x1024 --quality high
```

### バッチ（推奨: JSONジョブ）
```json
{
  "out_dir": "out/article",
  "size": "1536x1024",
  "quality": "high",
  "style": "Clean corporate flat vector, white background, navy/teal/green palette, Japanese labels correct. ",
  "images": [
    {"name": "fig1", "prompt": "..."},
    {"name": "fig2", "prompt": "..."}
  ]
}
```
```bash
set -a; . ./.env; set +a
python3 skills/generate-image/scripts/genimg.py --job job.json
python3 skills/generate-image/scripts/genimg.py --job job.json fig2   # 一部だけ再生成
```

### ヒーロー(2K)
```json
{ "out_dir": "out/hero", "size": "2048x1152", "quality": "high",
  "style": "Cinematic premium dark-navy tech hero, glowing cyan accents, keep lower-left dark for title overlay. No large text. ",
  "images": [ {"name":"kv1","prompt":"..."} ] }
```

### 実行のコツ
- 1枚 ~12s(low)〜64s(high)。Bash ツールは2分で切れるので **3枚以上はバックグラウンド実行**し完了通知を待つ。
- **並列で速くする**：`--job job.json`（引数なし）は**画像を逐次生成**する。急ぐときは画像ごとに `--job job.json <name>` を**別々のバックグラウンドジョブとして同時起動**する（gpt-image-2 側は並列リクエストを捌ける。capacity 10 なら数枚同時でも 429 は出にくい）:
  ```bash
  # 画像ごとに独立したバックグラウンドジョブで起動（推奨）
  python3 .../genimg.py --job job.json fig3   # 別ジョブ
  python3 .../genimg.py --job job.json fig4   # 別ジョブ
  ```
  ⚠️ **1つのラッパーshellで `nohup ... & ; nohup ... &` とまとめない**。親shellが終了すると子プロセスが巻き込まれて落ちる（実測 exit 144・logが空）。**画像ごとに独立したジョブ**にすること。
- **バリエーション生成**：迷ったら1案でなく**複数版を1ジョブに並べて作り比較**する。粒度違い（粗い/中間/詳細）、スタイル違い、構図違いなど。`images[]` に並べて一括、または上記の並列で同時に。目視で当たりを選び、外れだけ prompt を直して**その名前で再生成**。
- 生成後は必ず **`Read` で PNG を目視**（文字化け・意図ズレ・構図）。ダメなら prompt を直し、その名前だけ再生成。

## プロンプト設計

### 特異度ポリシー
- ユーザーの指示が**具体的なら整形のみ**（勝手に要素・ブランド・色を足さない）。
- **汎用なら、質を実質的に上げる分だけ**構図・用途・レイアウトを補う。

### 構造化スキーマ（必要な行だけ使う）
```
Use case: <infographic-diagram | ui-mockup | product-mockup | ads-marketing | illustration-story | logo-brand | stylized-concept ...>
Asset type: <どこで使う: 記事ヒーロー/挿絵/スライド図 等>
Subject: <主題>
Style/medium: <flat vector / premium dark tech / 3D 等>
Composition: <wide/close、要素配置、タイトル余白の位置>
Color palette: <配色>
Text (verbatim): "<図中に入れる文言をそのまま>"
Constraints / Avoid: <必須 / 禁止（例: no large text, no watermark）>
```

### 実務のコツ
- **構図・スタイルは英語**が効く。共通トーンは `style` 接頭辞に括り出すと統一感が出る。
- **日本語ラベルは（短ければ）密でも正確に出る**。6段＋分岐＋各箱4〜5行の詳細インフォグラフィックでも `2048x1152`/`high` で実質文字化けなしを確認済み。化けるのは**1ラベルが長文**のとき → 図中文言は prompt にそのまま日本語で明記し、**各ラベルを単語〜短句に割る**（長い一文にしない）。解像度は大きめ（2048px〜）＋`high` が効く。
- **汎用ストック画を避ける**: 「AI・青・光るデータ」だけだと"どの記事でも使える"絵になる。**そのコンテンツ固有の語・構造**（例：画面の用語、実データ表、記事の具体例）をラベル・要素に入れて内容直結にする。
- **ヒーロー**: タイトルを CMS で重ねるなら「一角を暗く＝タイトル余白を残す」「大きな文字を入れない」を明示。
- **反復は1回1変更**で。効いたか都度 `Read` で確認。

## 完了時の報告
保存パス・**最終プロンプト**・使ったサイズ/quality を必ず伝える。プロジェクトで使う画像はワークスペース内（例 `assets/gen/`）に保存し、一時領域に置きっぱなしにしない。

## 実績
6 段＋分岐＋各箱 4〜5 行の日本語ラベルを持つ詳細なデータフロー図でも、`2048x1152`・`high` で文字化けせずに出た。「密な図でも各ラベルを短くすれば実用」の裏付け。写実の素材は `examples/meetroom-30s/assets/gen/_input/job_live.json` が実例。

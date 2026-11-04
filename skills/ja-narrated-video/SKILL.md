---
name: ja-narrated-video
description: HyperFrames で日本語ナレーション付きの展示・商談用デモ動画（30〜180 秒、1920×1080）を作る／直す。gpt-image-2.5 で写実の素材を作り、自作画面をヘッドレス Chrome で撮り、gpt-realtime-2.1 を TTS に使い、無音検出でナレーション全文の字幕を付け、check→render→抜き出しコマで検証する。新しいデモ動画・字幕・ナレーション録り直し・レンダの依頼を受けたときに使う。
---

# ja-narrated-video

展示会・商談向けのデモ動画を何本も作って通ったパイプラインと、依頼者レビューで固まった編集方針。HyperFrames の一般手順（`/hyperframes`）より本スキルを優先する。

## いつ使わないか
- 英語のみ・ナレーションなしの短いモーショングラフィック → HyperFrames の `/motion-graphics`
- 既存の実写 MP4 に字幕を焼く → HyperFrames の `/embedded-captions`

## 始める前に（必須）
1. 依頼者に確認する（リポ直下の `AGENTS.md`「着手前の確認」）：接続先と費用、尺、見る人と流す場所、出してよい名称、BGM の権利、**テイスト**（[references/taste.md](references/taste.md) のプリセット calm／saas-bright から選んでもらう）。
2. 対象プロジェクトの `BRIEF.md`（`## vN` 節に過去の判断）と `STORYBOARD.md` を読む。無ければ作る（雛形は `examples/meetroom-30s/`）。
3. [references/editorial-rules.md](references/editorial-rules.md) を読む。BRIEF.md に書かれた禁止事項に反する提案はしない。
4. `.env` を読み込む: `set -a && . <repo>/.env && set +a`。画像生成と TTS はこれ無しで止まる。
5. `SK=<repo>/skills/ja-narrated-video/scripts`、`PY=<repo>/.venv/bin/python` として、スクリプトはコピーせずここから呼ぶ。**プロジェクト直下で実行する**（相対パスと `costs.jsonl` の置き場所がそろう）。

## 手順

```
① 構成    BRIEF.md → STORYBOARD.md（コマ・尺・ナレーション・画像）
② 素材    実画面: 画面を HTML で作り chrome-headless-shell で 2 倍撮影（shoot_ui.sh）
          写真  : 画像ジョブ JSON → $PY $SK/run_images.py job.json（1 場面 2 案、10 並列）
                  → $PY $SK/contact_sheet.py assets/gen "" sheet.jpg → Read で選定
③ 音声    assets/voice/lines.json → $PY $SK/gen_voice.py assets/voice marin
④ 字幕    $PY $SK/build_captions.py assets/voice --hard 30
⑤ BGM     python3 $SK/gen_bgm.py assets/bgm（torch が要る）→ $PY $SK/make_bed.py <total> <turn>
⑥ 組み    .hyperframes/build_frames_<video>.py（$SK/build_frames.py を import）→ コマ HTML と index_config.json
          $PY $SK/build_index.py index_config.json → index.html
⑦ 検証    npm run check（0 error）→ npm run render → $SK/sample_frames.py → ebur128
⑧ 記録    $SK/export_srt.py → renders/<name>.ja.srt、$SK/cost_report.py、STORYBOARD/BRIEF 更新、旧版を renders/<name>_vN.mp4 へ
```

テイスト（地と光、被写体、実画面の見せ方、文字、動き、転換、音、声）の決め方と変える場所は [references/taste.md](references/taste.md)。各段の細部（レイヤのキー、字幕規則、BGM 音量、render コマンド）は [references/authoring.md](references/authoring.md)。画像のスタイル接頭辞は [references/style-prefixes.md](references/style-prefixes.md)。完成形の時間割とコマ仕様は [references/worked-example.md](references/worked-example.md)。

## 判断のしかた（ここだけは本文に置く）
- **画面の文字は字幕に一元化。** 見出しテロップ・左上の常駐ラベルは作らない。字幕は 1 行 30 字以内。
- **共感を狙うコマは写実写真の人の様子で。** 動詞だけの概念図は伝わらない。伏線回収は同一画像の再利用で。
- **数字は画像に焼かない。** 画像生成は数字や長いラベルが化ける。数字は実画面か HTML で出す。
- **固有名の読みは表記で制御し、依頼者の耳で選ぶ。** 4〜6 take 並べて番号で選んでもらう。判定モデルは当てにならない。
- **主張は事実の範囲で。** 他社製品の挙動を断定しない。実画面に実データ・内部名を出さない。
- **修正は「批判的な見直し → 反映」の順。** 直す前に現状の問題点を列挙し、BRIEF.md の `## vN` 節に「指示 → 反映 → 不採用と理由」を残す。

## 詰まったら
[references/pitfalls.md](references/pitfalls.md)。依存の入っていない Python、スクショの下端欠け、レンダのディスク不足、`pkill -f` で自分のシェルを殺す、カバー矩形が見える、字幕が 2 行になる、児童を含む画像が 400、など既知の症状はすべてここに対処がある。

## スクリプト一覧（`scripts/`）
| ファイル | 用途 |
|---|---|
| `_client.py` | 接続先の切り替え（`PROVIDER=azure|openai`）と実測ログ `costs.jsonl` への追記 |
| `run_images.py` | ジョブ JSON を gpt-image-2.5 で並列生成（ジョブの `deployment` でモデルを指定）（`skills/generate-image/scripts/genimg.py` を使用） |
| `contact_sheet.py` / `sample_frames.py` | 画像一覧／レンダ結果の抜き出しシート（Read で目視） |
| `rt_tts.py` / `gen_voice.py` | gpt-realtime-2.1 で TTS、照合・整音・voice_meta.json（`REUSE_RAW=1` で整音だけやり直し） |
| `rt_listen.py` | 音声を gpt-realtime-2.1 に聞かせて採点（参考値） |
| `build_captions.py` / `export_srt.py` | 字幕チャンク＋無音スナップ／SRT 書き出し |
| `build_frames.py` | `build_frame()` ライブラリ（KB・パンチイン・カバー・ハイライト・吹き出し・カード） |
| `build_index.py` | 設定 JSON から index.html（スロット・転換・音声・字幕・BGM） |
| `gen_bgm.py` / `make_bed.py` | MusicGen small で BGM の素材 2 本／尺に合わせたベッド |
| `cost_report.py` | `costs.jsonl` から工程別の費用・時間の表を作る |

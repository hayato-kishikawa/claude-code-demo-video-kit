# AGENTS.md（AI エージェント向けの手順）

このリポジトリは、Claude Code などのコーディングエージェントが **日本語ナレーション・字幕・BGM 付きのデモ動画（1920×1080 の mp4）** を作るための道具一式です。
解説記事：`articles/claude-code-demo-video-hyperframes.md`（Zenn）。完成例：`examples/meetroom-30s-saas/`（架空の会議室予約 SaaS「ヘヤマド」の約 30 秒動画、明るい SaaS 調）と、同じ題材の落ち着いた説明調 `examples/meetroom-30s/`。

## 1. 着手前に、利用者へ必ず確認すること

勝手に進めず、次の 7 点を利用者に聞いてから始めてください。API の費用が発生し、生成物の権利にも関わります。

| 確認すること | 選択肢・目安 |
|---|---|
| 接続先 | Azure OpenAI（作者が実測）か OpenAI API（コード上は対応・作者は未検証）。必要なモデルは `gpt-image-2.5-flare`（精度優先なら `gpt-image-2.5-sunburst`）と `gpt-realtime-2.1` の 2 つ。Azure ならデプロイ済みか、クォータに空きがあるか |
| API 費用 | 約 30 秒・立体の小物 4 枚・写真 2 枚・ナレーション 7 行で **約 0.31 米ドル**（`docs/costs.md`）。画像は 2048×1152・high で 1 枚 約 0.044 ドル。ナレーションは 1 行につき照合のため最大 3 回まで自動で録り直すので、その分も含めて伝える。作り直すたびに増える |
| 所要時間 | 生成 API の待ちは合計 約 1 分。レンダは 30 秒動画で 約 1 分。CPU で BGM を作ると 約 6 分。作者の実測では、明るい SaaS 調の版でブリーフから完成まで 約 15 分（修正と再レンダ 1 回を含む。画面 4 枚の HTML はすでにあった）|
| 動画の中身 | 誰に・どこで流すか（展示会のループか商談の冒頭か）、尺、言いたいこと 1 つ、出してよい社名・製品名・固有名 |
| テイスト | 落ち着いた説明調（calm）か、明るい SaaS のローンチ調（saas-bright）か。近い既存の動画や LP、避けたいもの（ダーク、ネオン、顔など）。`skills/ja-narrated-video/references/taste.md` |
| 素材の権利 | 実画面を撮る対象は利用者に権利があるか。他社サイトやロゴは使わない |
| BGM | 既定の MusicGen は重みが **CC-BY-NC 4.0（非商用）**。商用の動画なら、利用者が用意したロイヤリティフリー音源に差し替えるか BGM なしにする |

ライセンスの一覧：HyperFrames は Apache-2.0、同梱フォント（Noto Sans JP・IBM Plex Mono）は SIL OFL 1.1、このリポのコードは MIT（`gen_bgm.py` の一部は HyperFrames 由来で Apache-2.0。`THIRD_PARTY_NOTICES.md`）。HyperFrames のエージェント用スキルは同梱していない。生成した画像・音声の扱いは各 API の利用規約に従う。

## 2. 環境

| 要るもの | 確認コマンド |
|---|---|
| Node.js 20 以上（HyperFrames を `npx hyperframes@0.8.30` で使う） | `node -v` |
| ffmpeg / ffprobe | `ffmpeg -version` |
| Python 3.10 以上 | `python3 --version` |
| Chrome 系ブラウザ（HyperFrames が初回に chrome-headless-shell を自動で取得する） | （自動） |
| BGM を作る場合だけ：torch と transformers（モデル 約 2.4GB） | `requirements-bgm.txt` |

```bash
git clone <this repo> && cd claude-code-demo-video-kit
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
# BGM を MusicGen で作る場合だけ（重い。同じ .venv に入れる）
# .venv/bin/pip install -r requirements-bgm.txt
cp .env.example .env   # 接続先と鍵を埋める
# レンダと撮影に使う chrome-headless-shell を先に取得しておく（完成例で check を 1 回回すと入る）
(cd examples/meetroom-30s-saas && npm run check)
```

Claude Code で使う場合は、スキルをプロジェクトに置きます。

```bash
mkdir -p .claude/skills && cp -r skills/ja-narrated-video skills/generate-image .claude/skills/
```

## 3. 手順

詳細は `skills/ja-narrated-video/SKILL.md`。新しい動画は、テイストに近い例を丸ごとコピーして始めるのが早いです。

| テイスト | コピー元 | 画像ジョブ | コマのビルダー |
|---|---|---|---|
| 明るい SaaS 調（saas-bright、記事の題材） | `examples/meetroom-30s-saas/` | `assets/gen/_input/job_obj.json`、`job_photo.json`（出力先 `assets/gen/flare/`） | `.hyperframes/build_frames_saas.py` |
| 落ち着いた説明調（calm） | `examples/meetroom-30s/` | `assets/gen/_input/job_flare.json`（出力先 `assets/gen/flare/`） | `.hyperframes/build_frames_meetroom.py` |

```bash
cp -r examples/meetroom-30s-saas examples/<name> && cd examples/<name>
# 生成物を消す（入力の JSON と画面の HTML、フォントは残す）。同名の画像があると生成をスキップするので必ず消す
rm -rf assets/gen/flare assets/gen/gpt-image-2 assets/gen/sunburst assets/ui/* assets/voice/*.wav assets/voice/voice_meta.json assets/voice/captions.json assets/bgm/* renders/* costs.jsonl
set -a && . ../../.env && set +a
SK=../../skills/ja-narrated-video/scripts; PY=../../.venv/bin/python
```

コピー後に書き換えるもの（SaaS 版のビルダーの場合）：画像のパス、冒頭の大きな文字（`kinetic()` の行）、締めの製品名とロゴ、件数のカウントアップの数値と文言、カードを寄せる位置。字幕キューの開始時刻に合わせる演出は、キューが足りなければ音声の長さの割合で代わりの時刻を使う。

1. `BRIEF.md`（`taste:` を含む）と `STORYBOARD.md` を書き、利用者に見せる。
2. 実画面：`site/` に画面を作り `.hyperframes/shoot_ui.sh` で撮る（または利用者の製品画面を撮る。映してはいけない情報は撮る前にダミーデータに差し替える。カードで画角から外すだけでは元画像に残る）。
3. 素材：画像ジョブを書き換え `$PY $SK/run_images.py <job>.json …`。`$PY $SK/contact_sheet.py assets/gen/flare "" sheet.jpg` を見て選ぶ。ジョブの `deployment` は環境変数 `IMAGE_DEPLOYMENT` より優先される。
4. 音声：`assets/voice/lines.json` を書き `TTS_STYLE="…" $PY $SK/gen_voice.py assets/voice marin` → `$PY $SK/build_captions.py assets/voice --hard 30`（30 字を超えるキューは警告が出る。台本を直す）。`WARN mismatch kept` が出た行は聞いて確かめる。
5. BGM の素材（時間がかかるので早めに裏で）：`$PY $SK/gen_bgm.py assets/bgm upbeat`（calm なら `calm`）。商用なら MusicGen を使わず、利用条件を確かめた音源を `assets/bgm/seed_a.wav`・`seed_b.wav` に置く。BGM なしなら `index_config.json` の `bgm` を `null` にする。
6. 組み：ビルダーを題材に合わせて書き換えて実行（`index_config.json` ができる）→ `$PY $SK/make_bed.py index_config.json`（総尺と切替秒を設定から読む）→ `$PY $SK/build_index.py index_config.json`。
7. 検証：`npm run check`（0 error）→ `npm run render` → 出力はタイムスタンプ付きの名前なので `mv "$(ls -t renders/*_20*.mp4 | head -1)" renders/<name>.mp4` → `$PY $SK/sample_frames.py renders/<name>.mp4 sheet.jpg <各シーンの中ほどの秒> …` を目視。
8. 記録：`$PY $SK/export_srt.py assets/voice index.html renders/<name>.ja.srt`、`$PY $SK/cost_report.py > ../../docs/costs-<name>.md`、check の結果と `ebur128` の統合ラウドネスを `renders/<name>.qa.txt` に残す。

## 4. 完了の条件

- `npm run check` が 0 error、Contrast が全件合格
- 抜き出したフレームで、字幕が全キュー 1 行、カバー矩形や画面端の欠けが見えない（写真のシーンと締めも含める）
- 音量が −16〜−12 LUFS（`ffmpeg -i renders/x.mp4 -af ebur128 -f null - 2>&1 | grep "I:"`）
- 利用者に、mp4・SRT・費用の実測・未確認の点（発音、名称、権利）を報告した

## 5. やってはいけないこと

- `.env` や鍵をコミットしない。ログに鍵を出さない。
- 実在の企業・人物・サービスに見えるもの（ロゴ、サイトの模写、実在人物の顔）を作らない。
- 利用者の確認なしに API を大量に呼ばない（作り直しは 1 回ずつ、自動の録り直しを含めた費用の目安を伝えてから）。

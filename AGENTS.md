# AGENTS.md（AI エージェント向けの手順）

このリポジトリは、Claude Code などのコーディングエージェントが **日本語ナレーション・字幕・BGM 付きのデモ動画（1920×1080 の mp4）** を作るための道具一式です。
解説記事：`articles/claude-code-demo-video-hyperframes.md`（Zenn）。完成例：`examples/meetroom-30s/`（架空の会議室予約 SaaS「ヘヤマド」の 30 秒動画）。

## 1. 着手前に、利用者へ必ず確認すること

勝手に進めず、次の 6 点を利用者に聞いてから始めてください。API の費用が発生し、生成物の権利にも関わります。

| 確認すること | 選択肢・目安 |
|---|---|
| 接続先 | Azure OpenAI（作者が実測）か OpenAI API（コード上は対応・作者は未検証）。必要なモデルは `gpt-image-2.5-flare`（精度優先なら `gpt-image-2.5-sunburst`）と `gpt-realtime-2.1` の 2 つ。Azure ならデプロイ済みか、クォータに空きがあるか |
| API 費用 | 30 秒・写真 4 枚・ナレーション 7 行で **約 0.23 米ドル**（`docs/costs.md`）。画像は 2048×1152・high で 1 枚 約 0.044 ドル。作り直すたびに増える |
| 所要時間 | 生成 API の待ちは合計 約 1 分。レンダは 30 秒動画で 約 80 秒。CPU で BGM を作ると 約 6 分。作者の実測では、画面 4 枚の作成と修正 2 回を含めて 約 20 分 |
| 動画の中身 | 誰に・どこで流すか（展示会のループか商談の冒頭か）、尺、言いたいこと 1 つ、出してよい社名・製品名・固有名 |
| 素材の権利 | 実画面を撮る対象は利用者に権利があるか。他社サイトやロゴは使わない |
| BGM | 既定の MusicGen は重みが **CC-BY-NC 4.0（非商用）**。商用の動画なら、利用者が用意したロイヤリティフリー音源に差し替えるか BGM なしにする |

ライセンスの一覧：HyperFrames は Apache-2.0、同梱フォント（Noto Sans JP・IBM Plex Mono）は SIL OFL 1.1、このリポのコードは MIT。生成した画像・音声の扱いは各 API の利用規約に従う。

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
# BGM を MusicGen で作る場合だけ（重い）
# .venv/bin/pip install -r requirements-bgm.txt
cp .env.example .env   # 接続先と鍵を埋める
```

Claude Code で使う場合は、スキルをプロジェクトに置きます。

```bash
mkdir -p .claude/skills && cp -r skills/ja-narrated-video skills/generate-image .claude/skills/
```

## 3. 手順

詳細は `skills/ja-narrated-video/SKILL.md`。新しい動画は `examples/meetroom-30s/` を丸ごとコピーして始めるのが早いです。

```bash
cp -r examples/meetroom-30s examples/<name> && cd examples/<name>
rm -rf assets/gen/*.png assets/ui/* assets/voice/*.wav assets/bgm/* renders/* costs.jsonl
set -a && . ../../.env && set +a
SK=../../skills/ja-narrated-video/scripts; PY=../../.venv/bin/python
```

1. `BRIEF.md` と `STORYBOARD.md` を書き、利用者に見せる。
2. 実画面：`site/` に画面を作り `.hyperframes/shoot_ui.sh` で撮る（または利用者の製品画面を撮る）。
3. 写真：`assets/gen/_input/job_flare.json` を書き換え `$PY $SK/run_images.py assets/gen/_input/job_flare.json`。`$PY $SK/contact_sheet.py assets/gen/flare "" sheet.jpg` を見て選ぶ。
4. 音声：`assets/voice/lines.json` を書き `$PY $SK/gen_voice.py assets/voice marin` → `$PY $SK/build_captions.py assets/voice --hard 30`。
5. BGM：`python3 $SK/gen_bgm.py assets/bgm`（torch が入った Python）→ `$PY $SK/make_bed.py <総尺> <切替秒>`。
6. 組み：`.hyperframes/build_frames_meetroom.py` を題材に合わせて書き換え実行 → `$PY $SK/build_index.py index_config.json`。
7. 検証：`npm run check`（0 error）→ `npm run render` → `$PY $SK/sample_frames.py renders/<file>.mp4 sheet.jpg 1 4 7 …` を目視。
8. 記録：`$PY $SK/export_srt.py assets/voice index.html renders/<name>.ja.srt`、`$PY $SK/cost_report.py > ../../docs/costs-<name>.md`。

## 4. 完了の条件

- `npm run check` が 0 error、Contrast が全件合格
- 抜き出したコマで、字幕が全キュー 1 行、カバー矩形や画面端の欠けが見えない
- 音量が −16〜−12 LUFS（`ffmpeg -i renders/x.mp4 -af ebur128 -f null - 2>&1 | grep "I:"`）
- 利用者に、mp4・SRT・費用の実測・未確認の点（発音、名称、権利）を報告した

## 5. やってはいけないこと

- `.env` や鍵をコミットしない。ログに鍵を出さない。
- 実在の企業・人物・サービスに見えるもの（ロゴ、サイトの模写、実在人物の顔）を作らない。
- 利用者の確認なしに API を大量に呼ばない（作り直しは 1 回ずつ、費用を伝えてから）。

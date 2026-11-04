# claude-code-demo-video-kit

Claude Code に、展示会や商談で流す **日本語ナレーション・字幕・BGM 付きのデモ動画（1920×1080 の mp4）** を作らせるための道具一式です。
動画は [HyperFrames](https://github.com/heygen-com/hyperframes)（HTML → mp4）で組み、素材の写真は `gpt-image-2.5-flare`、ナレーションは `gpt-realtime-2.1` で作ります。

![完成例のダイジェスト](images/claude-code-demo-video-hyperframes/digest-full.gif)

- 解説記事：[articles/claude-code-demo-video-hyperframes.md](articles/claude-code-demo-video-hyperframes.md)（Zenn）
- AI エージェント向けの手順：[AGENTS.md](AGENTS.md)
- 完成例：[examples/meetroom-30s](examples/meetroom-30s)（架空の会議室予約 SaaS「ヘヤマド」の 30 秒動画、mp4 と SRT は `renders/`）
- 費用と時間の実測：[docs/costs.md](docs/costs.md)（30 秒 1 本で API 約 0.23 米ドル）

## クイックスタート

```bash
git clone https://github.com/hayato-kishikawa/claude-code-demo-video-kit.git
cd claude-code-demo-video-kit
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env            # Azure OpenAI か OpenAI API の接続先と鍵を書く
mkdir -p .claude/skills && cp -r skills/ja-narrated-video skills/generate-image .claude/skills/
```

そのうえで Claude Code に、たとえば次のように頼みます。

```text
skills/ja-narrated-video を使って、<製品名> の 30 秒のデモ動画を作りたい。
見る人は <誰>、流す場所は <展示会ブース／商談の冒頭>。まず BRIEF.md と STORYBOARD.md を書いて見せて。
```

完成例だけをレンダし直すなら、API の鍵は要りません（素材はリポに入っています）。

```bash
cd examples/meetroom-30s && npm run check && npm run render
```

## 必要なもの

- Node.js 20 以上（`npx hyperframes@0.8.30`）、ffmpeg、Python 3.10 以上
- Azure OpenAI（`gpt-image-2.5-flare` と `gpt-realtime-2.1` のデプロイ）または OpenAI API。OpenAI API の経路はコード上は対応していますが、作者は未検証です
- BGM を MusicGen で作る場合だけ：`requirements-bgm.txt`（torch、transformers）

## ライセンス

- このリポのコードと文書：MIT（[LICENSE](LICENSE)）
- HyperFrames：Apache-2.0（npm から取得。このリポには含めていません）
- 同梱フォント（`examples/meetroom-30s/assets/fonts/`）：Noto Sans JP、IBM Plex Mono（SIL Open Font License 1.1、ライセンス文を同梱）
- 完成例の BGM（`examples/meetroom-30s/assets/bgm/`）：MusicGen small で生成。モデルの重みは CC-BY-NC 4.0 のため、非商用のサンプルとして扱ってください。商用の動画ではロイヤリティフリー音源に差し替えてください
- 完成例の写真と音声：Azure OpenAI の `gpt-image-2.5-flare` と `gpt-realtime-2.1` で生成（比較用に `gpt-image-2` と `gpt-image-2.5-sunburst` の画像も `assets/gen/` に同梱）
- 「ヘヤマド」は記事のために作った架空のサービスです。実在の企業・製品とは関係ありません

# 第三者の著作物と権利表示

このリポジトリのコードと文書は MIT License（`LICENSE`）です。ただし、次のものは各権利者のライセンスに従います。

| 対象 | 権利者・出典 | ライセンス | 備考 |
|---|---|---|---|
| `skills/ja-narrated-video/scripts/gen_bgm.py` の一部（MusicGen の読み込み、生成した波形の取り出し、ピークの正規化） | HyperFrames（HeyGen）https://github.com/heygen-com/hyperframes の `skills/media-use/audio/scripts/lib/bgm.mjs` | Apache License 2.0（`licenses/hyperframes-Apache-2.0.txt`） | 改変あり。変更点はファイル冒頭に記載 |
| `examples/*/assets/fonts/NotoSansJP-*.ttf` | Adobe / Google（Noto Sans JP） | SIL Open Font License 1.1（同じフォルダの `OFL-NotoSansJP.txt`） | 改変なし |
| `examples/*/assets/fonts/IBMPlexMono-*.ttf` | IBM（IBM Plex Mono） | SIL Open Font License 1.1（同じフォルダの `OFL-IBMPlexMono.txt`） | 改変なし |
| `examples/*/assets/bgm/` の音声と、それを含む `examples/*/renders/*.mp4` | MusicGen small（Meta）で生成 | モデルの重みは CC-BY-NC 4.0（生成した音声そのものへの適用関係は未確認） | 非商用のサンプルとして扱う。商用の動画では音源を差し替えて再レンダする |
| GSAP（`index.html` が CDN から読み込む gsap@3.14.2） | GreenSock / Webflow | Standard "No Charge" GSAP License（2025-04-30 発効。商用利用も無料。ノーコードのアニメーション作成ツールへの組み込みなど一部の用途に制限） | リポジトリには同梱していない |
| `images/claude-code-demo-video-hyperframes/hero.jpg` | Azure OpenAI の gpt-image-2 で生成（ジョブは同じフォルダの `_gen/job_hero.json`） | 各サービスの利用規約に従う | 記事の差し絵 |
| `images/claude-code-demo-video-hyperframes/studio.jpg` | HyperFrames（HeyGen）のプレビュー画面のスクリーンショット | HyperFrames は Apache-2.0 | 記事の説明用 |
| `examples/*/assets/gen/`、`examples/*/assets/voice/` | Azure OpenAI の gpt-image-2 系・gpt-realtime-2 系で生成 | 各サービスの利用規約に従う | |

HyperFrames 本体と、HyperFrames が提供するエージェント用スキル（`npx hyperframes skills` で入るもの）は、このリポジトリには含めていません。利用者がそれぞれの配布元から取得します。

# 第三者の著作物と権利表示

このリポジトリのコードと文書は MIT License（`LICENSE`）です。ただし、次のものは各権利者のライセンスに従います。

| 対象 | 権利者・出典 | ライセンス | 備考 |
|---|---|---|---|
| `skills/ja-narrated-video/scripts/gen_bgm.py` の一部（MusicGen の読み込み、生成した波形の取り出し、ピークの正規化） | HyperFrames（HeyGen）https://github.com/heygen-com/hyperframes の `skills/media-use/audio/scripts/lib/bgm.mjs` | Apache License 2.0（`licenses/hyperframes-Apache-2.0.txt`） | 改変あり。変更点はファイル冒頭に記載 |
| `examples/*/assets/fonts/NotoSansJP-*.ttf` | Adobe / Google（Noto Sans JP） | SIL Open Font License 1.1（同じフォルダの `OFL-NotoSansJP.txt`） | 改変なし |
| `examples/*/assets/fonts/IBMPlexMono-*.ttf` | IBM（IBM Plex Mono） | SIL Open Font License 1.1（同じフォルダの `OFL-IBMPlexMono.txt`） | 改変なし |
| `examples/*/assets/bgm/` の音声 | MusicGen small（Meta）で生成 | モデルの重みは CC-BY-NC 4.0 | 非商用のサンプルとして扱う。商用の動画では差し替える |
| `examples/*/assets/gen/`、`examples/*/assets/voice/` | Azure OpenAI の gpt-image-2 系・gpt-realtime-2 系で生成 | 各サービスの利用規約に従う | |

HyperFrames 本体と、HyperFrames が提供するエージェント用スキル（`npx hyperframes skills` で入るもの）は、このリポジトリには含めていません。利用者がそれぞれの配布元から取得します。

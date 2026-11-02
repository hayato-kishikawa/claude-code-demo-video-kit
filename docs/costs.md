# 実測：30 秒動画 1 本の費用と時間

対象：`examples/meetroom-30s`（架空の会議室予約 SaaS「ヘヤマド」、29.7 秒・1920×1080・30fps・ナレーション 7 行・字幕 9 キュー・BGM 付き）。
計測日：2026-11-02。接続先：Azure OpenAI（Global 標準デプロイ、East US）。マシン：Linux VM（GPU なし）。
ログの原本は `examples/meetroom-30s/costs.jsonl`。表は `skills/ja-narrated-video/scripts/cost_report.py` で作った。

## API の費用

| 工程 | 回数 | 費用（USD） | 条件 |
|---|---:|---:|---|
| ナレーション（gpt-realtime-2） | 7 | $0.044 | 計 137 字（再試行を含む） |
| 画像生成（gpt-image-2） | 4 | $0.686 | 2048x1152・quality high |
| **合計** | | **$0.730** | |

- 画像は 2048×1152・quality high で 1 枚あたり出力 約 5,650 トークン（約 0.17 ドル）。費用のほとんどは画像。1 場面 2 案で 2 場面 = 4 枚。
- ナレーションは 1 行あたり 0.5〜0.9 セント。照合の再試行は 0 回だった。
- 記事冒頭の差し絵 1 枚（約 0.17 ドル）は動画の費用に含めていない。
- Claude Code 自体の利用料は、契約プラン（サブスクリプションか API 従量か）によるので含めていない。

## 単価（100 万トークンあたり、米ドル）

| モデル | 入力（テキスト） | 出力 |
|---|---:|---:|
| gpt-image-2 | 5.00 | 画像 30.00 |
| gpt-realtime-2 | 4.00 | テキスト 24.00 ／ 音声 64.00 |

Azure（Global 標準）と OpenAI API は同額だった。
- Azure：Azure Retail Prices API（`https://prices.azure.com/api/retail/prices`、productName `Azure OpenAI Media`、eastus、2026-05-01 発効）
- OpenAI：`https://developers.openai.com/api/docs/pricing`（2026-11-02 取得）

## 時間（実時間）

| 工程 | 秒 | メモ |
|---|---:|---|
| 実画面の撮影（4 枚） | 4 | chrome-headless-shell、2 倍解像度 |
| ナレーション（7 行） | 24 | gpt-realtime-2、直列 |
| 写真の生成（4 枚） | 74 | gpt-image-2、並列 |
| BGM の素材（28 秒×2 本） | 350 | MusicGen small を CPU で。GPU があれば大幅に短い |
| BGM のベッド | 1 | numpy |
| check | 11 | lint・layout・contrast |
| レンダ（29.7 秒） | 78 | 3 ワーカー、14.1MB |

- 生成 API の待ちは合計 約 100 秒。最も長いのは BGM（CPU）だった。
- リポを作り始めてから完成版のレンダまで 約 20 分（画面 4 枚の HTML 作成、BGM 待ち、見た目の修正と再レンダ 2 回を含む）。Claude Code が手を動かし、人は確認だけした。

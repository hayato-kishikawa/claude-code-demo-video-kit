# 実測：30 秒動画 1 本の費用と時間

対象：`examples/meetroom-30s`（架空の会議室予約 SaaS「ヘヤマド」、30.2 秒・1920×1080・30fps・ナレーション 7 行・字幕 9 キュー・BGM 付き）。
接続先：Azure OpenAI（East US）。マシン：Linux VM（GPU なし）。
ログの原本は `examples/meetroom-30s/costs.jsonl`（現行）と `.hyperframes/costs_v1_gpt-image-2.jsonl`（旧モデルでの初版）。表は `skills/ja-narrated-video/scripts/cost_report.py` で作った。

## 現行の構成（2026-11-04）

| 工程 | モデル | 回数 | 費用（USD） | 実時間 |
|---|---|---:|---:|---:|
| 写真 | gpt-image-2.5-flare（2048×1152・high、Global 標準） | 4 枚 | 0.177 | 28 秒（並列） |
| ナレーション | gpt-realtime-2.1（DataZone 標準） | 7 行・137 字 | 0.055 | 19 秒 |
| **動画 1 本の API 費用** | | | **0.232** | |

- 比較のため、同じ 4 場面を gpt-image-2.5-sunburst でも生成した（0.177 ドル、38 秒）。動画には flare を使った。
- gpt-realtime-2.1 はサブスクリプションの Global 標準の枠が他のリソースで埋まっていたため、DataZone 標準（単価が Global の 1.1 倍）でデプロイした。Global 標準なら 0.050 ドル。
- gpt-realtime-2.1 は gpt-realtime-2 より約 1 割ゆっくり読む（同じ 7 行で 23.3 秒 → 25.8 秒、話速 1.15 倍の整音後）。話速を 1.25 倍にして 23.8 秒に合わせた。

## 旧モデルとの比較（同じプロンプト・同じ 4 場面）

| モデル | 1 枚の出力トークン | 1 枚の費用 | 4 枚の実時間（並列） |
|---|---:|---:|---:|
| gpt-image-2（初版、2026-11-02） | 5,650 | 0.170 ドル | 74 秒 |
| gpt-image-2.5-flare | 1,413 | 0.044 ドル | 28 秒 |
| gpt-image-2.5-sunburst | 1,413 | 0.044 ドル | 38 秒 |

解像度はどれも 2048×1152。単価は同じで、出力トークンが 4 分の 1 になったぶん安い。
初版（gpt-image-2 ＋ gpt-realtime-2）の動画 1 本の API 費用は 0.730 ドルだった。

## 単価（100 万トークンあたり、米ドル、Global 標準）

| モデル | 入力（テキスト） | 出力 |
|---|---:|---:|
| gpt-image-2.5-flare ／ sunburst | 5.00 | 画像 30.00 |
| gpt-realtime-2.1 | 4.00 | テキスト 24.00 ／ 音声 64.00 |
| （旧）gpt-image-2 | 5.00 | 画像 30.00 |
| （旧）gpt-realtime-2 | 4.00 | テキスト 24.00 ／ 音声 64.00 |

Azure の Global 標準と OpenAI API は同額。Azure の DataZone 標準は 1.1 倍。
- Azure：Azure Retail Prices API（`https://prices.azure.com/api/retail/prices`、productName `Azure OpenAI Media`、eastus。gpt-image-2.5 は 2026-09-01、gpt-realtime-2.1 は 2026-07-01 発効）
- OpenAI：`https://developers.openai.com/api/docs/pricing`（2026-11-04 取得）

## 時間（実時間、現行の構成）

| 工程 | 秒 | メモ |
|---|---:|---|
| 実画面の撮影（4 枚） | 4 | chrome-headless-shell、2 倍解像度 |
| ナレーション（7 行） | 19 | gpt-realtime-2.1、直列 |
| 写真の生成（4 枚） | 28 | gpt-image-2.5-flare、並列 |
| BGM の素材（28 秒×2 本） | 350 | MusicGen small を CPU で（初版で計測。素材は使い回し） |
| BGM のベッド | 1 | numpy |
| check | 10 | lint・layout・contrast |
| レンダ（30.2 秒） | 79 | 3 ワーカー、14.8MB |

- 生成 API の待ちは合計 約 50 秒。最も長いのは BGM（CPU）。
- 初版（gpt-image-2）では、リポを作り始めてから完成版のレンダまで 約 20 分だった（画面 4 枚の HTML 作成、BGM 待ち、見た目の修正と再レンダ 2 回を含む）。
- Claude Code 自体の利用料は、契約プラン（サブスクリプションか API 従量か）によるので含めていない。記事冒頭の差し絵 1 枚（gpt-image-2、約 0.17 ドル）も含めていない。

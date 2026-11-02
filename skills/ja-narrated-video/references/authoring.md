# 制作の細部（コマ・ナレーション・字幕・index・BGM）

SKILL.md の手順を実行するときに開く。数値は 1920×1080 前提。

## コマ（`scripts/build_frames.py` の `build_frame`）

`build_frame(fid, dur, layers, note=None, extra_css="", extra_html="", extra_js="")`。1 レイヤ＝1 枚の画像。出力は `compositions/frames/<fid>.html` と `<fid>.motion.json`。

| キー | 役割・目安 |
|---|---|
| `img` | `assets/` からの相対（`gen/x.png`, `ui/x.jpg`） |
| `s`,`e` | 表示区間（コマ内秒）。次レイヤと 0.3〜0.5s 重ねてフェード |
| `kb=(s0,s1,dx,dy)` | Ken Burns。写真は 1.0→1.04〜1.07、図は 1.0→1.02、要素が下端に近い図は 1.0 固定 |
| `fade_in` / `fade_out_prev` | 前レイヤをフェード後に `set opacity:0`（hard kill）。前半モンタージュは 0.35、転は 0.7 |
| `punch={s,tx,ty,at,d}` | パンチイン。中心 (cx,cy) に寄せる平行移動は `t=(960-cx, 540-cy)`。端が見えない条件 `540 - S*cy < 0` かつ `540 + S*(1080-cy) > 1080`。UI の小さな文字は S=1.9〜2.0 |
| `covers=[{box,at,color?}]` | 焼き込み要素を地色矩形で隠し `at` で剥がす。順に見せる／永久に隠す（`at` を尺より後ろに） |
| `hls=[{box,at,r,off}]` | インディゴ枠のハイライト。`off` で消す |
| `paints` / `labels` | 焼き込み文言の塗りつぶし＋HTML 上書き（再生成せずに文言を変える） |
| `says=[{box:(x,y,w,fs),text,at}]` | 吹き出しカード。左上 (96,96) 幅 470〜560、fs 42 |
| `card={x,y,w,h,sx,sy,zoom}` | 画像の (sx,sy) から切り出して (x,y,w,h) に zoom 倍で表示（実画面の一部だけ見せる） |
| `ground` | カバー・塗りの地色。**必ず明示**（`#F3F4F9` など）。省略時は (960,1020) をサンプル |
| `nohl` | カバー剥がし時の枠パルスを出さない（図の順次表示向け） |
| `note=(text,s,e)` | 右上の注記ピル（IBM Plex Mono 22px, #4F5B6E）。「概念図」「デモ環境の実画面／会話は一部抜粋・待ち時間を省略」。写真コマには付けない |

締めのコマは `extra_css/html/js` でサービス名（Noto Sans JP 700 80px）→ロゴ（380px, spring-pop）→白へ 1.0s フェード。

尺の目安: ナレーション実尺 + LEAD 0.6 + 余白 0.7。写真 1 枚 2〜4s、図のブロック剥がし 1〜1.5s 間隔、吹き出しはナレーションの該当語の 0.3s 後。

## ナレーション

- `lines.json`: `[{"id":"e01","text":"読み上げ文","caption":"字幕表記(省略可)"}]`。`caption` は読みと字幕の表記を分けるとき用（例：読み「エーアイ」／字幕「AI」）。
- `python3 $SK/gen_voice.py assets/voice_v2 marin [e07 …]`。`voice_meta.json` の `path` はプロジェクト相対（`assets/voice_v2/e07.wav`）になる。**プロジェクト直下で実行する。**
- 読み速度 ≈5.5 文字/秒（ATEMPO 1.15 後）。100 字 ≈ 18s。話速は環境変数 `ATEMPO` で変える。
- 固有名の読み: 表記で制御し、複数 take を `renders/<phrase>_takes/` に並べて利用者に選ばせる。`rt_listen.py <wav>` は参考程度。
- 差し替え後は `voice_meta.json` の `duration_s` を ffprobe で更新 → `build_captions.py` → index 再生成。

## 字幕

- `python3 $SK/build_captions.py assets/voice_v2 --hard 30 --minlen 8`
- 1 行 30 字以内。「。」で割り、超える文だけ中央の「、」で再帰的に割り、8 字未満は前に寄せ、境界を無音にスナップ（±0.7s）。
- 表示: `.cap{left:240px;right:240px;bottom:62px}` + 白ピル 44px/500。`transform` は使わない。
- キュー: `tl.set(opacity:0,0)` → `fromTo` 0.14s → `to opacity:0` at `max(a+0.3, b-0.14)`。
- 帯（y 900–1018）に重なる要素は `content_overlap` で検出される。要素を `top:640px` に上げる／右上ピルへ。
- SRT: `python3 $SK/export_srt.py assets/voice_v2 index.html renders/<name>.ja.srt`

## index.html

- 新規: `python3 $SK/build_index.py index_config.json`（frames, total, voice_dir, pre 0.5, lead 0.6, bgm, bgm_keys）。転換は blur crossfade 0.5s、前のコマを PRE だけ延長して重ねる。
- 既存の手書き index（ワーカー製）: 原本を `.hyperframes/index_v1.html` に退避し、パッチスクリプトで毎回再生成。時刻の一律シフトは `data-start="T"` と `tl.*( …, T);` の末尾 T を正規表現で。字幕は `<audio id="el-vo-XX" data-start>` を起点に注入。
- 要素を消すときは各コマの `</style>` 直前に `.fid-eyebrow,.fid-telop{display:none !important;}` を注入（DOM と GSAP ターゲットは残す）。

## BGM

- シード: `python3 $SK/gen_bgm.py assets/bgm`（MusicGen small、CPU で 28s×2 本）。seed_a 静かな単音ピアノ／seed_b 明るい主旋律。**重みは CC-BY-NC 4.0（非商用）**。商用ではロイヤリティフリー音源を seed_a/seed_b に置くか、ベッドを直接差し替える。
- ベッド: `python3 $SK/make_bed.py <total> <turn>`（seed_a→turn 秒で seed_b に 3s クロス、末尾 5.5s フェード、loudnorm −23）→ `assets/bgm/bed_<round(total)>.mp3`。
- 音量キー（絶対値、`data-volume="1"`）: 単音ピアノ区間 0.26、転調後 0.15〜0.24、締め前で 0.24 に戻す。seed_a 単独区間は 0.16 以下にしない（ループ位置で −50dB の穴）。

## check → render → 検証

```bash
npm run check
# 60 秒以下はそのまま。100 秒を超えるときは PRODUCER_STREAMING_ENCODE_MAX_DURATION_SECONDS=400 と --low-memory-mode を付ける
setsid nohup npx --yes hyperframes@0.8.30 render > render.log 2>&1 &
# 完了待ち
for i in $(seq 1 120); do grep -q "Render complete\|Render failed" render.log && break; sleep 5; done
mv renders/<name>_2026-*.mp4 renders/<name>.mp4 && rm -rf renders/work-*
python3 $SK/sample_frames.py renders/<name>.mp4 sheet.jpg 2 14 21 28 36 50 59 67 74 80 85 92
ffmpeg -ss 72 -t 21 -i renders/<name>.mp4 -af ebur128 -f null - 2>&1 | grep -E "^\s+I:"
```
目視で見る点: 字幕が全キュー 1 行／カバー矩形が見えていない／吹き出しの位置／注記ピル／締めのロゴ／転換のにじみ。音は各コマ −16〜−12 LUFS。

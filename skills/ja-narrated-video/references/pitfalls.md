# 罠と対処（実際に踏んだものだけ）

## 環境・実行
| 症状 | 原因 | 対処 |
|---|---|---|
| 画像生成・TTS が「接続先と鍵を環境変数に設定してください」で止まる | `.env` 未読込（バックグラウンド起動で忘れる） | `set -a && . <repo>/.env && set +a` を同じシェルで実行してから `setsid nohup … &` |
| デプロイが `InsufficientQuota` で失敗する | クォータはモデルとデプロイ種別ごとにサブスクリプション全体で共有。他のリソースが枠を使い切っていることがある。DataZone 標準は別枠（単価は 1.1 倍）。費用の集計に反映するため `.env` に `REALTIME_SKU=DataZoneStandard` を書く |
| `ModuleNotFoundError: websockets` | 別の Python（pyenv の版違いなど）で実行した | リポ直下の `.venv/bin/python` で実行する（`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`） |
| 実画面のスクショの下端に地の色が出る | `google-chrome --headless=new` はウィンドウ枠のぶんビューポートが縮む | HyperFrames が落とす chrome-headless-shell で撮る（例 `examples/meetroom-30s/.hyperframes/shoot_ui.sh`） |
| `ModuleNotFoundError: rt_tts` | スクリプトの相対パス誤り | `scripts/rt_tts.py` を同じディレクトリから import（`gen_voice.py` はスキル内の相対で解決済み） |
| `pkill -f "hyperframes render"` で自分のシェルが死ぬ（exit 144） | 自分のコマンド文字列にもマッチ | `ps -eo pid,args \| grep "[h]yperframes@0.8.30 render" \| awk '{print $1}' \| xargs kill` |
| 2 つのサブエージェントがレート制限で途中死 | セッションのレート制限 | ファイルは書かれていることが多い。自分で check して続ける |

## レンダ
| 症状 | 対処 |
|---|---|
| `Disk capture may need ~44000 MB of temporary frame storage` | `--low-memory-mode` を付ける（ストリーミング）。`PRODUCER_STREAMING_ENCODE_MAX_DURATION_SECONDS=400` は 100s 級では効いたが 176s では gate が `enabled:false` になった |
| 出力がタイムスタンプ付きファイル | 完了後 `mv renders/<name>_2026-*.mp4 renders/<name>.mp4`、`rm -rf renders/work-*`。先に旧版を `_vN.mp4` に退避 |
| 所要時間 | 100s ≈ 3.5 分（3 ワーカー）、176.5s ≈ 9 分（低メモリは 1 ワーカー）。待ちは `grep -q "Render complete\|Render failed"` のループで |

## check（lint / layout / contrast / motion）
| 指摘 | 対処 |
|---|---|
| `root_missing_dimensions` | 各コマの `#root` に `data-width="1920" data-height="1080"` |
| WCAG AA 落ち（灰文字 `#66707F` が白ピルの上で不足） | `#4F5B6E` に置換 |
| `audio_volume_tween_overrides_gain` | `data-volume="1"` にして `tl.set("#el-bgm",{volume:0.26},0)` から絶対値で刻む |
| `gsap_exit_missing_hard_kill` | フェード後に `tl.set(el,{opacity:0}, 境界)` を足す |
| `content_overlap … inside #cap-…` | 字幕帯（y 900–1018）に要素が重なっている。要素を `top:640px` に上げる／右上ピルに移す／旧テロップカードは `display:none` |
| `audio_src_not_found` | `voice_meta.json` の `path` がプロジェクト相対になっているか（`assets/voice_v2/e01.wav`） |
| `multiple_root_compositions` | サブコンポは 1 ファイル 1 `<template>` 1 `#root` |
| `timeline_track_too_dense`（warning） | 無視可 |
| `container_overflow`（Ken Burns・パンチインの層） | 意図したはみ出し。無視可 |
| プレビュー（スタジオ）を開いたあと、コマの HTML に `data-hf-id` が書き足されて git の差分が出る | スタジオが要素の識別用に付ける。生成スクリプトを再実行すれば消えるので、コミット前に再生成する |
| Python `IndentationError` after sed | sed が 2 行ある `FRAMES = [` の片方だけ置換して孤児行が残った。複数行のリテラルは python で書き換える |

## 見た目
| 症状 | 原因と対処 |
|---|---|
| カバー矩形が薄い青の板として見える | `ground()` のサンプル点が接続線の淡色帯に乗った。**(960,1020) の字幕帯で取る**か図ごとに `ground:"#F4F5F8"` を明示 |
| UI 実画面のチップ文字が読めない | パンチ 1.5 では不足。**1.9〜2.0** に上げるか `card` で 2 倍切り出し |
| 焼き込みラベルがテロップ／字幕の後ろで二重に見える | 焼き込み側に常時カバー（`coverBL`） |
| 字幕が 2 行になり図の下端に重なる | `build_captions.py --hard 30`（1 行 ≈ 31 字） |
| 字幕の断片「〇〇は、」だけが単独で 1.5 秒出る | 無音だけで切っていた。文境界＋中央の「、」だけで割る（現行の chunker） |
| 右列が空白の「これまで／これから」図が未完成に見える | 図をやめて写真モンタージュに（editorial-rules） |
| パンチインで左端の文字が切れる | カメラ中心を左へ（cx 1030→890）。端の条件: `540 - S*cy < 0` かつ `540 + S*(1080-cy) > 1080` |
| 同じ机・同じカウンターの「ペアロック」が守られない | 言葉では無理。**同一画像を再利用**する |

## 音
| 症状 | 対処 |
|---|---|
| 社名・英字略称の読みが take ごとに揺れる | 長音と中黒で表記を決め（例「エヌ・ティー・ティー」）、4〜6 take 録って依頼者に選ばせる。判定モデル（`rt_listen.py`）はノイズが大きい |
| BGM に 1〜2 秒の穴（−50dB） | seed_a（単音ピアノ）のループ位置。単独区間は 0.26 程度、0.16 まで下げない |
| 尺変更後に BGM 末尾がずれる | `ffmpeg -t <total> -af "afade=t=out:st=<total-5.5>:d=5.5"` でベッドを作り直す |
| 生音声の末尾に 1 秒前後の無音が付く（6.02 秒にそろうことがある） | 切れてはいない。`gen_voice.py` が前後の無音を削るので気にしなくてよい |
| 読み上げの照合に文字起こしモデルが要るか | 要らない。realtime の `response.output_audio_transcript.done` で照合している |

## 素材
| 症状 | 対処 |
|---|---|
| 画像生成が 400 Bad Request | 児童（小学生・親子の子ども）を含むプロンプト。子ども不在の構図に |
| 題字・注記が勝手に焼き込まれる | STRICT TEXT RULE を接頭辞末尾に |
| どのタブから線が出るかを守らない | 拡大ボックスを付けるタブを行末（右下）に |
| ラベルが化ける | 8 字以内。長文は SVG/HTML で |

## 写真の「らしさ」
| 症状 | 対処 |
|---|---|
| 役所の窓口が病院・銀行に見えるなど、場所の「らしさ」が出ない | 接頭辞にその場所を決める小道具と色を明示する（例：木のカウンター、低い仕切り、発券機、待合ベンチ、白衣・医療機器なし）。beige/wood のような色指定が効く |
| テロップ非表示後に空の白カードが残る | テロップを包む `-card` 要素（白地＋アクセント線）が別にある。包みごと `display:none` |

# gpt-image-2 スタイル接頭辞

ジョブ JSON の `style` に入れる固定文。画像ごとの `prompt` の前に連結される。**末尾の STRICT TEXT RULE を削らない**（無いと 20 枚中 7 枚に題字・注記が焼き込まれた）。サイズは `2048x1152`、`quality: high`（1 枚 約 70〜100 秒、10 並列）。

接頭辞の中の「どこの・どんな場所か」「色」を題材に合わせて書き換える。それ以外（顔なし、文字なし、下 22% を空ける、STRICT TEXT RULE）は残す。

## LIVE（写実・顔なし・文字なし・朝の順光）

人の様子・職場・街など「人と場所」のコマに使う。以下は `examples/meetroom-30s` で使った版（日本のオフィス、アクセントは深緑）。

```
Photorealistic location photography for a Japanese B2B software promo video, landscape 16:9, 2048x1152. Depict an anonymous modern Japanese mid-size company office, never an identifiable company. Morning front-light, soft daylight through windows, soft contrast, natural 35mm-film-like colors, a calm palette of off-white, warm wood and muted deep green (#0F7B5F) accents; no evening light or dramatic backlighting. All people are East Asian adults in business-casual clothing, with no identifiable faces: show backs, shoulders, hands, or distant rear-facing figures. No legible text anywhere; signage is blank or out of focus, documents contain only illegible abstract marks, screens show blank panels or soft abstract grids, keyboards have unmarked keys. No real company names, brands, logos, recognizable products, watermarks, or readable badges. Keep the lower 22%, y=78-100%, simple and free of important subjects or fine detail for video subtitles; use uncluttered floor or desk surfaces rather than darkening the image. Keep principal subjects within the side margins. No robots, holograms, sparkles, or decorative particles. Text (verbatim): [] means no visible text. STRICT TEXT RULE: never render titles, annotations, captions, footnotes, overlay text, logos, or any other legible characters.
```

画像プロンプトの書き方（実績のある形）:
```
Scene: <誰が・どこで・何をしているか。小道具を具体的に（ノート PC を胸に抱える、紙コップのコーヒー、付箋だらけの綴り）>. <光・雰囲気>. Composition: <主要被写体の位置>, lower 22% is plain floor / desk surface.
```

## CG（フラットな図解）

概念図・比較図に使う。配色は BRIEF.md の palette に合わせて書き換える。

```
Flat vector-style raster graphics for a Japanese B2B promo video, landscape 16:9, 2048x1152. Restrained corporate design: off-white background #F6F8F7, ink #14211C, exactly one accent color #0F7B5F, and secondary greys #8A9690 and #DCE3DF. Use crisp consistent strokes, solid fills, generous space, and rounded corners no larger than 12px. No shadows, gradients, glow, lighting effects, textures, volumetric 3D, or glossy rendering; isometric diagrams use parallel projection and flat fills only. Keep lower 22%, y=78–100%, simple and free of essential content for subtitles; preserve additional empty regions specified per image. UI text consists only of the exact short labels in Text (verbatim), each at most eight characters, preferably 44px or larger in clean Japanese sans-serif. An empty array means no visible characters. Body content uses grey horizontal rules, never pseudo-writing. No real company names, logos, competitor interfaces, invented place names, real statistics, robots, brains, circuits, gears, database cylinders, or sparkles. People, if present, are East Asian and shown only from behind, from the shoulders, or as hands, without visible faces. STRICT TEXT RULE: the complete visible text inventory is exactly Text (verbatim); never add titles, annotations, captions, footnotes, closing explanations, overlay text, or any unlisted characters.
```

CG プロンプトの書き方:
```
Use case: <infographic-diagram など>. Asset type: <side-by-side comparison …>. Subject: <ブロックの並びを x/y の % で>. Composition: <どこを空けるか>. Text (verbatim): ["これまで","探す",…]. Avoid: crosses, x marks, red, warning icons, numbers, brand names, robots. STRICT TEXT RULE: render only Text (verbatim) …
```

## 既知の癖
- **児童を含む構図は 400 Bad Request** になることがある。子ども不在の構図にするか、表現を弱める（後ろ姿・遠景）。
- 「どのタブから線が出るか」のような接続関係は守れないことがある。拡大ボックスを付ける要素は行末（右下）に置く。
- ラベルが 8 字を超えると化ける。密な図でもラベルが短ければ通る。数字は焼き込まない。
- 焼き込まれたラベルの文言を後から変えたいときは、`paints`（地色で塗る）＋`labels`（HTML で上書き）で対応できる。再生成しない。
- 写実の下 22% が単調でないと字幕ピルが浮く。プロンプトに必ず lower 22% の指示を入れる。
- 写実の人物は「後ろ姿・手元だけ」と明示しないと顔が正面や横顔で出る。

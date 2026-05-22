---
name: mobile-preflight-check
description: |
  kizukikumitate.com の HTML/CSS 編集後、コミット前に必ず実行するモバイル最終チェックスキル。
  「スマホ版の改行が変」「カードが壊れている」「、や。が単独行に出る」等を
  毎回手動で修正する時間を抜本的に削減するためのもの。

  以下のタイミングで必ず参照する:
  - HTMLページを編集してコミット直前
  - CSS（特に @media (max-width: 768px) 系）を編集した直後
  - 「モバイルで〇〇が壊れた」「スマホで〇〇がおかしい」とユーザーから指摘されたとき
  - 新規ページを公開する前

  3種類のチェックを順に実行:
  1. 静的 grep 検査（3パターンの既知アンチパターンを検出）
  2. iPhone viewport の自動スクショ取得（Playwright）
  3. スクショを目視確認
---

# モバイル最終チェック・スキル

## なぜこのスキルが存在するか

過去、以下の同じ問題が **何度も** 繰り返されてきた:

1. **flex+アイコンカードのモバイル崩れ**
   - `pricing-impact` / `vision-mechanism` の本文が intrinsic 幅に縮み、右側へはみ出す
   - 親の `align-items: flex-start` がモバイルでも残ることが原因
2. **句読点の孤立**（、 や 。 だけが単独行に）
   - HTML の `<p>` タグ内に複数行のインデント付き文字列が書かれていて、その空白が改行候補になる
3. **「筋肉① 好奇心筋」が「筋肉①」「好奇心筋」で分割される**
   - ASCII 半角スペースが `word-break: keep-all` でも改行候補のため
4. **タイポグラフィルールの hanging-punctuation 抜け漏れ**

これらは静的解析で **機械的に検出可能** なため、コミット前に自動チェックする。

## 実行手順（コミット前の標準フロー）

```bash
cd /Users/morimotoyasuhito/kizukikumitate

# 1. 静的チェック（数秒で終わる）
./.claude/scripts/mobile-preflight.sh check <file.html>

# 2. runtime チェック（Playwright で iPhone レンダリング検査、~10秒）
./.claude/scripts/mobile-preflight.sh runtime <file.html>

# 3. スクショ取得（目視確認用）
./.claude/scripts/mobile-preflight.sh shoot <file.html>

# まとめて実行
./.claude/scripts/mobile-preflight.sh full <file.html>
```

スクショは `.claude/screenshots/mobile_<ファイル名>_<タイムスタンプ>.png` に出力される。
Claude は出力された PNG を Read ツールで表示してチェックする。

## 検出されるアンチパターン

### Pattern A: 句読点（、。）の直後に HTML 改行があるテキストブロック

**症状:** 句読点（、。）が単独行に追い出される。または文章の途中で不自然な改行。

**対象タグ（葉ノード）:**
- `<p>`, `<h1>`〜`<h6>`, `<li>`, `<dt>`, `<dd>`, `<blockquote>`
- 見出し的な `<div class="*-bridge|*-heading|*-quote|*-callout-title|*-visual-quote|*-manifesto|hero-title|hero-subtitle|hero-label">` 等

**例（NG）:**
```html
<p>
  自分の社会への違和感、組織での孤独、家族との対話の難しさ——
  昼のワークではまだ言葉になっていなかったものが、
  夜の火のゆらぎの前で、ぽつりぽつりと言葉になっていく。
</p>
```
HTML の改行とインデントが空白文字に変換され、それがブラウザの改行候補になる。
`word-break: auto-phrase` と `line-break: strict` の組合せで、空白を境に句読点が
孤立する現象が起きる。

**修正:**
```html
<p>自分の社会への違和感、組織での孤独、家族との対話の難しさ——昼のワークではまだ言葉になっていなかったものが、夜の火のゆらぎの前で、ぽつりぽつりと言葉になっていく。</p>
```
1段落 = 1行で書く。長くなっても改行しない。本当に行替えしたい箇所のみ `<br>` を入れる。

**経験則:** 多くの場合、見出しや段落内の HTML 改行は無意識にエディタの右端で折返されたコピペ由来。
`<p>` `<h*>` `<div class="*-quote">` 等の中身は **必ず1行に展開** すること。

### Pattern B: 半角スペース付き「番号+名称」パターン

**症状:** 「筋肉① 好奇心筋」「Step 1 はじめに」等が、狭幅で「筋肉①」「好奇心筋」と分断される。

**例（NG）:**
```html
<div class="timetable-item">筋肉① 好奇心筋／<br>筋肉② 傾聴筋</div>
```

**修正:**
```html
<div class="timetable-item">筋肉①&nbsp;好奇心筋／<br>筋肉②&nbsp;傾聴筋</div>
```
番号+名称の間に意図的にスペースを入れたい場合は、必ず `&nbsp;`（U+00A0 改行禁止スペース）にする。

### Pattern C: flex column で align-items: stretch 抜け

**症状:** モバイルでカード本体が壊れて、本文が右側へはみ出す/中央に偏る。

**例（NG）:**
```css
.pricing-impact {
  display: flex;
  align-items: flex-start;  /* PC では正しい */
}
@media (max-width: 768px) {
  .pricing-impact {
    flex-direction: column;  /* ← これだけだと content が intrinsic 幅に縮む */
  }
}
```

**修正:**
```css
@media (max-width: 768px) {
  .pricing-impact {
    flex-direction: column;
    align-items: stretch;  /* ← 明示的に上書き */
  }
  .pricing-impact-icon { align-self: center; }  /* アイコンだけ中央 */
}
```

### Pattern D: モバイルタイポグラフィに hanging-punctuation 抜け

**症状:** Pattern A の対策後も、句読点が行末で次行に流れる事故が稀に発生。

**修正:** モバイルの段落系セレクタに `hanging-punctuation: allow-end` を追加。
行末の `、` `。` `」` 等をマージン側にぶら下げて、強制的に行内に収める。

### Pattern E: runtime チェック（Playwright で実機相当検査）

静的検査だけでは捕まえられない以下の問題を、iPhone 14 Pro viewport で
レンダリングして実検出する。

**E1. 行頭句読点（line-break: strict 違反）:**
CSS の `line-break: strict` 設定があっても、`</strong>` 等の inline 境界や
`<em>` の挟み込みで Safari が strict を破ってしまうケースがある。
runtime check は各行の先頭文字を実取得して、`、。」）】 ・` 等が出ていないか確認する。

**E2. 1〜2文字 widow:**
段落最終行に1〜2文字だけ残るケースを検出。例:
- 「デモクラシーフィットネスとは」が「とは」「は」のように分割される

**修正例:**
```html
<!-- NG: 「フィットネスとは」が分断されうる -->
<h2>デモクラシーフィットネスとは</h2>

<!-- OK: nowrap span で意味的なまとまりを保つ -->
<h2>デモクラシー<span class="jp-nowrap">フィットネスとは</span></h2>
```

CSS:
```css
.jp-nowrap {
  white-space: nowrap;
  word-break: keep-all;
}
```

または、見出しに `<br class="br-mobile-only">` を入れて意図的に改行ポイントを制御する:
```html
<h2>この2日間は、ゴールではなく、<br class="br-mobile-only">はじまりです。</h2>
```
```css
.br-mobile-only { display: none; }
@media (max-width: 768px) {
  .br-mobile-only { display: initial; }
}
```

**E3. `line-break: strict` 未適用要素:**
日本語テキストを含むのにモバイル typography rule が当たっていない要素を検出。
セレクタの列挙漏れを発見する。

**修正:** 該当クラスを `fix-japanese-typography` の typography rule リストに追加する。

**E4. `text-wrap: balance` が日本語テキストに適用 ⚠️**

これは **runtime check が PASS したのに実機で句読点が行頭に出る** という不可解な現象の原因だった。

`text-wrap: balance` は「複数行の行幅を均等にする」CSS で、見出しなど短文の体裁を整えるのに使う。
しかし日本語に対しては:
- `line-break: strict` を **無視** して句読点を行頭に動かしてしまう
- `auto-phrase` の文節境界より「行幅の均等性」を優先する

具体例:「私たちは、日本に「対話で物事を動かせる人」を、ひとりずつ…」が
「…を / 、ひとりずつ…」のように 「、」 を行頭に押し出す。

**修正:** `text-wrap: balance` を `text-wrap: pretty` に変更する。
pretty は行均等は犠牲にするが、widow（1文字孤立）防止と禁則を尊重する。

```css
/* NG */
.xxx-lead { text-wrap: balance; }

/* OK */
.xxx-lead { text-wrap: pretty; }
```

## スクショ確認のポイント

`.claude/screenshots/mobile_*.png` を Read で表示し、目視で以下を確認:

- [ ] カード（pricing-impact / vision-mechanism / for-whom-card / why-camp-card）が
      正しく表示されている（テキスト全文が読める、はみ出していない）
- [ ] 句読点が単独行に出ていない
- [ ] 「筋肉①」等の番号+名称が同一行に収まっている
- [ ] 横スクロールが発生していない
- [ ] グローバルナビが画面内に収まっている

## トラブルシュート

### Playwright のインストールに失敗する
- `npm` 経由の起動なら nvm の Node が必要。`nvm use --lts` してから再実行
- ブラウザだけ再 DL：`npx -y playwright@1 install chromium`

### ローカル HTTP サーバーがポート 8080 で起動できない
- 既存プロセスを停止: `lsof -ti tcp:8080 | xargs kill -9`
- もしくはスクリプトの PORT を 8081 等に変更

### grep チェックが誤検出する
- 各チェックの誤検出パターンは `.claude/scripts/mobile-preflight.sh` のコメントに記載
- 既知の許容例は同スクリプトの SKIP リストに追加できる

## デプロイ

チェックがすべてパスし、スクショで問題ないことを確認したら通常通り:
```bash
git add <ファイル>
git commit -m "..."
git push origin main
```

## 既存スキルとの関係

このスキルは「最終チェック」担当。各論の修正方針は以下のスキルを参照:

- `fix-japanese-typography` — 句読点・改行ルール全般
- `fix-mobile-overflow` — はみ出し全般
- `fix-nav-spacing` — ナビ周り
- `optimize-page-images` — 画像最適化

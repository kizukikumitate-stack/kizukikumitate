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
./.claude/scripts/mobile-preflight.sh check democracy-fitness-camp-0811.html

# 2. スクショ取得（初回は Playwright のブラウザ DL に1-2分）
./.claude/scripts/mobile-preflight.sh shoot democracy-fitness-camp-0811.html

# または両方まとめて
./.claude/scripts/mobile-preflight.sh full democracy-fitness-camp-0811.html
```

スクショは `.claude/screenshots/mobile_<ファイル名>_<タイムスタンプ>.png` に出力される。
Claude は出力された PNG を Read ツールで表示してチェックする。

## 検出される3つのアンチパターン

### Pattern A: Multi-line `<p>` ブロック

**症状:** 句読点（、。）が単独行に追い出される。または文章の途中で不自然な改行。

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

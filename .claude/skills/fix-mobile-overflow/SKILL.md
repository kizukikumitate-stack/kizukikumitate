---
name: fix-mobile-overflow
description: |
  kizukikumitate.com のモバイル表示でコンテンツが右にはみ出す・折り返されない問題を予防・診断・修正するスキル。
  このスキルは2つの場面で使う:
  (1) 予防: HTMLページを新規作成・編集するとき、コミット前にモバイル表示の安全性を確認する
  (2) 修正: 「モバイルで右側が切れている」「スマホで横スクロールが出る」等の報告を受けたとき
  kizukikumitateリポジトリのHTML/CSSを触るときは必ずこのスキルを参照すること。
  ページの作成、デザイン変更、CSS調整、コンテンツ追加のいずれでも適用する。
---

# モバイル表示 予防・修正スキル

## リポジトリ情報

- パス: `/Users/morimotoyasuhito/kizukikumitate`
- デプロイ: GitHub Pages（`git push origin main` で自動反映、1〜2分かかる）
- 構成: 各HTMLファイルに `<style>` タグでCSSが埋め込まれている（外部CSSファイルなし）

## 予防: HTML/CSSを書く・編集するときのチェックリスト

kizukikumitateリポジトリでHTML/CSSを作成・編集するときは、**コミット前に**以下を必ず確認する。
過去2回連続でモバイルはみ出しが発生しており、事後修正のコストが高いため、ここで防ぐ。

### コミット前チェック（全項目クリアしてからコミット）

1. **メディアクエリの位置**: モバイル用 `@media` ブロックが対象のベーススタイルより**後ろ**にあるか？
   - 同じ詳細度ならCSSは後に書いた方が勝つ。ベーススタイルの前にメディアクエリがあると無効化される
   - **対策**: 必ず `</style>` 直前に最終overrideブロックとしてまとめる

2. **padding/margin の確認**: 新たに追加した `padding` や `margin` に `3rem` 以上の水平値がないか？
   - モバイル（375px幅）では左右 `2rem` 以上で危険域に入る
   - **対策**: ベースで大きいpadding を書いたら、最終overrideで `1.5rem` 以下に縮小する

3. **white-space: nowrap の確認**: 英語テキストを含む要素に `nowrap` を指定していないか？
   - 日本語は短いが英語（例: "Constructive Developmental Theory"）は長い
   - **対策**: バッジ等はモバイルで `white-space: normal` にする

4. **flex の確認**: `flex-shrink: 0` や `flex-wrap: nowrap`（デフォルト）で横並びにしていないか？
   - モバイルでは横幅が足りず子要素がはみ出す
   - **対策**: モバイルで `flex-direction: column` または `flex-wrap: wrap` にする

5. **overflow-x: hidden**: `html, body` へのモバイル用 `overflow-x: hidden` があるか？
   - 1要素のはみ出しがページ全体に波及する「連鎖効果」を防ぐ安全ネット

6. **最終overrideブロックの存在**: ファイル末尾（`</style>` 直前）にモバイル最終overrideブロックがあるか？
   - 新規ページ作成時は最初からこのブロックを入れておく

### 新規ページ作成時の必須ルール

新しいHTMLページを作るとき、768pxメディアクエリに以下を**必ず**含めること。
過去に何度も「カードのテキストが右に切れる」問題が発生しており、原因は毎回同じ:
テキスト要素に `overflow-wrap: break-word` が付いていなかった。

#### ルール: すべてのテキスト要素に break-word を付ける

ページ内で定義した**タイトル・説明文・リード文のクラスすべて**に対して、
モバイル用メディアクエリ内で以下を付与する:

```css
.クラス名 { overflow-wrap: break-word; word-break: break-word; }
```

「このクラスは短いテキストだから大丈夫」と判断しない。
日本語でも英語混じりやURLが含まれると折り返せなくなる。**全部付ける**。

#### ルール: カード要素に overflow: hidden を付ける

カード型のコンテナ（`.service-card`, `.evidence-card`, `.approach-card` 等）には
`overflow: hidden` を付けて、子要素が親からはみ出さないようにする。

#### テンプレート

新しいHTMLページを作るときは、`<style>` ブロックの末尾に以下の構造で含めておく:

```css
/* ===== モバイル最終override（CSS特異度対策・必ず末尾に配置） ===== */
@media (max-width: 768px) {
  html, body { overflow-x: hidden; }

  /* グリッドを1カラムに */
  .xxx-grid { grid-template-columns: 1fr; }

  /* カードのパディング縮小 + はみ出し防止 */
  .xxx-card { padding: 1.4rem 1.2rem; overflow: hidden; }

  /* ★ 全テキスト要素にbreak-word（これを忘れると右切れが発生する） */
  .section-title,
  .section-lead,
  .xxx-card-title,
  .xxx-desc,
  .emphasis-text,
  .cta-sub {
    overflow-wrap: break-word;
    word-break: break-word;
  }

  /* その他のモバイル修正 */
  footer { padding: 2rem 1.5rem; flex-direction: column; gap: 0.8rem; }
}

@media (max-width: 480px) {
  .container { padding: 0 1rem; }
  /* 極小画面用の追加修正 */
}
```

**`xxx` の部分をページ固有のクラス名に置き換える。**
タイトル・説明文・リード文のクラスは**漏れなく全部**含めること。

---

## 診断手順（問題が報告されたとき）

### 1. 対象ファイルを特定して読む

ユーザーが指摘したページのHTMLファイルを開き、`<style>` ブロック全体を把握する。

### 2. モバイル用メディアクエリの位置を確認する

ファイル内の `@media` ブロックがどこに書かれているかを確認する。

**最も重要なポイント**: CSSは同じ詳細度（specificity）なら**後に書かれた方が優先**される。
モバイル用の `@media (max-width: 768px)` がファイル上部にあり、対象の基本スタイルがそれより
下に定義されている場合、メディアクエリの指定は基本スタイルに上書きされて**無効化される**。

```
/* NG: この順序だとモバイル指定が効かない */
@media (max-width: 768px) {
  .method-card { padding: 1rem; }  /* ← 先に書かれている */
}
.method-card { padding: 2rem 2.2rem; }  /* ← 後に書かれて上書き */

/* OK: 基本スタイルの後にメディアクエリを置く */
.method-card { padding: 2rem 2.2rem; }
@media (max-width: 768px) {
  .method-card { padding: 1rem; }  /* ← 後に書かれているので有効 */
}
```

### 3. はみ出しの原因を特定する

以下のパターンを順にチェックする:

| チェック項目 | よくある原因 | 修正方法 |
|---|---|---|
| `padding` が大きすぎる | `footer { padding: 3rem 6rem }` など | モバイルで `1.5rem` 程度に縮小 |
| `white-space: nowrap` | 英語バッジ等の長いテキストが折り返されない | モバイルで `white-space: normal` に |
| `flex-shrink: 0` + 長いコンテンツ | flex子要素が縮まず親をはみ出す | `flex-direction: column` に変更 |
| `overflow-x: hidden` がない | 1つの要素のはみ出しがページ全体に波及 | `html, body` に設定 |
| `word-break: keep-all` | 長い日本語テキストが折り返されない | `overflow-wrap: break-word` を併用 |
| `overflow-wrap` がない | カード内テキストが親要素をはみ出す（**最頻出**） | 全テキスト要素に `overflow-wrap: break-word; word-break: break-word;` を追加 |
| カードに `overflow: hidden` がない | テキストはみ出しがカード外まで波及 | カード要素に `overflow: hidden` を追加 |
| `min-width` が大きい | `.flow-step { min-width: 120px }` など | モバイルで `80px` 等に縮小 |

**連鎖効果に注意**: 1つの要素（例: footer）がビューポート幅を超えると、`body` 自体が
広がり、**すべてのセクション**が右に余白を持つように見える。原因は1箇所でも症状は全体に出る。

### 4. 修正パターン

すべてのモバイル修正は、ファイル末尾の `</style>` 直前にある「最終override」ブロックに
集約する。これにより、基本スタイルより後に記述されることが保証される。

```css
/* ===== モバイル最終override（CSS特異度対策・基本スタイルより後に記述） ===== */
@media (max-width: 768px) {
  html, body { overflow-x: hidden; }

  /* パディング縮小 */
  .method-card { padding: 1.4rem 1.2rem; }
  .day-card { padding: 1.2rem 1.2rem; }
  .retreat-block { padding: 1.8rem 1.5rem; }
  .prereq-box { padding: 1.4rem 1.2rem; gap: 1rem; }
  footer { padding: 2rem 1.5rem; flex-direction: column; gap: 0.8rem; }

  /* flex方向変更 */
  .method-head { flex-direction: column; gap: 0.5rem; }

  /* 折り返し有効化 */
  .method-badge { white-space: normal; }
  .method-title, .method-desc { overflow-wrap: break-word; word-break: break-word; }

  /* セクション単位のoverflow防止 */
  .methods-section { overflow-x: hidden; }
  .program-section { overflow-x: hidden; }
}

@media (max-width: 480px) {
  /* 極小画面ではさらにパディングを縮小 */
  .container { padding: 0 1rem; }
  .method-card { padding: 1.2rem 1rem; }
  .interim-card { margin-left: 0.5rem; padding: 0.8rem 0.8rem; }
  footer { padding: 1.5rem 1rem; }
}
```

## デプロイ手順

修正が完了したら:

```bash
cd /Users/morimotoyasuhito/kizukikumitate
git add <修正したファイル>
git commit -m "fix: <ページ名>のモバイル表示はみ出しを修正"
git push origin main
```

GitHub Pagesへの反映に1〜2分かかることをユーザーに伝える。
スマホで確認する際はブラウザキャッシュのクリア（Safariなら下に引っ張ってリロード）を案内する。

## 注意事項

- ウェブ版を修正したときは**必ずモバイル版も同時に確認・修正する**（ユーザーからのフィードバック）
- Chrome のウィンドウリサイズではモバイルビューポートを正確に再現できない（最小幅の制限がある）
- 修正後は実機またはブラウザ開発者ツールのデバイスモードでの確認をユーザーに依頼する

---

## 過去にハマった具体的な落とし穴（2026-05 セッションで判明）

### 落とし穴 1: CSS コメントに `</style>` リテラルを入れてはいけない

最も時間を浪費した事故。HTMLパーサーは `<style>` 要素を "raw text" として扱うため、
内容内に `</style>` を見つけると即座にstyleブロックを終了する。CSSコメント内であっても同様。

```css
/* NG: このコメントを書くと、ここで style 要素が早期終了し、以降の CSS が全部 body に流れる */
/* ===== 末尾の override（必ず </style> 直前に配置） ===== */

/* OK: 「</style>」を別の表現に置き換える */
/* ===== 末尾の override（必ず style 終端の直前に配置） ===== */
```

**症状**: モバイル用overrideを追加したのに、`getComputedStyle()` で見ても適用されていない。
ソースを見ると CSS は確かに書かれている。しかしDevToolsで見ると style が途中で閉じている。

**チェック**: CSSコメント内に `</style>` 文字列が含まれていないか必ず確認する。

### 落とし穴 2: `grid-template-columns: 1fr` の content-min-width 問題

CSSの `1fr` は実は `minmax(auto, 1fr)` であり、`auto` minimum は **コンテンツの最小幅** を取る。
日本語の `word-break: keep-all` で長文がひとつの「単語」になっていると、
**grid trackが画面より広く広がってしまう**。

```css
/* NG: 1fr が content-min-width まで拡張する */
.voices-grid { grid-template-columns: 1fr; }

/* OK: minmax(0, 1fr) で 0 まで縮小可能に */
.voices-grid { grid-template-columns: minmax(0, 1fr); }
.voice-card { min-width: 0; }                    /* grid item 側にも必要 */
.voice-text { word-break: normal; }              /* もしくは auto-phrase */
```

**症状**: `1fr` の単一カラムなのに、カードが画面より広く描画される（例: 327px枠に514pxのカード）。
`getBoundingClientRect()` の `gridTemplateColumns` が `"514px"` のように具体値で出る。

**対策（テンプレート）**: モバイル最終overrideで以下を一括適用:

```css
@media (max-width: 768px) {
  .xxx-grid, .yyy-grid {
    grid-template-columns: minmax(0, 1fr) !important;
  }
  .xxx-card, .yyy-card { min-width: 0; }
}
```

### 落とし穴 3: flex 子要素の `min-width: auto` も同じ問題

`display: flex` の子要素も `min-width: auto`（content min-width）で広がる。
flex子要素にテキストブロックが入っている場合、画面より広くなることがある。

```css
/* NG: flex子の text コンテンツが親より広く広がる */
.pricing-impact { display: flex; flex-direction: column; }
.pricing-impact-content { flex: 1; }  /* min-width: auto がデフォルト */

/* OK: flex子側で min-width:0 */
.pricing-impact-content { flex: 1; min-width: 0; }
```

**症状**: 親 `.pricing-impact` は 327px だが、子の `.pricing-impact-content` が 456px に。
`section { overflow-x: hidden }` で見えないだけで、テキストは画面外にクリップされている。

### 落とし穴 4: テーブル (`<table>`) は自動レイアウトで content-min-width に伸びる

テーブルは `width: 100%` でも、`table-layout: auto`（デフォルト）だと
セル内コンテンツの最小幅にしたがって全体が伸びる。長い文字列を含むと viewport を超える。

```css
/* OK: テーブルレイアウトを固定し、列幅を明示 */
.tokusho-table {
  table-layout: fixed;
  width: 100%;
}
.tokusho-table th { width: 38%; }
.tokusho-table th, .tokusho-table td {
  word-break: auto-phrase;
  overflow-wrap: break-word;
}
```

### 落とし穴 5: グローバルナビの padding/margin で hamburger が画面外

```css
/* NG: モバイルでもデスクトップ用 padding 3rem (48px) + margin-right 4rem (64px) のまま */
.global-nav { padding: 1rem 3rem; }
.global-nav .nav-logo { margin-right: 4rem; }
/* 375pxの中で: 48 + (logo) + 64 + (links) + (hamburger 36px) → hamburger が右にはみ出す */

/* OK: モバイルで padding/margin を縮小 */
@media (max-width: 768px) {
  .global-nav { padding: 1rem 1.2rem; }
  .global-nav .nav-logo { margin-right: 1rem; }
}
```

---

## 「全grid・全カード安全ネット」テンプレート

新規ページにも、既存ページの修正にも、このブロックを `</style>` 直前に置くだけで
過去の落とし穴をまとめて防げる:

```css
/* ===== モバイル最終 overflow override（必ず style 終端の直前に配置） ===== */
@media (max-width: 768px) {
  html, body { overflow-x: hidden; }

  /* 全gridセクションへの安全ネット */
  .voices-grid,
  .muscles-grid,
  .pricing-grid,
  .why-camp-grid,
  .vision-roadmap,
  .gallery-grid,
  .what-section,
  .speaker-section,
  .hero-info-bar,
  .venue-meta {
    grid-template-columns: minmax(0, 1fr) !important;
  }

  /* カード/コンテナの min-width:0 + 改行ルール */
  .voice-card, .why-camp-card, .price-card, .muscle-card,
  .vision-step, .pricing-impact, .vision-mechanism,
  .pricing-impact-content, .vision-mechanism-content {
    min-width: 0;
    overflow-wrap: anywhere;
  }

  /* テーブル */
  table {
    table-layout: fixed;
    width: 100%;
  }
  th, td {
    word-break: auto-phrase;
    overflow-wrap: break-word;
  }

  /* グローバルナビ */
  .global-nav { padding: 1rem 1.2rem; }
  .global-nav .nav-logo { margin-right: 1rem; }

  /* セクション overflow ガード */
  section { overflow-x: hidden; }
}
```

## 診断ワンライナー（プレビューブラウザ内）

```javascript
// すべての要素の中で、viewport を超えているものをリストアップ
(function(){
  var v = document.documentElement.clientWidth;
  var o = [];
  document.querySelectorAll('body *').forEach(function(el){
    var r = el.getBoundingClientRect();
    if (r.right > v + 1) {
      o.push({
        cls: (el.className || '').toString().slice(0, 50),
        right: Math.round(r.right),
        w: Math.round(r.width),
        text: (el.textContent || '').trim().slice(0, 25)
      });
    }
  });
  return { viewportW: v, bodyW: document.body.scrollWidth, n: o.length, samples: o.slice(0, 10) };
})()
```

**期待値**: `n: 0`、`bodyW === viewportW`。
1つでもオーバーする要素があればそれが原因。クラス名から CSS を特定して上記テンプレートに追加。

---

## モバイルでのセンタリング判断ロジック（2026-05 セッションで策定）

### 背景

`word-break: auto-phrase` で改行が自然になった後、ユーザーから「全般的に左に寄っていて
右にスペースがある」報告が来た。文章を全部センタリングすると本文の可読性が下がるため、
**選択的に中央寄せ** するルールを策定した。

### 中央寄せ vs 左寄せ 判断マトリクス

| 要素タイプ | モバイルでの基本方針 | 理由 |
|---|---|---|
| セクションラベル（"VOICES", "ABOUT" 等の小さなキャプション）| **中央寄せ** | 短く、視覚的アンカーになる |
| セクション見出し（h2, `.section-heading`）| **中央寄せ** | ページ構造のリズムを作る |
| ヒーローのテキスト（label/title/subtitle/body/info）| **中央寄せ** | 第一印象の中心要素 |
| 短いリード文（1-3行、見出し直下）| **中央寄せ** | 視線が落ち着く |
| カードタイトル（`.followup-title` 等）| **中央寄せ** | タイトルは中央が標準 |
| カード内アイコン + 見出し + 本文（特集カード）| **中央寄せ** | 視覚的バランスが取れる |
| 価格カード（`.price-card-*`）| **中央寄せ** | 価格表示は中央が標準 |
| 申し込み関連（`.register-*`）| **中央寄せ** | CTA周辺は中央が標準 |
| 引用・参加者の声（`.voice-text`）| **中央寄せ** | 引用は中央が映える |
| **本文段落（多行、3行以上）** | **左寄せ** | 中央寄せは多行で行頭が揃わず読みにくい |
| **リスト要素（`<li>`、agenda 等）**| **左寄せ** | bullet point の整列が崩れる |
| **テーブル本文**| **左寄せ** | 行内の整列が必要 |
| **マニフェスト・ボディコピー**（vision-manifesto 等）| **左寄せ** | 長文ステートメントは左寄せの方が読みやすい |

### 適用テンプレート

最終 override ブロックに以下を追加（このページ固有のクラス名に置き換える）:

```css
@media (max-width: 768px) {
  /* セクションラベル（flex container の場合は justify-content も） */
  .section-label {
    justify-content: center;
    text-align: center;
  }
  .section-heading { text-align: center; }

  /* ヒーロー */
  .hero-label, .hero-title, .hero-subtitle,
  .hero-info-label, .hero-info-value, .hero-body {
    text-align: center;
  }

  /* 短いリード／タイトル系（このページ固有のクラスを列挙） */
  .xxx-lead, .xxx-title, .xxx-note,
  .yyy-heading, .yyy-sub {
    text-align: center;
  }

  /* アイコン付きカードのコンテンツ
     .cool-icon は display: inline-flex なので、親の text-align: center で水平中央配置される */
  .for-whom-card,
  .why-camp-card,
  .muscle-item {
    text-align: center;
  }
  .for-whom-card h3, .for-whom-card p,
  .why-camp-card h3, .why-camp-card p,
  .muscle-num, .muscle-name {
    text-align: center;
  }
}
```

### アイコン中央寄せの落とし穴

`display: flex` で配置されているアイコン（`.cool-icon` 等）は、親の `text-align: center` で
中央寄せされる。これは `inline-flex` だから可能で、`block` レベルだと効かない。

```css
/* OK: inline-flex なので text-align で中央配置される */
.cool-icon {
  display: inline-flex;
  /* ... */
}
.xxx-card { text-align: center; }
/* → cool-icon が水平中央に配置される */

/* もし block level なら margin: 0 auto が必要 */
.xxx-icon {
  display: block;
  margin: 0 auto 1.2rem;  /* 水平中央 */
}
```

### 安全ネットとの衝突に注意（再発防止）

「全grid を minmax(0, 1fr) に !important」のような安全ネットを使うと、
**既存の `repeat(2, 1fr)` や `repeat(3, 1fr)` の指定を上書きしてしまう**。

```css
/* NG: muscles-grid が 2 カラム→ 1 カラムになってしまう */
.muscles-grid, .pricing-grid, ... {
  grid-template-columns: minmax(0, 1fr) !important;
}

/* OK: 個別に column 数を維持しつつ minmax(0, ...) で content-min 問題回避 */
.pricing-grid, .why-camp-grid, ... {
  grid-template-columns: minmax(0, 1fr) !important;
}
.muscles-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
}
.gallery-grid.cols-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
}
```

**チェック**: 安全ネットの一括ルールを追加する前に、各 grid の本来のカラム数を確認する。
modify したら必ずプレビューで全 grid セクションを目視確認。

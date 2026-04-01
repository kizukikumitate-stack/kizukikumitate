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

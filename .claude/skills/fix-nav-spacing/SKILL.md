---
name: fix-nav-spacing
description: |
  kizukikumitate.com のグローバルナビゲーションのスペーシングと折り返しを管理するスキル。
  このスキルは2つの場面で使う:
  (1) 予防: HTMLページを新規作成・編集するとき、ナビCSSが正しいパターンに従っているか確認する
  (2) 修正: 「ナビのスペースが狭い」「グローバルナビが2行になっている」等の報告を受けたとき
  kizukikumitateリポジトリでHTMLページを新規作成する場合や、ナビゲーションを含むCSSを
  編集する場合は必ずこのスキルを参照し、正しいパターンに合わせること。
---

# グローバルナビ スペーシング管理スキル

## リポジトリ情報

- パス: `/Users/morimotoyasuhito/kizukikumitate`
- デプロイ: GitHub Pages（`git push origin main` で自動反映、1〜2分かかる）
- 構成: 各HTMLファイルに `<style>` タグでCSSが埋め込まれている（外部CSSファイルなし）

## 予防チェックリスト（ページ新規作成・編集時）

HTMLページを新規作成するとき、または既存ページのナビCSS周辺を編集するときは、
以下の4点を**コミット前に必ず確認**する。1つでも欠けているとナビの崩れが発生する。

| # | チェック項目 | NG例 | OK例 |
|---|---|---|---|
| 1 | `nav` に `justify-content: space-between` が**ない** | `justify-content: space-between;` | （この行自体がない） |
| 2 | `.nav-logo` に `flex-shrink: 0` と `margin-right: 4rem` が**ある** | `flex-shrink` なし | `flex-shrink: 0; margin-right: 4rem;` |
| 3 | `.nav-links` に `margin-left: auto` が**ある** | `margin-left` なし | `margin-left: auto;` |
| 4 | `.nav-links a` に `white-space: nowrap` が**ある** | `white-space` なし | `white-space: nowrap;` |
| 5 | ナビリンク追加後に**右端リンクが切れていないか**確認した | Contactが画面外にはみ出す | 全リンクがビューポート内に収まっている |

### ナビリンクが増えたときの調整ルール

ナビリンクを追加した場合（またはリンクのテキストが長くなった場合）、**全ページで**以下を確認・調整する。
`white-space: nowrap` があると折り返されない分、リンクが画面外に飛び出す。

**調整の優先順位（この順で試す）:**

1. **`gap` を縮小する**: `1.4rem` → `1.2rem` → `1rem`
2. **nav `padding` を縮小する**: `0.7rem 2rem` → `0.7rem 1.5rem`
3. **リンクテキストを短くする**: 例「対話力向上プログラム」→「対話プログラム」

現在のリンク数（8本）での適正値:
- `nav { padding: 0.7rem 2rem; }`
- `.nav-links { gap: 1.4rem; }`

**ロゴとHOMEの間は絶対に崩さない**: `margin-right: 4rem` は変更禁止。ここを削ると別の問題が再発する。

### 簡易チェック用grepコマンド

新規ページを作成した後、以下を実行して確認できる:

```bash
cd /Users/morimotoyasuhito/kizukikumitate
# NG: justify-content: space-between が残っているファイル
grep -l "justify-content: space-between" *.html
# OK: margin-right が設定されているか
grep -l "margin-right: 4rem" *.html
# OK: margin-left: auto が設定されているか
grep -l "margin-left: auto" *.html
```

## 正しいナビCSS（リファレンス）

新規ページを作成するときは、以下のCSSをそのままコピーして使う。
既存ページを修正するときは、このパターンと差異がないか照合する。

```css
nav {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 100;
  padding: 0.7rem 2rem;
  display: flex;
  /* justify-content: space-between は使わない——ナビ項目が多いとロゴとの間隔が消える */
  align-items: center;
  background: rgba(255,255,255,0.97);
  backdrop-filter: blur(12px);
  border-bottom: 3px solid #3C3489;  /* ページのアクセントカラーに合わせて変更可 */
}
.nav-logo {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  text-decoration: none;
  flex-shrink: 0;        /* ロゴがナビリンクに押し潰されないようにする */
  margin-right: 4rem;    /* ロゴとナビリンクの間に十分なスペースを確保 */
}
.nav-logo img { height: 36px; width: auto; object-fit: contain; }
.nav-logo-text {
  font-family: 'Shippori Mincho', serif;
  font-size: 1.1rem;
  font-weight: 800;
  white-space: nowrap;   /* ロゴテキストの折り返しを防止 */
  color: #1a5fad;
  letter-spacing: 0.06em;
}
.nav-links {
  display: flex;
  gap: 1.4rem;           /* 8リンク収容のため2remより狭く */
  list-style: none;
  align-items: center;
  margin-left: auto;     /* ナビリンクを右寄せにする */
}
.nav-links a {
  font-family: 'Noto Sans JP', sans-serif;
  font-size: 0.82rem;
  font-weight: 400;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-decoration: none;
  white-space: nowrap;   /* ナビリンクの折り返しを防止 */
  transition: color 0.2s;
}
```

## 正しいナビHTML（リファレンス）

ナビリンクの一覧も統一する。新規ページでは以下をコピーし、`class="active"` を該当ページに移す:

```html
<!-- デスクトップナビ -->
<ul class="nav-links">
  <li><a href="./index.html">Home</a></li>
  <li><a href="./democracy-fitness.html">Democracy Fitness</a></li>
  <li><a href="./lsp.html">LSP</a></li>
  <li><a href="./education-program.html">研修設計プログラム</a></li>
  <li><a href="./od-program.html">組織開発プログラム</a></li>
  <li><a href="./dialogue-program.html">対話力向上プログラム</a></li>
  <li><a href="./social-leader-coaching.html">リーダー向けコーチング</a></li>
  <li><a href="./index.html#contact">Contact</a></li>
</ul>

<!-- モバイルメニュー -->
<div class="mobile-menu" id="mobileMenu">
  <button class="mobile-menu-close" id="mobileClose">✕</button>
  <a href="./index.html">Home</a>
  <a href="./democracy-fitness.html">Democracy Fitness</a>
  <a href="./lsp.html">LSP</a>
  <a href="./education-program.html">研修設計プログラム</a>
  <a href="./od-program.html">組織開発プログラム</a>
  <a href="./dialogue-program.html">対話力向上プログラム</a>
  <a href="./social-leader-coaching.html">リーダー向けコーチング</a>
  <a href="./index.html#contact">Contact</a>
</div>
```

## よくある症状と原因（修正時の参考）

| 症状 | 原因 |
|---|---|
| ロゴテキストとHOMEリンクの間にスペースがない | `justify-content: space-between` がナビ項目が多い場合にスペースを圧縮する。`.nav-logo` に `margin-right` がない |
| ナビリンクが2行に折り返される | `.nav-links a` に `white-space: nowrap` がない |
| 右端のリンク（Contactなど）が画面外に切れる | リンク数増加により `gap` × リンク数 + `padding` がビューポート幅を超えた。`gap` と `padding` を縮小する（ロゴの `margin-right` は変えない） |
| ページごとにナビの見た目が異なる | 各HTMLファイルに独立したCSS定義があり、修正が一部のファイルにしか反映されていない |

## ページごとの差異に注意

- `border-bottom` の色はページのアクセントカラーに合わせて異なる場合がある（例: `var(--teal-600)`, `var(--purple-800)` など）。色はそのまま維持する
- `.nav-links a:hover` の色もページごとに異なる場合がある。これもそのまま維持する
- `font-family` が `'Jost', sans-serif` のままのページがある場合は `'Noto Sans JP', sans-serif` に統一する

## 注意事項

- 新しいページが追加された場合、そのページのナビCSSも同じパターンに合わせる必要がある
- ナビリンクの数が増えすぎると、デスクトップでも収まりきらなくなる可能性がある。その場合はリンクのテキストを短くするか、`gap` の値を調整する
- ウェブ版を修正したときは**必ずモバイル版も同時に確認する**

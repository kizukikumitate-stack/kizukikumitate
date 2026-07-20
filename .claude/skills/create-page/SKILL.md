---
name: create-page
description: |
  きづきくみたてサイトに新しいHTMLページを作成するための手順書とテンプレート。
  新規ページ作成時に必ず参照し、デザインルール遵守・モバイル対応済みの状態でページを仕上げる。
---

# 新規ページ作成スキル

## リポジトリ情報

- パス: `/Users/morimotoyasuhito/kizukikumitate`
- デプロイ: GitHub Pages（`git push origin main` で自動反映）
- 構成: 各HTMLファイルに `<style>` タグでCSSが埋め込まれている（外部CSSファイルなし）

## 作成手順

### 1. 既存ページを参考にする

最も近い既存ページを特定し、HTML構造を参考にする。

| ページタイプ | 参考にするファイル |
|---|---|
| プログラム紹介 | `education-program.html` |
| イベント告知 | `democracy-fitness-event-0427.html` |
| サービス紹介 | `social-leader-coaching.html` |
| ランディングページ | `democracy-fitness.html` |

### 2. テンプレートからHTMLを生成

以下のテンプレートを使い、ページ固有の内容を埋める。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[ページタイトル] | きづきくみたて工房</title>
  <meta name="description" content="[ページの説明文 120〜160文字]">
  <meta property="og:title" content="[ページタイトル] | きづきくみたて工房">
  <meta property="og:description" content="[ページの説明文]">
  <meta property="og:image" content="https://kizukikumitate.com/ogp.png">
  <meta property="og:url" content="https://kizukikumitate.com/[ファイル名].html">
  <meta property="og:type" content="website">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2280%22>🧱</text></svg>">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;600;700;900&family=Shippori+Mincho:wght@400;500;600;700;800&family=DM+Serif+Display:ital@0;1&family=Jost:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-E3YZKY8DQG"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-E3YZKY8DQG');
  </script>
  <style>
    /* ===== リセット・ベース ===== */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Noto Serif JP', serif; color: #1a1a2e; line-height: 1.8; }

    /* ===== ナビゲーション（既存ページからコピー） ===== */
    nav {
      position: fixed; top: 0; left: 0; right: 0; z-index: 100;
      padding: 0.7rem 2rem;
      display: flex; align-items: center;
      background: rgba(255,255,255,0.97);
      backdrop-filter: blur(12px);
      border-bottom: 3px solid #3C3489;
    }
    .nav-logo {
      display: flex; align-items: center; gap: 0.7rem;
      text-decoration: none; flex-shrink: 0; margin-right: 4rem;
    }
    .nav-logo img { height: 36px; width: auto; object-fit: contain; }
    .nav-logo-text {
      font-family: 'Shippori Mincho', serif;
      font-size: 1.1rem; font-weight: 800;
      white-space: nowrap; color: #1a5fad; letter-spacing: 0.06em;
    }
    .nav-links {
      display: flex; gap: 1.4rem; list-style: none;
      align-items: center; margin-left: auto;
    }
    .nav-links a {
      font-family: 'Noto Sans JP', sans-serif;
      font-size: 0.82rem; font-weight: 400;
      letter-spacing: 0.1em; text-transform: uppercase;
      text-decoration: none; white-space: nowrap; transition: color 0.2s;
    }
    .hamburger {
      display: none; flex-direction: column; gap: 5px;
      cursor: pointer; margin-left: auto; padding: 10px;
    }
    .hamburger span { display: block; width: 24px; height: 2px; background: #1a1a2e; }
    .mobile-menu {
      display: none; position: fixed; top: 0; right: 0;
      width: 280px; height: 100vh; background: #fff;
      z-index: 200; padding: 2rem; flex-direction: column; gap: 1.2rem;
      box-shadow: -5px 0 20px rgba(0,0,0,0.15);
    }
    .mobile-menu.active { display: flex; }
    .mobile-menu a {
      font-family: 'Noto Sans JP', sans-serif;
      font-size: 0.95rem; text-decoration: none; color: #1a1a2e;
      padding: 0.5rem 0; border-bottom: 1px solid #eee;
    }
    .mobile-menu-close {
      align-self: flex-end; background: none; border: none;
      font-size: 1.5rem; cursor: pointer; padding: 0.5rem;
    }

    /* ===== ヒーロー ===== */
    .hero {
      padding: 10rem 3rem 5rem;
      text-align: center;
      /* background: ページに合わせて設定 */
    }
    .hero h1 {
      font-family: 'Shippori Mincho', serif;
      font-size: clamp(2rem, 4vw, 4.8rem);
      font-weight: 800;
      word-break: keep-all; overflow-wrap: break-word;
    }

    /* ===== ページ固有のスタイル ===== */
    /* ここにページ固有のCSSを追加 */

    /* ===== フッター ===== */
    footer {
      background: #26215C; border-top: 3px solid #3C3489;
      padding: 3rem 6rem; display: flex;
      justify-content: space-between; align-items: center;
    }
    .footer-logo {
      font-family: 'Shippori Mincho', serif;
      font-size: 1rem; font-weight: 800;
      color: rgba(255,255,255,0.9);
    }
    .footer-copy { color: rgba(255,255,255,0.6); font-size: 0.85rem; }

    /* ===== モバイル最終override（CSS特異度対策・必ず末尾に配置） ===== */
    @media (max-width: 768px) {
      html, body { overflow-x: hidden; }
      .nav-links { display: none; }
      .hamburger { display: flex; }
      .hero { padding: 7rem 1.5rem 3rem; }
      .hero h1 { font-size: 1.8rem; white-space: normal; }
      footer { padding: 2rem 1.5rem; flex-direction: column; gap: 0.8rem; }

      /* ★ 全テキスト要素にbreak-word */
      .section-title,
      .section-lead,
      .hero h1 {
        overflow-wrap: break-word;
        word-break: break-word;
      }
    }

    @media (max-width: 540px) {
      .hero h1 { font-size: 1.4rem; white-space: normal; }
      footer { padding: 1.5rem 1rem; }
    }
  </style>
</head>
<body>
  <!-- ナビゲーション：手で書かない。空マーカーだけ置く。
       data/nav.json に登録して scripts/update-nav.py を実行すると中身が生成される -->
  <!-- NAV START -->
  <!-- NAV END -->

  <!-- ヒーロー -->
  <section class="hero">
    <h1>[ページタイトル]</h1>
  </section>

  <!-- メインコンテンツ -->
  <!-- ここにページ固有のコンテンツを追加 -->

  <!-- フッター：手で書かない。空マーカーだけ置く（同上） -->
  <!-- FOOTER START -->
  <!-- FOOTER END -->

  <script>
    // ナビの開閉JS。variant "standard" の id/class に対応（台帳の variant と必ず揃える）
    document.getElementById('hamburger').addEventListener('click', () => {
      document.getElementById('mobileMenu').classList.add('open');
    });
    document.getElementById('mobileClose').addEventListener('click', () => {
      document.getElementById('mobileMenu').classList.remove('open');
    });
    document.querySelectorAll('.mobile-acc-toggle').forEach(t => {
      t.addEventListener('click', () => t.parentElement.classList.toggle('open'));
    });
  </script>
</body>
</html>
```

### 3. コミット前チェック

ページ完成後、以下を必ず確認:

1. `/fix-nav-spacing` のチェックリストに合格するか
2. `/fix-mobile-overflow` のチェックリストに合格するか
3. title タグと meta description が設定されているか
4. OGP 情報が正しいか
5. Google Analytics タグが含まれているか
6. ナビのリンク構成が他ページと同一か

### 4. data/nav.json への登録（★必須・省略するとCIが落ちる）

ページを作ったら、共通ナビを載せる／載せないに関わらず **必ず** `data/nav.json` に登録する。
どちらにも無いページがあると GitHub Actions（update-nav）が失敗する。

**共通ナビを載せる場合** — `pages` に追加（variant は3種から選ぶ。通常は `standard`）:

```json
{ "path": "new-page.html", "variant": "standard" }
```

**独自デザインで載せない場合** — `exclude` に理由付きで追加:

```json
{ "path": "new-page.html", "reason": "◯◯シリーズ＝独自ブランドバーの別LP" }
```

**グローバルナビのメニューにも項目として出す場合** — `nav.items` の該当グループに追加する。
これだけで全ページのナビが自動追従する（1ファイルずつ手で直すのは禁止）。

最後に生成を実行して確認:

```bash
python3 scripts/update-nav.py    # マーカーの中身が生成される
```

⚠️ ナビ／フッターのCSSは各ページのインライン `<style>` 側にあり、台帳の管理外。
手順1で既存ページ（`education-program.html` 等）をコピーして作れば、正しいナビCSSと
マーカーが最初から入っている。ゼロから書くとドロップダウンが無スタイルになる。

---

## モバイル耐性 標準テンプレート（2026-05 セッションで策定）

新規ページは、`</style>` 直前に以下のブロックを **必ず** 含めること。
今日のセッションで判明した5つの罠（grid 1fr / flex min-width / `</style>` リテラル /
iOS Dynamic Type / 日本語禁則処理）への防御を網羅。

```css
  /* ===== モバイル最終 overflow & typography override
     （必ず style 終端の直前に配置 / コメント内に閉じstyleタグを書かないこと） ===== */
  @media (max-width: 768px) {
    html, body {
      overflow-x: hidden;
      /* iOS Safari の text autosizing を無効化（暗背景カードで文字巨大化を防ぐ） */
      -webkit-text-size-adjust: 100%;
      text-size-adjust: 100%;
    }

    /* 全grid: minmax(0, 1fr) で content-min-width による拡張を防ぐ */
    [class*="-grid"] {
      grid-template-columns: minmax(0, 1fr) !important;
    }

    /* カード要素: min-width:0 + overflow-wrap で flex/grid 子の暴走を防ぐ */
    [class*="-card"], [class*="-content"] {
      min-width: 0;
      overflow-wrap: anywhere;
    }

    /* セクション横padding を縮小（インラインstyleには !important が必要） */
    section {
      padding-left: 1.5rem !important;
      padding-right: 1.5rem !important;
      overflow-x: hidden;
    }

    /* テーブルは table-layout: fixed で content-min による拡張を防ぐ */
    table {
      table-layout: fixed;
      width: 100%;
    }

    /* 日本語タイポグラフィ: 禁則処理＋自然な文節改行＋孤立防止 */
    body, p, li, h1, h2, h3, h4,
    [class*="-title"], [class*="-heading"], [class*="-body"], [class*="-text"],
    [class*="-lead"], [class*="-desc"], [class*="-meta"], [class*="-name"] {
      word-break: auto-phrase !important;
      overflow-wrap: break-word !important;
      line-break: strict !important;
      text-wrap: pretty;
    }

    /* 暗背景カード内のフォントは px 固定（iOS Dynamic Type の影響を遮断）
       ※ rem だとアクセシビリティ設定で巨大化することがある */
    [class*="-body"] { font-size: 15px !important; line-height: 1.95 !important; }
    [class*="-title"]:not(.hero-title):not(.section-heading) { font-size: 17px !important; }
    [class*="-label"]:not(.section-label) { font-size: 12px !important; }

    /* グローバルナビ: モバイルでは padding 縮小（hamburger が画面外に出ないように） */
    .global-nav { padding: 1rem 1.2rem; }
    .global-nav .nav-logo { margin-right: 1rem; }

    /* ===== モバイルでの文字整列 =====
       - 見出し・ラベル・短文 → 中央寄せ
       - 多行の本文 → プロジェクトのデザイン方針に従う
       - 表・リスト → 左寄せのまま */
    .section-label, .section-heading,
    [class*="-title"], [class*="-heading"], [class*="-lead"] {
      text-align: center;
    }
    .section-label::before {
      display: none !important;  /* 中央寄せ時の片側横棒を非表示 */
    }
    .section-label {
      justify-content: center;  /* flex container の中央配置 */
    }
  }
```

### 開発中の確認方法（dev-preview.sh）

`push` してから GitHub Pages の反映（1-2分）を待たずに、ローカル編集中のページを
即座にスマホで確認できる：

```bash
cd /Users/morimotoyasuhito/kizukikumitate
./dev-preview.sh
```

公開URLが表示されるので、それをスマホのSafariで開く。
ファイルを保存→スマホでリロードで即座に反映される（5秒サイクル）。

---

## コミット前チェックリスト（モバイル耐性確認）

新規ページの実装が終わったら、コミット前に以下を必ず確認:

| カテゴリ | チェック項目 |
|---|---|
| 構造 | nav, footer, OGP, title, GA タグが入っているか |
| 構造 | ナビリンクが他ページと一致しているか |
| 構造 | **CSS コメント内に `</style>` というリテラルが含まれていないか** |
| モバイル | `dev-preview.sh` でスマホ実機確認した |
| モバイル | 上記の「モバイル最終 override」ブロックが `</style>` 直前にある |
| モバイル | 暗背景カード内のフォントが px 固定になっているか |
| モバイル | 画像が `loading="lazy"` 付きで合計 5MB 以下か |
| タイポ | 日本語の本文に `word-break: auto-phrase` が効いているか |
| 寄付 | ※ 課金がある場合、特商法表記がフッターに含まれているか |

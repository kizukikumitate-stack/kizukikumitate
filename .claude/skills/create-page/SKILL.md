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
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-2ECK6163X4"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-2ECK6163X4');
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
  <!-- ナビゲーション -->
  <nav>
    <a href="./index.html" class="nav-logo">
      <img src="./logotype.png" alt="きづきくみたて工房ロゴ">
      <span class="nav-logo-text">きづきくみたて工房</span>
    </a>
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
    <div class="hamburger" id="hamburger">
      <span></span><span></span><span></span>
    </div>
  </nav>

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

  <!-- ヒーロー -->
  <section class="hero">
    <h1>[ページタイトル]</h1>
  </section>

  <!-- メインコンテンツ -->
  <!-- ここにページ固有のコンテンツを追加 -->

  <!-- フッター -->
  <footer>
    <div class="footer-logo">きづきくみたて工房</div>
    <div class="footer-copy">&copy; 2026 Yasuhito Morimoto. All rights reserved.</div>
  </footer>

  <script>
    document.getElementById('hamburger').addEventListener('click', () => {
      document.getElementById('mobileMenu').classList.add('active');
    });
    document.getElementById('mobileClose').addEventListener('click', () => {
      document.getElementById('mobileMenu').classList.remove('active');
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

### 4. ナビリンクに新ページを追加する場合

新ページをナビに追加する場合は、**全HTMLファイル**のナビとモバイルメニューを更新する必要がある。
1ファイルだけ更新して終わりにしない。

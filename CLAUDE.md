# きづきくみたて工房 ウェブサイト

GitHub Pages で公開中の静的HTMLサイト。
公開URL: https://kizukikumitate-stack.github.io/kizukikumitate/
独自ドメイン: https://kizukikumitate.com/

## 技術構成

- 静的HTML + インラインCSS（外部CSSファイルなし）
- GitHub Pages でホスティング
- GitHub Actions で note 記事を自動取得（articles.json）

## デザインルール

### グローバルナビゲーション（全ページ共通）

構成: Home / Democracy Fitness / LSP / 研修設計プログラム / 組織開発プログラム / Contact

- ロゴ: `logotype.png` + テキスト「きづきくみたて工房」を必ず両方表示
- ロゴ文字スタイル: `font-family: 'Shippori Mincho', serif; font-size: 1.1rem; font-weight: 800; color: #1a5fad; letter-spacing: 0.06em;`
- ナビ下線: `border-bottom: 3px solid #3C3489`

### フッター（全ページ共通）

```html
<footer>
  <div class="footer-logo">きづきくみたて工房</div>
  <div class="footer-copy">&copy; 2026 Yasuhito Morimoto. All rights reserved.</div>
</footer>
```

- CSS: `background: #26215C; border-top: 3px solid #3C3489; padding: 3rem 6rem; display: flex; justify-content: space-between; align-items: center;`
- ロゴ: `font-family: 'Shippori Mincho', serif; font-size: 1rem; font-weight: 800; color: rgba(255,255,255,0.9);`
- lsp.html のみフッターにLEGO商標表記を追加

### ヒーロー h1 フォントサイズ

- 基準: `font-size: clamp(2rem, 4vw, 4.8rem)`
- レスポンシブ:
  - `@media (max-width: 768px) { font-size: 1.8rem; white-space: normal; }`
  - `@media (max-width: 540px) { font-size: 1.4rem; white-space: normal; }`

### テキスト表示

- 重要テキストに `word-break: keep-all; overflow-wrap: break-word` を適用し、単語途中での改行を避ける
- 見出しなど必要な箇所は `white-space: nowrap` を使用

### 専門家の表記

- 専門家の理論には説明を付加（例：アージリス（クリス・アージリス／ハーバード大学教授。組織学習と行動科学の第一人者））
- 専門家名はカタカナ表記: アージリス、シャイン、コッター など

## レスポンシブ対応（必須）

**PC版を修正したら、モバイル版も必ず同時に確認・修正すること。**

確認すべきブレークポイント:
- PC: 1200px以上
- タブレット: 768px
- モバイル: 540px以下

チェックポイント:
- コンテンツが右にはみ出していないか（横スクロールが出ないか）
- テキストが適切に折り返されているか
- 画像がはみ出していないか
- ナビゲーションが正しく表示されているか

## エージェント + スキル構成

本プロジェクトでは「何をするか」（エージェント）と「どうやるか」（スキル）を分離して管理している。

### エージェント（`.claude/agents/`）

各エージェントは性格・原理原則・制約を定義。`claude -a エージェント名` で起動する。

| エージェント | 役割 |
|---|---|
| `quality-auditor` | 全ページの品質を横断監査（モバイル表示・ナビ・デザインルール） |
| `page-creator` | デザインルール遵守で新規HTMLページを作成 |
| `seo-content` | SEO最適化とコンテンツ改善の分析・提案 |
| `design-unifier` | 全ページのCSS/デザインの一貫性確認・統一 |
| `note-writer` | note記事の企画・執筆・下書き保存（公開は手動） |

### スキル（`.claude/skills/`）

各スキルは具体的な手順書。エージェントから参照される。

| スキル | 内容 |
|---|---|
| `fix-mobile-overflow` | モバイル表示のはみ出し予防・診断・修正手順 |
| `fix-nav-spacing` | ナビスペーシング管理手順 |
| `create-page` | 新規ページ作成テンプレートと手順 |
| `check-responsive` | 全ブレークポイントでのレスポンシブチェック手順 |
| `check-seo` | SEOチェック項目（title/meta/h1/OGP） |
| `check-design-consistency` | 全ページのデザイン一貫性チェック手順 |
| `propose-article-theme` | note記事テーマの提案手順 |
| `post-to-note` | Chrome MCPでnoteに下書き保存する手順 |

## Git 運用

- リモート: https://github.com/kizukikumitate-stack/kizukikumitate
- push は https トークン経由
- コミットメッセージは日本語で簡潔に

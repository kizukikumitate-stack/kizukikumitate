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

### コミット前の必須チェック（mobile-preflight）

HTML/CSS を編集して **コミットする前に必ず** 以下を実行する:

```bash
./.claude/scripts/mobile-preflight.sh full <編集したファイル>
```

- 静的 grep 検査で5種のアンチパターン（multi-line `<p>` / 番号+ASCIIスペース /
  flex column align-items 漏れ / hanging-punctuation 漏れ / grid `fr` が minmax(0,…) 未包囲）
  を機械的に検出
  - 最後の grid `fr` 検査は Safari 固有の右はみ出し対策。`1fr` は `minmax(auto,1fr)` の略で、
    日本語 + `word-break: keep-all` だと Safari で track がコンテンツ全幅まで広がるため、
    すべて `minmax(0, 1fr)` で囲む
- iPhone 14 Pro viewport の full-page スクショを `.claude/screenshots/` に保存
- 詳細: `.claude/skills/mobile-preflight-check/SKILL.md`

過去、これらは何度も再発して時間を浪費していた。**スキル参照ではなく自動チェックで根絶する**
方針。新規ページ作成・既存ページ編集・どちらでも適用。

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
| `mobile-preflight-check` | **HTML/CSS編集後・コミット前に必ず実行**。grep静的検査（multi-line `<p>`/番号+ASCIIスペース/flex column align-items漏れ/hanging-punctuation漏れ）+ iPhone viewport の自動スクショ。`./.claude/scripts/mobile-preflight.sh full <file>` |
| `manage-event-archive` | デモクラシーフィットネスのイベントを終了日時で自動「過去の開催」へ移動する仕組みの保守。**イベントカード追加時の形式契約**（`EVENT START/END`マーカー＋`data-event-end`/`data-region`）を必ず守る。`scripts/archive-events.py` + `.github/workflows/archive-events.yml` |
| `fix-mobile-overflow` | モバイル表示のはみ出し予防・診断・修正手順（grid 1fr/flex min-width/style内コメント等の落とし穴含む） |
| `fix-japanese-typography` | 日本語の禁則処理・単語内分割・1文字孤立を CSS Text Level 4 (auto-phrase/line-break/text-wrap) で解決 |
| `optimize-page-images` | ページ内画像の sips リサイズ・再圧縮＋ preload/lazy 戦略でモバイル読み込みを高速化 |
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

## モバイル即時プレビュー（push 前にスマホで確認する）

GitHub Pages のデプロイ（1-2分）を待たずに、ローカル編集中の状態を即座に
森本さんのスマホで確認できる仕組み。

### 使い方

```bash
cd /Users/morimotoyasuhito/kizukikumitate
./dev-preview.sh
```

実行すると `https://kizuki-preview.loca.lt`（または `https://xxxxx.loca.lt`）
の公開URLが表示される。スマホのSafariで開くと、ローカルの編集内容が即時反映される。

### 修正→確認サイクル

1. クロード側がファイルを編集して保存
2. スマホでページをリロード（下に引っ張ってリロード）
3. 即座に反映される（GitHub Pages 待ち不要）
4. 問題なければ git commit & push して本番反映

これで修正サイクルが「1-2分」から「5秒」に短縮される。

### 注意

- `dev-preview.sh` 実行中の Mac の電源が入っていて、ネット接続が必要
- スマホは同じ Wi-Fi でなくてもOK（インターネット経由で繋がる）
- 初回アクセス時に loca.lt の「Click to Continue」画面が出る場合あり
- 停止するには Ctrl+C

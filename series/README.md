# /series/ デプロイ前チェックリスト

連載「気づきから組み立てる」のサブサイト。kizukikumitate.com/series/ で公開。

## 必須（動作のために必要）

- [ ] `diagnostic.html` の `WEBHOOK_URL` に Make.com の Webhook URL を設定
- [ ] `index.html` セクション9 の 30分相談CTA リンクを Calendly URL に差し替え（現在 `https://calendly.com/yasuhito/30min` プレースホルダー）
- [ ] `index.html` セクション10 のメルマガ登録フォームを実際のサービス埋込コードに差し替え（現在 `action="#"` ダミー）
- [ ] OGP画像 (`/og-image.png`) を作成・設置（メインリポジトリ直下）

## 推奨（品質向上）

- [ ] About セクションの写真 (`assets/yasuhito.jpg`) を設置
- [ ] ヒーロー右側のビジュアル（BEM マトリクス図 or A社イラスト）を作成・設置
- [ ] 第1記事公開後、`index.html` セクション5（最新記事）を実データに更新
- [ ] favicon を作成・設置

## オプション

- [ ] Google Analytics 4 のトラッキングコードを設置
- [ ] プライバシーポリシーのページを作成・リンク
- [ ] メインサイト (kizukikumitate.com) のグローバルナビに「連載」リンクを追加

## ディレクトリ構成

```
series/
├── index.html              ← 連載LP本体
├── diagnostic.html         ← BEM 診断フォーム（Make.com 連携）
├── README.md               ← このファイル
├── assets/
│   ├── logo.png
│   └── pdf/                ← 診断結果配布用 PDF（5タイプ）
│       ├── type-a.pdf
│       ├── type-b.pdf
│       ├── type-c.pdf
│       ├── type-d.pdf
│       └── type-e.pdf
├── styles/
│   └── series.css
└── _reference/             ← Jekyll が公開対象から自動除外（社内参照用）
    ├── BEM-diagnostic-form.html             （元フォーム・base64 ロゴ込み）
    ├── BEM-diagnostic-email-templates.md    （Make.com 用メール文面）
    ├── BEM-diagnostic-implementation-guide.md（Tally + Make.com 自動化ガイド）
    └── BEM-diagnostic-Type-{A,B,C,D,E}-*.pdf（元の長いファイル名 PDF）
```

## ホスティング

GitHub Pages（kizukikumitate-stack/kizukikumitate）/ Deploy from `main` / `/ (root)`。
リポジトリには `_config.yml` が無いため Jekyll デフォルト処理が走り、`_reference/` のような `_` 始まりパスは公開対象から自動除外される。

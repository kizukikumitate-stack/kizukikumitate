---
name: check-seo
description: |
  きづきくみたてサイトの各ページのSEO項目をチェックする手順書。
  title/meta description/h1構造/OGP/構造化データを確認し、改善案を提案する。
---

# SEOチェックスキル

## リポジトリ情報

- パス: `/Users/morimotoyasuhito/kizukikumitate`
- 公開URL: https://kizukikumitate.com/

## チェック項目

### 1. title タグ

- [ ] 各ページに固有の `<title>` が設定されているか
- [ ] 文字数: 30〜60文字（日本語）が理想
- [ ] フォーマット: `[ページ固有のタイトル] | きづきくみたて工房`
- [ ] キーワードが含まれているか

### 2. meta description

- [ ] 各ページに固有の `<meta name="description">` があるか
- [ ] 文字数: 80〜160文字が理想
- [ ] ページの内容を正確に要約しているか
- [ ] 行動喚起（CTA）が含まれているか

### 3. 見出し構造（h1〜h3）

- [ ] h1 がページに1つだけあるか
- [ ] h1 にキーワードが含まれているか
- [ ] h2, h3 が論理的な階層構造になっているか
- [ ] 見出しだけ読んでページの内容が理解できるか

### 4. OGP（Open Graph Protocol）

- [ ] `og:title` が設定されているか
- [ ] `og:description` が設定されているか
- [ ] `og:image` が設定されているか（推奨: 1200x630px）
- [ ] `og:url` が正しい公開URLか
- [ ] `og:type` が設定されているか

### 5. 内部リンク

- [ ] 他のページへの内部リンクが適切にあるか
- [ ] リンク切れがないか
- [ ] アンカーテキストが説明的か（「こちら」ではなく具体的なテキスト）

### 6. 画像

- [ ] 全画像に `alt` 属性が設定されているか
- [ ] alt テキストが画像の内容を説明しているか
- [ ] 画像ファイルサイズが最適化されているか

### 7. パフォーマンス

- [ ] Google Fonts の読み込みに `display=swap` が付いているか
- [ ] 不要なスクリプトがないか
- [ ] 画像に `loading="lazy"` が設定されているか（ファーストビュー以外）

## チェック実行方法

```bash
cd /Users/morimotoyasuhito/kizukikumitate

# titleタグの一覧
grep -h '<title>' *.html

# meta descriptionの一覧
grep -h 'meta name="description"' *.html

# h1タグの一覧
grep -h '<h1' *.html

# OGP設定の確認
grep -h 'og:title\|og:description\|og:image\|og:url' *.html

# alt属性なし画像の検出
grep -Pn '<img(?![^>]*alt=)' *.html
```

## 改善提案のルール

1. **タイトルは読者の課題を言語化する** — 「組織開発プログラム」より「チームの対話が変わる組織開発プログラム」
2. **meta description は行動を促す** — 「...のプログラムです」で終わらず「...で組織を変えませんか？」
3. **h1 は検索意図に合わせる** — ユーザーが何を検索してこのページに来るかを想像する

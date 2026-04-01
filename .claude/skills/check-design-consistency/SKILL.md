---
name: check-design-consistency
description: |
  きづきくみたてサイト全ページのデザイン一貫性をチェックする手順書。
  ナビCSS/フッターCSS/フォント/カラーを全ページで照合し、差異を検出する。
---

# デザイン一貫性チェックスキル

## リポジトリ情報

- パス: `/Users/morimotoyasuhito/kizukikumitate`
- 構成: 各HTMLファイルに `<style>` タグでCSSが埋め込まれている（外部CSSファイルなし）

## チェック対象ページ

```bash
cd /Users/morimotoyasuhito/kizukikumitate
ls *.html | grep -v mockup | grep -v overflow-check | grep -v ogp-generator | grep -v preview
```

主要ページ:
- `index.html`
- `democracy-fitness.html`
- `lsp.html`
- `education-program.html`
- `od-program.html`
- `dialogue-program.html`
- `social-leader-coaching.html`

## チェック項目

### 1. ナビゲーションCSS

全ページで以下が統一されているか確認:

| プロパティ | 正パターン |
|---|---|
| `nav { padding }` | `0.7rem 2rem` |
| `nav { border-bottom }` | `3px solid [ページのアクセントカラー]` — 色はページごとに異なってOK |
| `.nav-logo { margin-right }` | `4rem` — **変更禁止** |
| `.nav-logo { flex-shrink }` | `0` |
| `.nav-links { gap }` | `1.4rem` |
| `.nav-links { margin-left }` | `auto` |
| `.nav-links a { font-family }` | `'Noto Sans JP', sans-serif` |
| `.nav-links a { font-size }` | `0.82rem` |
| `.nav-links a { white-space }` | `nowrap` |

```bash
# ナビ関連CSSの差異検出
for f in index.html democracy-fitness.html lsp.html education-program.html od-program.html dialogue-program.html social-leader-coaching.html; do
  echo "=== $f ==="
  grep -A2 'nav-logo' "$f" | grep -E 'margin-right|flex-shrink'
  grep -A2 'nav-links {' "$f" | grep -E 'gap|margin-left'
done
```

### 2. フッターCSS

| プロパティ | 正パターン |
|---|---|
| `footer { background }` | `#26215C` |
| `footer { border-top }` | `3px solid #3C3489` |
| `footer { padding }` | `3rem 6rem` |
| `footer { display }` | `flex` |
| `.footer-logo { font-family }` | `'Shippori Mincho', serif` |
| `.footer-logo { font-weight }` | `800` |
| `.footer-logo { color }` | `rgba(255,255,255,0.9)` |

### 3. Google Fonts 読み込み

全ページで同じフォントセットが読み込まれているか:

```bash
grep 'fonts.googleapis.com' *.html | sort -u
```

正パターン:
- Noto Serif JP (wght@400;600;700;900)
- Shippori Mincho (wght@400;500;600;700;800)
- DM Serif Display (ital@0;1)
- Jost (wght@300;400;500;600;700)

### 4. ナビリンク構成

全ページで同じリンク構成か:

```bash
for f in *.html; do
  echo "=== $f ==="
  grep -o 'href="[^"]*"' "$f" | head -20
done
```

正パターン（8リンク）:
1. `./index.html` (Home)
2. `./democracy-fitness.html` (Democracy Fitness)
3. `./lsp.html` (LSP)
4. `./education-program.html` (研修設計プログラム)
5. `./od-program.html` (組織開発プログラム)
6. `./dialogue-program.html` (対話力向上プログラム)
7. `./social-leader-coaching.html` (リーダー向けコーチング)
8. `./index.html#contact` (Contact)

### 5. ロゴ表示

- [ ] 全ページで `logotype.png` + テキスト「きづきくみたて工房」の両方が表示されるか
- [ ] ロゴテキストのスタイルが統一されているか

## レポート形式

```
## デザイン一貫性レポート

### 統一OK
- [チェック項目]: 全ページ統一済み

### 差異検出
| 項目 | 正パターン | 差異のあるファイル | 現在の値 |
|---|---|---|---|
| nav gap | 1.4rem | od-program.html | 2rem |

### 修正手順
1. [ファイル名] の [行番号付近] を [正パターン] に変更
```

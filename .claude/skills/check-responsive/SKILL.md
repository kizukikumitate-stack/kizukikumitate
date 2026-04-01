---
name: check-responsive
description: |
  きづきくみたてサイトの全ブレークポイント（1200px/768px/540px）でのレスポンシブ表示を
  チェックする手順書。品質監査エージェントが使用する。
---

# レスポンシブチェックスキル

## リポジトリ情報

- パス: `/Users/morimotoyasuhito/kizukikumitate`
- 開発サーバー: `python3 -m http.server 8080` （port 8080）

## チェック対象ブレークポイント

| ブレークポイント | ビューポート幅 | 主な確認事項 |
|---|---|---|
| PC | 1200px以上 | ナビが1行に収まる、レイアウトが正常 |
| タブレット | 768px | グリッドが1カラムに変わる、パディングが縮小 |
| モバイル | 540px以下 | h1が1.4rem、横スクロールなし、全テキスト折り返し |

## チェック手順

### 1. 対象ファイルの特定

```bash
cd /Users/morimotoyasuhito/kizukikumitate
ls *.html | grep -v mockup | grep -v overflow-check | grep -v ogp-generator | grep -v preview
```

### 2. 各ページのメディアクエリ確認

各HTMLファイルの `<style>` ブロックを読み、以下を確認:

#### 必須メディアクエリ

| メディアクエリ | 必須内容 |
|---|---|
| `@media (max-width: 768px)` | `html, body { overflow-x: hidden; }` |
| `@media (max-width: 768px)` | `.hero h1 { font-size: 1.8rem; white-space: normal; }` |
| `@media (max-width: 768px)` | `footer { flex-direction: column; }` |
| `@media (max-width: 768px)` | `.nav-links { display: none; }` + `.hamburger { display: flex; }` |
| `@media (max-width: 540px)` | `.hero h1 { font-size: 1.4rem; }` |

#### チェックリスト（全ページ共通）

- [ ] 768px メディアクエリが `</style>` 直前（最終overrideブロック）にあるか
- [ ] `overflow-x: hidden` が `html, body` に設定されているか
- [ ] 全テキスト要素に `overflow-wrap: break-word` があるか
- [ ] グリッドが1カラムに変わるか
- [ ] カード要素に `overflow: hidden` があるか
- [ ] パディングがモバイル用に縮小されているか
- [ ] 540px ブレークポイントが存在するか
- [ ] h1 が clamp() を使っているか

### 3. プレビューでの目視確認

開発サーバーを起動して、preview ツールで確認:

1. デスクトップ幅でページを表示
2. 768px にリサイズして表示を確認
3. 540px（または mobile プリセット）にリサイズして確認

### 4. 問題のレポート

問題を見つけたら以下の形式で報告:

```
| ページ | ブレークポイント | 問題 | 原因 | 修正案 |
|---|---|---|---|---|
| od-program.html | 540px | カードテキストが右に切れる | overflow-wrap なし | モバイル最終overrideに追加 |
```

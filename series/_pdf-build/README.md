# BEM 診断結果 PDF ビルド

`series/assets/pdf/type-{a-e}.pdf` を HTML テンプレートから生成する仕組み。

## 使い方

```bash
cd series/_pdf-build
python3 build.py            # 全タイプ生成
python3 build.py A          # Type A のみ
python3 build.py A B        # Type A と B
```

出力先: `../assets/pdf/type-{a-e}.pdf`

## 必要な環境

- macOS (Chrome がインストール済みであること)
- Python 3 (標準ライブラリのみ。追加パッケージ不要)
- `/Applications/Google Chrome.app` ← Chrome headless でPDFレンダリング

## ファイル構成

| ファイル | 役割 |
|---|---|
| `build.py` | ビルドスクリプト本体。タイプ別データを保持し、HTMLにテンプレート展開してChrome headlessでPDF化 |
| `template.html` | HTMLテンプレート。`{{PLACEHOLDER}}` 形式でデータを差し込む |
| `README.md` | このファイル |

## 内容を変更したい場合

### 文言・スコア・記事リストなどを変える

`build.py` 内の `TYPES` 辞書を編集 → `python3 build.py` で再生成。

### デザイン (色・余白・フォントなど) を変える

`template.html` の `<style>` を編集 → `python3 build.py` で再生成。

### ロゴを変える

`/Users/morimotoyasuhito/kizukikumitate/logo.png` を差し替え → 再生成（`build.py` が自動で base64 埋め込み）。

## 設計上のポイント

### Chrome headless で生成している理由

- 日本語フォント（Hiragino）の組版が安定
- CSS のレイアウト精度が高い
- インストール済みの Chrome を使うので追加依存なし

### `--user-data-dir` を毎回別で作る

複数 Chrome インスタンス起動時のプロファイル衝突を回避。生成完了後にクリーンアップ。

### Chrome がハングするときの対応

Chrome は PDF 書き出し後にときどきハングするので、`build.py` はファイルサイズが安定したら自動で Chrome を terminate する仕組み。

### ページの構成

- 1 ページあたり `.page` div 1つ。`height: 297mm; overflow: hidden;` で A4 固定
- `.page-spacer { flex: 1 }` で footer をページ下部に押し付ける
- ページ間は `.page + .page { break-before: page; }` で改ページ

## 修正履歴

- 2026-05-06: 初版。Claude Chat で生成された PDF を HTML テンプレート生成に置き換え
  - ロゴを白パディング付きで dark header に表示
  - 「このレポートについて」をheadline直後に配置 (旧版の妙な空白を解消)
  - Footer を A4 ページ下部に配置

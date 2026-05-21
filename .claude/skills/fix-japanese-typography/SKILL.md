---
name: fix-japanese-typography
description: |
  kizukikumitate.com の日本語テキストレンダリングの問題（句読点の行頭・1文字孤立・単語内分割・不揃いな改行）を、
  CSS Text Module Level 4 の新機能で根本解決するスキル。
  以下のキーワード/症状が出たら必ずこのスキルを参照する:
  - 「行頭に句読点が出る」「、や。が行の最初にある」
  - 「改行後に1文字だけ」「単語が分割されている」
  - 「文章の折り返しが変」「行が不揃い」「choppyな改行」
  - 「日本語のレイアウトを整えたい」「タイポグラフィを整える」
  HTML/CSSを編集した直後、特にモバイルで日本語の見栄えがおかしいと感じたら適用する。
---

# 日本語タイポグラフィ修正スキル

## なぜこのスキルが必要か

日本語テキストには英語にはない改行の難しさがある:
1. **禁則処理**: 句読点（、。）や閉じカッコ（」）が行頭に来てはいけない
2. **単語境界**: スペースで区切られないため、ブラウザがどこで切るべきか判断しにくい
3. **1文字孤立**: 単語の途中で1文字だけ次行に流れる（「皆さ」/「ん」）

過去に何度も「word-break: keep-all → 行が不揃い」「word-break: normal → 1文字孤立」の間で
ピンポンしていた問題を、CSS Text Module Level 4 の新機能で **根本解決** する。

## 修正パターン（モバイル中心）

ファイル末尾の最終 `@media (max-width: 768px)` ブロックに以下を追加:

```css
/* ===== 日本語の禁則処理・自然な文節改行 =====
   - word-break: auto-phrase: CJK文節境界で改行（Safari 17.4+ / Chrome 119+）
     → 「皆さ」「ん」のような単語内1文字分割を解消
     → 未対応ブラウザは normal にフォールバック
   - line-break: strict: 、。」）等を行頭にしない（禁則処理）
   - text-wrap: pretty: paragraph last line の1文字孤立を防止
   - 見出しには text-wrap: balance で複数行のバランスを揃える */

body,
p, li, dd, dt, blockquote, figcaption,
.section-heading, .section-label,
/* ↑ ページ固有のクラスもすべて列挙する。漏れがあるとそこだけ汚い改行になる */
{
  word-break: auto-phrase;
  overflow-wrap: break-word;
  line-break: strict;
  text-wrap: pretty;
}

/* 見出し系は balance で複数行を均等に */
h1, h2, h3, h4,
.hero-title, .section-heading,
.followup-title, .pricing-impact-title {
  text-wrap: balance;
}
```

## 各プロパティの役割

| プロパティ | 役割 | 必須度 |
|---|---|---|
| `word-break: auto-phrase` | CJK文節境界で改行。「合宿参加費」を「合宿参/加費」に分割せず、「合宿参加費/」で改行 | ★★★ |
| `line-break: strict` | 、。」）（等の行頭禁止文字を強制的に行末に保持（禁則処理） | ★★★ |
| `text-wrap: pretty` | 段落末の1文字孤立を防止。全体のwrap品質を向上 | ★★ |
| `text-wrap: balance` | 複数行タイトルを均等な行長に。短い見出し限定（性能影響あり） | ★ |
| `overflow-wrap: break-word` | 長い英単語/URL等のオーバーフロー対策 | ★ |

## ブラウザサポート（2026年現在）

| 機能 | Safari | Chrome | Firefox |
|---|---|---|---|
| `word-break: auto-phrase` | 17.4+ | 119+ | 未対応 |
| `line-break: strict` | 11+ | 58+ | 58+ |
| `text-wrap: pretty` | 17.4+ | 117+ | 124+ |
| `text-wrap: balance` | 17.4+ | 114+ | 121+ |

`auto-phrase` 未対応ブラウザは `normal` に自動フォールバックするため、書き方として
壊れない（最悪ケース＝Firefox: 古い `word-break: normal` 相当の挙動）。

## 適用範囲の決め方

### モバイルのみに適用すべき理由

PCで広い表示幅では、上記の問題はほぼ目立たない。`text-wrap: pretty` は計算コストもあるため、
**`@media (max-width: 768px)` の中で適用する** のが基本。

### どの要素に適用すべきか

「テキストが流れる要素すべて」に適用するのが原則。具体的には:

- 段落: `p`, `.xxx-body`, `.xxx-text`, `.xxx-lead`, `.xxx-body p`
- リスト: `li`, `.xxx-agenda li`
- 引用: `blockquote`, `.voice-text`
- 表セル: `th`, `td`, `.tokusho-table th`, `.tokusho-table td`
- 見出し: `h1-h4`, `.section-heading`, `.hero-title`（こちらは `balance` も）
- ラベル/キャプション: `.section-label`, `.muscle-name`, `.timetable-item` 等

**漏れがあるとそこだけ汚い改行になる** ので、ページ固有のクラスはすべて列挙すること。
fix-mobile-overflow スキルの「全テキスト要素列挙」と同じ原則。

## 診断手順

ユーザーが「行頭に句読点」「1文字孤立」「変な改行」と言ってきたら:

1. **プレビューブラウザのモバイル幅で再現**:
   ```javascript
   // 該当する p や li の computed style を確認
   (function(){
     var el = document.querySelector('.followup-purpose p');  // 該当クラス
     var cs = getComputedStyle(el);
     return {
       wordBreak: cs.wordBreak,
       lineBreak: cs.lineBreak,
       textWrap: cs.textWrap,
       overflowWrap: cs.overflowWrap
     };
   })()
   ```

2. **期待値**:
   - `wordBreak: "auto-phrase"` （ブラウザ非対応なら "normal"）
   - `lineBreak: "strict"`
   - `textWrap: "pretty"` （見出しは `"balance"`）

3. **`"normal"` や `"keep-all"` のままなら**: その要素のクラス名が
   モバイル override の列挙に含まれていない。追加する。

## デプロイ・確認

```bash
cd /Users/morimotoyasuhito/kizukikumitate
git add <修正したファイル>
git commit -m "fix: <ページ名>の日本語タイポグラフィを整える"
git push origin main
```

確認時はスマホで `Cmd + Shift + R`（Safariは下に引っ張ってリロード）でキャッシュ破棄。

## 注意事項

- **デスクトップでも適用したい場合**: `@media` を外してbase styleにする。ただし
  `text-wrap: pretty` は性能コストがあるので、長文記事ページなど効果が大きい場所に限定する
- **`text-wrap: balance` は短いテキスト専用**: 段落本文には適さない（balance は遅い）。
  4-6行までの見出しに使う
- **`word-break: auto-phrase` は段落単位で効く**: span 等の inline 要素に直接かけても
  期待通り動かないことがある。block-level 要素 (p, div, h*, li) に適用する
- 古い `keep-all` が残っていないか確認する。auto-phrase より優先される

# きづきくみたて工房 ウェブサイト

GitHub Pages で公開中の静的HTMLサイト。
公開URL: https://kizukikumitate-stack.github.io/kizukikumitate/
独自ドメイン: https://kizukikumitate.com/

運営: 森本康仁（屋号: きづきくみたて工房）。
組織開発・人材開発コンサルティングの拠点サイト。診断ツール・図鑑コンテンツ・
Democracy Fitness 等のハブ。

## サイト構成（主要ページ）

- index.html — トップ（今後のイベントプレビューあり・自動整理対象）
- democracy-fitness.html — Democracy Fitness（イベント一覧・自動アーカイブ対象）
- dialogue-program.html — 対話力向上プログラム（SEOメインKW「対話力向上研修」）
- dialogue-program-trial.html — 体験会ハブページ
- lsp.html — LEGO® SERIOUS PLAY®（フッターにLEGO商標表記）
- education-program.html / od-program.html — 研修設計・組織開発プログラム
- social-leader-coaching.html — 社会派リーダーコーチング
- topaasia.html / topaasia-data-notes.html — Topaasia（日英切替対応）
- roadmap.html — 世界平和までのロードマップ（D3グローブ・共創主義セクション）
- ashimoto-map.html — 足元からの地図（五層の平和構築モデル）
- nobel-peace.html — ノーベル平和賞 125年の系譜
- dialogue-zukan.html / shikumi-zukan.html / poverty-zukan.html / ted-collection.html
  — 図鑑シリーズ（紙背景テンプレ）
- risk-calculators.html — 未来のリスク計算機について（シリーズのハブ。共通の前提・出典・免責・
  ライセンス・変更履歴・フィードバック導線の**唯一の正**。各計算機からここへリンク）
- customer-age-timebomb(01) / recruitment-extinction(02) / tax-revenue-countdown(03) /
  skill-succession-timebomb(04) / school-consolidation-countdown(05) /
  caregiving-capacity-calculator(06).html — 未来リスク計算機シリーズ
  （ナビ「未来のリスク計算機」。素のHTML/JS＋手書きSVGで作る。新作の元原稿がReact/Rechartsで
  来ても移植すること。テンプレの正は recruitment-extinction.html）
- yokai/ — 会社の妖怪診断（index/zukan/workshop/ranking/gallery、夜色・金・墨の独自世界観）
- shakai-yokai/ — 社会の妖怪診断（完全バイリンガル・自己完結）
- democracy-fitness-camp-*.html / democracy-fitness-event-*.html — イベント個別ページ
- *-mockup.html / preview-diagram.html / od-overflow-check.html / ogp-generator.html — 作業用（ナビ非掲載）
- data/nav.json + scripts/update-nav.py — グローバルナビ・フッターの台帳・自動同期（唯一の正）
- data/kaiyu.json + scripts/update-kaiyu.py — サイト内回遊バンドの台帳・自動更新
- scripts/update-calculators.py — 未来リスク計算機6本の共通パーツ（版・出典・免責・ライセンス・
  「簡易試算」バッジ）の正。6本はCSS/JSがコピペ共有なので、共通文言を手で1本ずつ直すと必ず
  取り残しが出る。`<!-- CALC-COMMON START/END -->` 間が生成物。版を上げるときは VERSION を
  書き換えて実行し、risk-calculators.html の変更履歴に1項目足す

### 未来リスク計算機シリーズの約束（数字を扱うページの原則）

数字を出すツールは、誤用されると当事者を傷つける。以下は確定方針:

- **出典は実装と一致させる。** 使っていないデータを出典に挙げない（例: 03税収・05学校は
  利用者入力のみで、社人研・人口動態統計の実績値は読み込んでいない）。出典を足すときは
  必ずコードを読んで実際に使っているデータか確認し、URLは curl で200を確認してから書く
- **「確定」と書けるのは、実際に確定データを読み込んでいるときだけ。** モデルが入力値からの
  近似なら「〜と仮定した近似値」と明記する
- **大きな数字には必ず「簡易試算」バッジを隣に置く。** 数字と但し書きは数スクロール離れており、
  スクショされると前提が伝わらないため
- **どの結論も勧めない。** 学校統廃合・税収は政治的にセンシティブ。PTAキットと同じ中立性を貫く

## 技術構成

- 静的HTML + インラインCSS（外部CSSファイルなし）
- GitHub Pages でホスティング
- GitHub Actions で note 記事を自動取得（articles.json）
- **フレームワーク禁止**: React/Vue/Tailwind 等は導入しない（個別指示がある場合のみ例外）
- 文字コード UTF-8、lang属性は "ja"（英語ページは "en"）
- OGP必須項目: title / description / og:title / og:description / og:image / viewport

### 日英切替の実装方式（2方式が併存）

- topaasia系: 要素に `data-ja` / `data-en` 属性を持たせ、`.lang-toggle` ボタンで一括切替
- shakai-yokai系: ページ内蔵のUI辞書＋データ（DATA.questions_en 等）で切替。
  右下 langfab、`?lang=en` パラメータ＋ localStorage（キー: shakaiYokaiLang）で永続化
- 新規バイリンガルページはどちらかに合わせる（第3方式を作らない）

## デザインルール

### グローバルナビゲーション・フッター（全ページ共通・台帳で自動同期）

**❌ ページの `<nav>` や `<footer>` を手で書き換えないこと。** GitHub Actions が
`data/nav.json` から再生成して黙って上書きするため、手の修正は必ず消える。
各ページの `<!-- NAV START -->〜<!-- NAV END -->` / `<!-- FOOTER START -->〜<!-- FOOTER END -->`
の中身は生成物であり、正は `data/nav.json` ただ一つ。

- **ナビ項目を足す・減らす・並べ替える** → `data/nav.json` の `nav.items` を編集して push するだけで
  全ページ（現在35ページ）が自動追従する。相対パス（`./` と `../`）と `active` は階層から自動計算される
- **新規ページを作った** → `data/nav.json` の `pages`（共通ナビを載せる）か `exclude`（独自デザインで
  載せない・理由必須）に必ず1エントリ追加する。**どちらにも無いと GitHub Actions が失敗する**
- **新規ページを作ったら `sitemap.xml` にも手で1エントリ追加する**（`data/kaiyu.json` の回遊も同様）。
  ⚠️ sitemap.xml だけは**ジェネレーターが無く手動メンテ**で、update-nav.py を通しても入らず CI も
  検証しない＝黙って漏れる。現状ナビ掲載35ページに対し21件しか載っておらず、実際に漏れ続けている。
  形式は既存エントリのコピーでよい（`loc` / `lastmod` / `changefreq: monthly` / `priority: 0.6`）
- ローカル確認: `python3 scripts/update-nav.py`（生成）/ `--check`（検証のみ）
- 詳細は `scripts/update-nav.py` の冒頭コメントと `data/nav.json` の `_comment` を読む

ナビは **3変種** があり、各ページのJSが id/class を参照しているので台帳の `variant` を間違えないこと:

| variant | ハンバーガー | モバイルメニュー | 対象 |
|---|---|---|---|
| `standard` | `.nav-hamburger#hamburger` | `.mobile-menu#mobileMenu` | 通常ページ |
| `event` | `.global-nav-hamburger#globalHamburger` | `.global-mobile-menu#globalMobileMenu` | イベント・申込系 |
| `topaasia` | `div.hamburger#hamburger`（＋`.lang-toggle`） | `.mobile-menu#mobileMenu` | topaasia系 |

見た目のルール（CSSは各ページのインライン `<style>` 側にあり、台帳の管理外）:

- ロゴ: `logotype.png` + テキスト「きづきくみたて工房」を必ず両方表示
- ロゴ文字スタイル: `font-family: 'Shippori Mincho', serif; font-size: 1.1rem; font-weight: 800; color: #1a5fad; letter-spacing: 0.06em;`
- ナビ下線: `border-bottom: 3px solid #3C3489`
- ハンバーガー切替は全ページ 1250px（7項目化でデスクトップ横ナビが欠けるため。
  ナビ項目を増やすときは、この値も引き上がるか実測で確認する）
- フッターCSS: `background: #26215C; border-top: 3px solid #3C3489; padding: 3rem 6rem; display: flex; justify-content: space-between; align-items: center;`
- フッターロゴ: `font-family: 'Shippori Mincho', serif; font-size: 1rem; font-weight: 800; color: rgba(255,255,255,0.9);`
- フッターの例外は台帳側で表現する: lsp.html＝`footer_copy_prefix`（LEGO商標）、topaasia.html＝`footer: "topaasia"`（日英TM行）

### ヒーロー h1 フォントサイズ

- 基準: `font-size: clamp(2rem, 4vw, 4.8rem)`
- レスポンシブ:
  - `@media (max-width: 768px) { font-size: 1.8rem; white-space: normal; }`
  - `@media (max-width: 540px) { font-size: 1.4rem; white-space: normal; }`

### テキスト表示

- 重要テキストに `word-break: keep-all; overflow-wrap: break-word` を適用し、単語途中での改行を避ける
- 見出しなど必要な箇所は `white-space: nowrap` を使用

### カラーパレット・フォント

- 基調色: `#26215C`（濃紺・フッター背景）/ `#3C3489`（紫・ボーダー）/ `#1a5fad`（青・ロゴ文字）
- 妖怪系ページ（yokai/ shakai-yokai/）は夜色・金・墨の独自世界観。**白くしない**（確定方針）
- フォント: Shippori Mincho（ロゴ・見出し）、Noto Serif JP（本文）、DM Serif Display（欧文アクセント）

### 専門家の表記

- 専門家の理論には説明を付加（例：アージリス（クリス・アージリス／ハーバード大学教授。組織学習と行動科学の第一人者））
- 専門家名はカタカナ表記: アージリス、シャイン、コッター など

### サイト内回遊バンド（次は、こちらへ）

`data/kaiyu.json`（台帳）+ `scripts/update-kaiyu.py` で全ページのフッター直前を自動生成する。
新ページは台帳に1エントリ足して push すれば全ページの回遊が自動更新される。

- **有料商品は無料版の先でだけ見せる**（確定方針）。有料ページ（例: pta-kit-text.html＝
  PTA進行テキスト3,000円）は台帳で `"auto": false` を付け、新着枠・同カテゴリ補完枠の
  自動掲載から除外する。到達導線は無料版ページ（pta-dialogue-kit.html）の `next` に
  明示指定した1本だけにする（「まず無料キット → その先に有料」を全ページで担保）
- 新着枠（3枠目）は `added` が最新のページを全体から自動選出するため、有料・限定物を
  普通に追加すると全ページのフッターに勝手に露出する。有料物は必ず `auto:false` を付ける

### 文言のトーン（森本さんの好み）

- 「乗り越える」「倒す」等の対決・負荷感のある語を避け、「対になる」「向き合う」等の中立表現を使う
- 比較で特定業界（酒・化粧品等）を名指ししない（"敵を作る"表現を避ける）
- 「海外」を権威づけの修飾語として使わない
- 専門・制度用語（公民館等）は現代語の言い換えを併記する

## やってはいけないこと

- ❌ ページの `<nav>` / `<footer>`（NAV・FOOTERマーカーの中身）を手で書き換えない
      → `data/nav.json` を編集する。手の修正は自動生成で上書きされて消える
- ❌ 依頼されていないページのデザイン・文言を変えない
- ❌ 診断ツールの質問・スコアリング・判定ロジックを無断で変えない
- ❌ CSSフレームワーク / JSフレームワークを勝手に導入しない
- ❌ APIキー・トークンをコードにハードコードしない
- ❌ force push しない
- ❌ 承認なしにこの CLAUDE.md を書き換えない（更新は claude-md-keeper スキル経由）

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

### コミット・公開前の品質レビュー（site-reviewer）

ページの新規作成・大幅変更・ナビ変更・公開作業の前には、ユーザーレベルの
**site-reviewer エージェント**（`~/.claude/agents/site-reviewer.md`）にレビューさせる。
チェック項目: ナビ整合 / リンク切れ / 日英切替 / OGP / モバイル / ブランドトーン / 機密情報。
結果の「✅チェック済み項目」を完了報告に含めること。

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
| `manage-event-archive` | 終了したイベントを自動整理する仕組みの保守（一覧 democracy-fitness.html は「過去の開催」へ移動・トップ index.html は削除）。**イベントカード追加時の形式契約**（一覧＝`EVENT START/END`＋`data-event-end`/`data-region`、トップ＝`event-date`）を必ず守る。`scripts/archive-events.py` + `.github/workflows/archive-events.yml` |
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

### ユーザーレベルのスキル（~/.claude/skills/、他リポジトリ共通）

- 新イベントページ作成 → `democracy-fitness-event-setup`（プラグイン）
- イベント告知文セット → `event-announce-kit` / 申込者への連絡 → `event-comms`
- メルマガ定期配信 → `newsletter-ops`
- 手順の資産化（指示書→スキル昇格） → `skill-promoter`
- この CLAUDE.md の更新 → `claude-md-keeper`
- スキル台帳: `~/.claude/skills/README.md`

## Git 運用・デプロイ

- リモート: https://github.com/kizukikumitate-stack/kizukikumitate
- push はキーチェーン保存のクラシックPAT経由（workflow スコープあり＝ .github/workflows/*.yml も push 可）
- コミットメッセージは日本語で簡潔に
- デプロイ: GitHub Pages（main ブランチ / root）。push 後2〜3分で https://kizukikumitate.com に反映
- `.nojekyll` 設置済み（純静的HTML）。新規ページが本番だけ404のときは .nojekyll の有無をまず疑う
- main への直接コミットは小さな変更のみ。コミットはユーザーの承認を得てから

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

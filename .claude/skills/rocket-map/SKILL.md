---
name: rocket-map
description: |
  きづきくみたてのサイト全体図「平和な地球行きロケット」(rocket-map.html) の保守・拡張スキル。
  8つのスポット（地球/平和の使者/目指すルート/小惑星帯/対話の工房/事業のエンジン/
  世界の知恵図鑑=発射台/協力者）を持つSVGナビゲーションハブで、縦長(モバイル)と
  横長(PC)の2枚のSVGを持つ特殊構造。以下のときに必ず参照する:
  - 「ロケット図」「全体図」「rocket-map」「ロケットの扉」「発射台の図鑑」の話題
  - rocket-map.html のSVG・レイアウト・扉リンク・アニメーションを直したいとき
  - ロケット図に区画/リンクを足したい、位置や角度を調整したいとき
  - この環境でローカルHTML/SVGの見た目をスクショで確認したいとき（Playwright手順）
  ロケット全体図・そのSVGギミック・扉リンクが話題になったら必ずこのスキルを使うこと。
---

# サイト全体図「平和な地球行きロケット」保守スキル

- リポジトリ: `/Users/morimotoyasuhito/kizukikumitate`
- 対象ファイル: `rocket-map.html`（ルート直下・variant standard・夜色 #16132a）
- 公開URL: https://kizukikumitate.com/rocket-map.html
- ナビ「目指す未来」の3項目目。index.html ヒーロー下から導線リンクあり

## 0. このページの構造（最初に必ず理解する）

- **SVGが2枚ある**。CSSメディアクエリで出し分け:
  - `.sky` … 縦長（viewBox `0 0 380 520`）。**モバイル用**。`@media(min-width:860px)` で `display:none`
  - `.sky-wide` … 横長（viewBox `0 70 940 420`）。**PC(≥860px)用**。左→右に発射台→ロケット→小惑星帯→地球と流れる構図
- 8スポット（`data-spot`）: earth / prize(平和の使者=鳩) / route(目指すルート=星) / belt(小惑星帯) /
  studio(対話の工房) / engine(事業のエンジン) / archive(世界の知恵図鑑=発射台) / crew(協力者)。
  加えて cycle(コイン・engine扱い・aria-hidden)
- 案内板 `.rkt-panel` はSVGの下。スポットをクリック（PCはホバーでも）すると `SPOTS[key]` の
  tag/title/desc/doors に切り替わる。JSは末尾の `<script>` 内 IIFE

## 1. 扉リンクを増やす／直す（★ふつうは手を出さない＝自動生成）

**belt / studio / engine / archive の4区画の扉は `data/nav.json` から自動生成される。**
`rocket-map.html` を手で編集しない。ページを足したいなら nav.json を直すだけ。

- 生成器: `scripts/update-rocket-map.py`（`data/nav.json` の該当グループ→doors配列を再生成）
  - belt←「未来のリスク計算機」/ studio←「手法・ワークショップ」/ engine←「ソリューション」/
    archive←「世界の知恵」（archiveは `nobel-peace.html` を除外＝鳩に集約。外部リンクhttp/mailtoも除外）
- 生成物は `/* AUTO:<spot> … */ 〜 /* /AUTO:<spot> */` マーカーの内側。**この中は手編集しない**
- GitHub Actions `.github/workflows/update-nav.yml` に生成ステップ入り＝**nav.jsonにページを足してpushすれば扉も自動追従**
- ローカル手動実行: `python3 scripts/update-rocket-map.py`（生成）/ `--check`（検証・要更新ならexit1）
- 物語スポット（earth=roadmap.html#evidence / prize=nobel-peace.html / route=roadmap+ashimoto /
  crew=mailto）は**手書き**。SPOTS内の該当doorsを直接編集してよい

手順（例: 図鑑を1冊増やす）:
1. `data/nav.json` の「世界の知恵」children に1行追加（`{ "label": "...", "href": "xxx-zukan.html" }`）
2. `python3 scripts/update-rocket-map.py` を実行（ローカル確認）→ archiveの扉に反映される
3. `python3 scripts/update-nav.py`（ナビ本体も更新）→ 完了。pushすればActionsが同じことを再現

## 2. SVGの見た目・アニメを直す（★2枚とも直す）

**ロケットの絵・アニメを変えるときは `.sky`(縦長) と `.sky-wide`(横長) の両方を直す。** 片方だけだと
PC/モバイルで食い違う。横長版は各グループを `<g transform="translate(dx,dy)">` で再配置した複製:

- 複製スポットのidは **`-w` 接尾辞**（spot-earth-w 等）で重複回避。`data-spot` は共通（earth等）
- 地球グラデは横長側だけ `id="earthsea-w"`（id重複回避）
- コインの公転: 縦長は `transform-box:view-box; transform-origin:252px 322px`（モバイルでfill-boxが
  効かず流れ星化する不具合対策）。横長は `.coin-orbit-w{transform-box:fill-box}`（PC限定なのでfill-boxで可）
- ロケットの機首角: 縦長 `rotate(45 165 285)`（真上の地球へ）/ 横長 `rotate(72 165 285)`（右上の地球へ）
- fill-box+origin:center を使う他のアニメ（gear-spin/roid/dove-orbit/earth-float/flame/cheer/logo-rock）は
  各自の中心で回るので translate 再配置しても壊れない
- 位置は横長生成時の translate 値で管理。大きく組み替えるときは各グループの translate(dx,dy) を調整
- `prefers-reduced-motion` で全アニメ停止する記述を維持すること

## 3. PC横長レイアウトの約束

- `.sky-wide{ width:auto; height:min(44vh, 448px); max-width:100% }` … 高さ基準で1画面に収める
- viewBox上下クロップ（`0 70 940 420`）で空きスペースを詰め全体を上へ
- **ナビは `position:fixed`（高さ約57px）**。`.rocket-map` の padding-top と `.rkt-wrap` の padding-top の
  合計を**約70px以上**確保しないと、見出しがナビの裏に隠れる（詰めすぎ注意）
- ホバー可能端末（`(hover:hover)`）では全スポットに `mouseenter`→`show()`。カーソルを合わせるだけで
  案内板に内容プレビュー。クリック/Enter/Spaceも維持（タッチ用）
- 扉が最多の区画（archive/belt=7〜9個）の案内板が最も高い。小型ノートPC(768px)でも図＋案内板が
  1画面に収まることを目視確認する（下の検証手順）

## 4. 見た目の検証（この環境はブラウザ描画スクショ不可 → Playwright を使う）

アプリ内ブラウザ(mcp__Claude_Browser)はローカルHTMLを静的スナップショット化しスクショできない。
mobile-preflight の Playwright もサンドボックスでChromium起動に失敗する。**次の手順で目視検証する:**

1. `assets/shot.mjs`（このスキル同梱）を `.claude/scripts/` にコピー（node_modulesのplaywrightを解決するため必ずこのディレクトリで実行）
2. `node .claude/scripts/shot.mjs <絶対パス.html> <出力.png> [幅] [高さ] [hoverセレクタ]` を
   **`dangerouslyDisableSandbox: true`** で実行（例: `... rocket-map.html out.png 1366 820 "#spot-archive-w"`）
3. 出力PNGを Read ツールで開いて目視。JSエラーはコンソールに出力される
4. 終わったらコピーした一時 `.claude/scripts/shot.mjs` は削除
- 幅を変えて PC(1366) と モバイル(390) の両方を確認する。`.claude/scripts/build-ogp.sh` と同じ経路

## 5. コミット前

1. `./.claude/scripts/mobile-preflight.sh check rocket-map.html`（静的5項目PASS）
2. `python3 scripts/update-rocket-map.py --check`（扉が台帳と一致）
3. 変更ファイルを**明示指定**して `git add`（`git add -A` 禁止）→ 日本語メッセージでコミット
4. push後 https://kizukikumitate.com/rocket-map.html を確認（GitHub Pages反映2〜3分）

## やってはいけないこと

- ❌ `/* AUTO:<spot> */` マーカー内（belt/studio/engine/archive の扉）を手編集しない → nav.json を直す
- ❌ ロケットの絵・アニメを片方のSVGだけ直さない（`.sky` と `.sky-wide` は必ず両方）
- ❌ 複製スポットの id 重複（`-w` 接尾辞を必ず付ける）。id重複はホバー/アクティブ判定を壊す
- ❌ PC padding-top を詰めすぎて見出しを固定ナビの裏に隠さない（合計70px目安）
- ❌ `git add -A` 禁止（未追跡の od-overflow-check.html / preview-diagram.html を巻き込むとCIが落ちる）
- ❌ archive に nobel-peace.html を戻さない（ノーベル平和賞は鳩=平和の使者に本籍を一本化）
- ❌ 新規ページを nav.json に足したら sitemap.xml への追記も忘れない（自動化されていない）

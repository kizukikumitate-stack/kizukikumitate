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
  - `.sky` … 縦長（viewBox `0 0 380 584`）。**モバイル用**。`@media(min-width:860px)` で `display:none`
  - `.sky-wide` … 横長（viewBox `0 70 940 420`）。**PC(≥860px)用**。左→右に発射台→ロケット→小惑星帯→地球と流れる構図
- 9スポット（`data-spot`）: earth / prize(平和の使者=鳩) / route(目指すルート=星) / belt(小惑星帯) /
  studio(対話の工房) / engine(事業のエンジン) / archive(世界の知恵図鑑=発射台) / crew(協力者=本機の左上を並走する小型ロケット3機) /
  vein(未来への鉱脈=眠るお金図鑑・手書きの物語スポット)。加えて cycle(コイン・engine扱い・aria-hidden)
- vein は物語スポット（手書き）。SPOTS.vein と `BASE_KEYS`（進捗カウンタ `N/9` と隠し部屋の解錠数の
  両方がこの配列長で決まる）に追加済み。区画を増減したら HTML の `見てまわった区画 …/9` と
  cockpit の desc「9つの区画」も手で合わせる。縦SVGは vein 用に viewBox 高さを 584 に拡張済み
- 案内板 `.rkt-panel` はSVGの下。スポットをクリック（PCはホバーでも）すると `SPOTS[key]` の
  tag/title/desc/doors に切り替わる。JSは末尾の `<script>` 内 IIFE

## 1. 扉リンクを増やす／直す（★ふつうは手を出さない＝自動生成）

**belt / studio / engine / archive の4区画の扉は `data/nav.json` から自動生成される。**
`rocket-map.html` を手で編集しない。ページを足したいなら nav.json を直すだけ。

- 生成器: `scripts/update-rocket-map.py`（`data/nav.json` の該当グループ→doors配列を再生成）
  - belt←「未来のリスク計算機」/ studio←「手法・ワークショップ」/ engine←「ソリューション」/
    archive←「世界の知恵」。外部リンク(http/mailto)は除外。さらに `MAPPING` の除外セットで
    個別ページを外せる（現状 `nobel-peace.html`＝鳩に集約 / `nemuru-okane-zukan.html`＝鉱脈に集約）
- 生成物は `/* AUTO:<spot> … */ 〜 /* /AUTO:<spot> */` マーカーの内側。**この中は手編集しない**
- GitHub Actions `.github/workflows/update-nav.yml` に生成ステップ入り＝**nav.jsonにページを足してpushすれば扉も自動追従**
- ローカル手動実行: `python3 scripts/update-rocket-map.py`（生成）/ `--check`（検証・要更新ならexit1）
- 物語スポット（earth=roadmap.html#evidence / prize=nobel-peace.html / route=roadmap+ashimoto /
  crew=mailto）は**手書き**。SPOTS内の該当doorsを直接編集してよい

手順（例: 図鑑を1冊増やす）:
1. `data/nav.json` の「世界の知恵」children に1行追加（`{ "label": "...", "href": "xxx-zukan.html" }`）
2. `python3 scripts/update-rocket-map.py` を実行（ローカル確認）→ archiveの扉に反映される
3. `python3 scripts/update-nav.py`（ナビ本体も更新）→ 完了。pushすればActionsが同じことを再現

手順（例: あるページを1区画の扉からだけ外す＝本籍を別スポットに一本化する）:
- グローバルナビ(nav.json)には残したまま、rocket-map の特定スポットの扉からだけ消したいとき。
  「そのページは本来べつのスポットの物語だ」という場合に使う（例: 眠るお金図鑑は発射台=archiveではなく
  未来への鉱脈=vein の物語）。**nav.json は触らない。**
1. `scripts/update-rocket-map.py` の `MAPPING` で、対象スポットの除外セットに href を追加
   （例: `"archive": ("世界の知恵", {"nobel-peace.html", "nemuru-okane-zukan.html"})`）
2. `python3 scripts/update-rocket-map.py` で再生成 → その扉だけ消える。行き先スポット(vein等)の
   手書き doors 側にリンクが残っていることを確認する（両方から消してしまわない）

## 2. SVGの見た目・アニメを直す（★2枚とも直す）

**ロケットの絵・アニメを変えるときは `.sky`(縦長) と `.sky-wide`(横長) の両方を直す。** 片方だけだと
PC/モバイルで食い違う。横長版は各グループを `<g transform="translate(dx,dy)">` で再配置した複製:

- 複製スポットのidは **`-w` 接尾辞**（spot-earth-w 等）で重複回避。`data-spot` は共通（earth等）
- 地球グラデは横長側だけ `id="earthsea-w"`（id重複回避）
- コインの公転: 縦長は `transform-box:view-box; transform-origin:252px 322px`（モバイルでfill-boxが
  効かず流れ星化する不具合対策）。横長は `.coin-orbit-w{transform-box:fill-box}`（PC限定なのでfill-boxで可）
- ロケットの機首角は「地球へのルート(点線軌道)」に合わせる。縦長と横長でルート角が違うので値も違う:
  縦長 `rotate(33 165 285)`（急な軌道の地球へ）/ 横長 `rotate(72 165 285)`（浅い軌道の地球へ）。
  角度を変えるときは、その向きが実際に地球・点線ルートを向くか必ずレンダリングで確認する
- fill-box+origin:center を使う他のアニメ（gear-spin/roid/dove-orbit/earth-float/flame/logo-rock）は
  各自の中心で回るので translate 再配置しても壊れない
- 位置は横長生成時の translate 値で管理。大きく組み替えるときは各グループの translate(dx,dy) を調整
- `prefers-reduced-motion` で全アニメ停止する記述を維持すること（新アニメを足したらこの一覧にも追加）

### crew(協力者)＝本機の左上を並走する小型ロケット3機（橙#d85a30/緑#0f6e56/金#d9a441）

- 白ボディ＋色付きノーズ/フィン/窓の小型ロケットを本機と同じ機首角で並走させた編隊。両SVGにある
- **「抜きつ抜かれつ」アニメ**: 各機を `.esc / .esc.e2 / .esc.e3` クラスにし、`@keyframes rkt-esc1/2/3`
  で機軸方向(local Y)に前後させる。周期と位相を1機ずつずらすと追い越し合って見える。3機は横位置が
  違う＝別レーンなので交差しても衝突しない。`prefers-reduced-motion` の停止一覧に `.esc` 追加済み
- myflag(記帳フラグ)はいまも `.cheer`（上下バウンス）。cheer と esc は別物なので混同しない

### ★最重要の落とし穴: 位置決めtransform属性 と CSSアニメのtransform は両立しない

CSSアニメの `transform`（例 `translateY`）は、その要素の `transform=""` 属性を**丸ごと上書き**する。
だから「translate/rotate/scale で置いた要素」に直接アニメclassを付けると、位置が原点に飛ぶ。
**必ず入れ子にする**: 外側 `<g transform="translate(..) rotate(..) scale(..)">`（位置決め）→
内側 `<g class="esc e2">`（動き）。内側の translateY は外側の回転後ローカル座標＝機軸方向になる（＝前後動として効く）。
flame の scaleY は葉ノードで独立に効くので入れ子の中でもOK。

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
2. `node .claude/scripts/shot.mjs <絶対パス.html> <出力.png> [幅] [高さ] [hoverセレクタ] [clipセレクタ] [clip高さ割合] [clip上端オフセット]` を
   **`dangerouslyDisableSandbox: true`** で実行（例: `... rocket-map.html out.png 1366 1000`）
   - **イントロ演出は自動でスキップ**する（shot.mjs が「スキップ」ボタンを押し #rocket-map まで
     スクロールしてから撮る）。撮影前にカウントダウンの残像が写るのはこの待ちが足りないだけ
   - **部分拡大**は clip 引数: 例 `... out.png 390 1500 "" ".sky" 0.55 0.04`＝縦SVGの上半分を2倍解像度で。
     文字と機体・小惑星の重なりを詰めるときはこの拡大で1px単位に確認する
3. 出力PNGを Read ツールで開いて目視。JSエラーはコンソールに出力される
4. 終わったらコピーした一時 `.claude/scripts/shot.mjs`（clip用の派生も）は削除
- 幅を変えて PC(1366) と モバイル(390) の両方を確認する。`.claude/scripts/build-ogp.sh` と同じ経路
- **座標調整は必ずレンダリング→目視→微調整のループで**。縦SVGは上部（地球/ルート星/小惑星帯/本機機首/
  編隊）が密集して重なりやすい。ラベルと小惑星・機体の重なりは計算だけで詰めきれないので撮って直す

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
- ❌ archive の扉に nobel-peace.html / nemuru-okane-zukan.html を戻さない（前者は鳩、後者は鉱脈に本籍を一本化）
- ❌ 位置決め transform 属性を持つ要素に、CSSアニメで transform を掛けない（属性が上書きされ原点に飛ぶ）。
  位置決めと動きは必ず入れ子の別グループに分ける（上の「最重要の落とし穴」参照）
- ❌ 機首角を変えたら地球ルートとのズレを撮って確認せずに終わらない（縦横でルート角が違う）
- ❌ 新規ページを nav.json に足したら sitemap.xml への追記も忘れない（自動化されていない）

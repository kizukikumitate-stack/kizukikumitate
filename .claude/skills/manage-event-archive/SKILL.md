---
name: manage-event-archive
description: |
  democracy-fitness.html のイベント一覧で、終了日時を過ぎたイベントを自動で
  「過去の開催」へ移動する仕組み（自動アーカイブ）を扱うスキル。

  以下のタイミングで必ず参照する:
  - 「今後のイベント予定」に新しいイベントカードを追加・編集するとき
    （自動アーカイブされる形式で書く必要があるため）
  - 「イベントが過去に移動しない」「実施済みにならない」と報告を受けたとき
  - アーカイブのスクリプト / GitHub Actions ワークフローを変更・調査するとき

  キーワード: 「イベント追加」「体験会を載せる」「実施済み」「過去の開催」
  「アーカイブ」「終了したイベント」「自動で移動」が出たら適用する。
---

# イベント自動アーカイブ スキル

`democracy-fitness.html` の「今後のイベント予定」に並ぶイベントカードは、
**終了日時(JST)を過ぎると自動で「過去の開催」へ移動**する。
この自動化を壊さずにイベントを追加・編集・保守するための手順書。

## 仕組みの全体像（3要素）

| ファイル | 役割 |
|---|---|
| `democracy-fitness.html` | 予定カードにメタデータとマーカーを持たせる（下記の形式契約） |
| `scripts/archive-events.py` | 終了日時を過ぎたカードを past 形式に整形し「過去の開催」先頭へ移動 |
| `.github/workflows/archive-events.yml` | 6時間ごと(cron `0 */6 * * *`)＋手動で上記スクリプトを実行し、変更があれば bot がコミット |

処理は **該当カードのブロックだけを文字列置換**するので、HTML 全体は再整形されず差分は最小。

## ⭐ 新しいイベントを追加するときの形式契約（最重要）

「今後のイベント予定」グリッド（`<div class="events-grid fade-up">` 〜 `</div>`、
`<!-- ===== 過去のイベント ===== -->` より前）に、**必ず次の形**でカードを追加する。

```html
      <!-- EVENT START -->
      <!-- イベントカード：〇〇 -->
      <div class="event-card" data-event-end="2026-09-30T20:00" data-region="大阪開催">
        <div class="event-card-meta">
          <div class="event-card-tag">2時間体験</div>
          <div class="event-card-title">デモクラシーフィットネス体験会 in 〇〇<br>— サブタイトル</div>
          <div class="event-card-details">
            <div class="event-card-detail">📅 <span>2026年9月30日（火）18:00〜20:00</span></div>
            <div class="event-card-detail">📍 <span>会場名</span></div>
            <div class="event-card-detail">💴 <span>¥2,500</span></div>
          </div>
        </div>
        <a href="申込ページURL" class="event-card-btn" target="_blank" rel="noopener">
          詳細・お申込みへ →
        </a>
      </div>
      <!-- EVENT END -->
```

必須ポイント（**1つでも欠けると自動移動されない／壊れる**）:

1. `<!-- EVENT START -->` と `<!-- EVENT END -->` でカード全体を囲む
2. `div.event-card` に次の2属性を付ける:
   - `data-event-end="YYYY-MM-DDTHH:MM"` … **イベント終了日時(JST)**。
     - 終了時刻が分かるならその時刻（例 `2026-09-30T20:00`）
     - 日付のみ／合宿など複数日は **最終日の終了見込み**（例 終日なら `T23:59`、合宿2日目18時なら `2026-08-12T18:00`）
   - `data-region="〇〇開催"` … past カードのタグに `終了 / 〇〇開催` として表示される地域ラベル
3. タイトルのサブタイトルは `<br>` 区切り（アーカイブ時に `<br>` 以降は自動で落とされる）
4. 詳細行のうち **📅 と 📍 はアーカイブ後も残る**。💴 / 👥 / 🎯 等はアーカイブ時に自動で除去される

> 既に過ぎた日付のイベントを「最初から過去の開催として」載せたい場合は、
> 上記マーカーは付けず、`<!-- PAST EVENTS INSERT -->` の下にある既存の past カード
> （`class="event-card past"`、タグ `終了 / 〇〇開催`、ボタン `event-card-btn past`）と
> 同じ形で手書きで追加する。

## アーカイブ後の見た目（スクリプトが生成する past 形式）

```html
      <!-- 〇〇開催（自動アーカイブ） -->
      <div class="event-card past">
        <div class="event-card-meta">
          <div class="event-card-tag">終了 / 〇〇開催</div>
          <div class="event-card-title">（サブタイトルを除いたタイトル）</div>
          <div class="event-card-details">
            <div class="event-card-detail">📅 ...</div>
            <div class="event-card-detail">📍 ...</div>
          </div>
        </div>
        <a href="（元のhref）" class="event-card-btn past" target="_blank" rel="noopener">
          イベント詳細 →
        </a>
      </div>
```

挿入位置は `<!-- PAST EVENTS INSERT -->` の直後＝過去の開催の先頭。複数同時なら終了日時の**新しい順**。

## 動作テスト（時刻を注入して確認）

実時刻ではなく任意時刻を「現在」として判定できる。**必ずバックアップを取ってから**実行する。

```bash
cd /Users/morimotoyasuhito/kizukikumitate
cp democracy-fitness.html "$TMPDIR/df.bak"            # バックアップ
ARCHIVE_NOW="2026-12-31T00:00" python3 scripts/archive-events.py   # 全イベントを過去扱いで実行
# → 出力と過去の開催セクションを確認
cp "$TMPDIR/df.bak" democracy-fitness.html            # 復元
```

実時刻での空振り確認（移動対象が無ければ「移動対象なし」と出てファイル無変更）:

```bash
python3 scripts/archive-events.py && git diff --stat democracy-fitness.html
```

## マーカーの整合性チェック

```bash
cd /Users/morimotoyasuhito/kizukikumitate
echo "START=$(grep -c 'EVENT START' democracy-fitness.html) END=$(grep -c 'EVENT END' democracy-fitness.html) INSERT=$(grep -c 'PAST EVENTS INSERT' democracy-fitness.html)"
```

`START` と `END` は同数、`INSERT` は 1 であること。予定カード数＝`data-event-end` の数。

## トラブルシュート

| 症状 | 原因・対処 |
|---|---|
| イベントが過去に移動しない | カードに `EVENT START/END` マーカーか `data-event-end` が無い。上の形式契約で付け直す |
| 移動はされるがタグが変 | `data-region` 未設定（タグが `終了 / 開催` になる）。地域ラベルを設定 |
| 隣のカードも巻き込んで消える/残る | マーカーの対応がズレている。整合性チェックで START=END を確認 |
| 手動で即実行したい | GitHub の Actions タブ →「Archive Past Events」→ Run workflow（workflow_dispatch） |
| ワークフロー .yml を push できない | リモート認証のクラシックPATに `workflow` スコープが必要（付与済みのはず。無効化されたら再付与） |

## 関連

- 新規イベントページ作成は `democracy-fitness-event-setup` スキル（ページ作成＋一覧追加）。
  そのスキルで一覧に追加する際も、本スキルの形式契約に必ず合わせること。
- HTML 編集後のコミット前は `mobile-preflight-check` を実行。

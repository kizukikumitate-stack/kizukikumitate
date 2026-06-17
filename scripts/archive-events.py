#!/usr/bin/env python3
"""
終了したイベントを各ページから自動で片付ける。

対象1: democracy-fitness.html（イベント一覧）
  終了日時を過ぎた「今後のイベント予定」カードを「過去の開催」へ移動する。
  予定カードは <!-- EVENT START --> ... <!-- EVENT END --> で囲み、
  <div class="event-card" data-event-end="YYYY-MM-DDTHH:MM" data-region="〇〇開催"> を持つ。
  data-event-end（JST）を過ぎたら past 形式に整形し、<!-- PAST EVENTS INSERT --> の
  直後（過去の開催の先頭）へ新しい順で差し込み、予定側から削除する。

対象2: index.html（トップページの「今後のイベント」プレビュー）
  過去セクションが無いので、開催日 <div class="event-date">YYYY.MM.DD</div> が
  今日(JST)より前のカードは単純に削除する（移動先なし）。

いずれも元HTMLは該当カードのブロックのみ文字列置換するので、差分は最小限。

動かし方: GitHub Actions から呼ばれる。手動なら `python3 scripts/archive-events.py`。
テスト用: 環境変数 ARCHIVE_NOW="2026-07-01T00:00" を渡すと、その時刻を「現在」として判定する。
"""

import os
import re
import sys
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(REPO, "democracy-fitness.html")
INDEX_TARGET = os.path.join(REPO, "index.html")

INSERT_MARKER = "<!-- PAST EVENTS INSERT -->"
BLOCK_RE = re.compile(
    r"[ \t]*<!-- EVENT START -->.*?<!-- EVENT END -->[ \t]*\n(?:[ \t]*\n)?",
    re.DOTALL,
)
# index.html のイベントカード（4スペース字下げの event-card ブロック）
INDEX_CARD_RE = re.compile(
    r'[ \t]*<div class="event-card">.*?\n    </div>\n',
    re.DOTALL,
)
INDEX_DATE_RE = re.compile(r'<div class="event-date">(\d{4})\.(\d{2})\.(\d{2})</div>')


def now_jst():
    override = os.environ.get("ARCHIVE_NOW")
    if override:
        return datetime.fromisoformat(override).replace(tzinfo=JST)
    return datetime.now(JST)


def parse_attr(block, name):
    m = re.search(name + r'="([^"]*)"', block)
    return m.group(1) if m else ""


def build_past_card(block, region):
    """予定カードのブロック文字列から past 形式のカード文字列を生成する。"""
    href = parse_attr(block, "href")

    title_m = re.search(r'<div class="event-card-title">(.*?)</div>', block, re.DOTALL)
    title = title_m.group(1) if title_m else ""
    title_main = re.split(r"<br\s*/?>", title)[0].strip()

    # 📅 と 📍 の detail 行だけ残す
    details = re.findall(r'<div class="event-card-detail">.*?</div>', block, re.DOTALL)
    kept = [d for d in details if d.startswith('<div class="event-card-detail">📅')
            or d.startswith('<div class="event-card-detail">📍')]
    detail_lines = "\n".join("            " + d for d in kept)

    return (
        f"\n      <!-- {region}（自動アーカイブ） -->\n"
        f'      <div class="event-card past">\n'
        f'        <div class="event-card-meta">\n'
        f'          <div class="event-card-tag">終了 / {region}</div>\n'
        f'          <div class="event-card-title">{title_main}</div>\n'
        f'          <div class="event-card-details">\n'
        f"{detail_lines}\n"
        f"          </div>\n"
        f"        </div>\n"
        f'        <a href="{href}" class="event-card-btn past" target="_blank" rel="noopener">\n'
        f"          イベント詳細 →\n"
        f"        </a>\n"
        f"      </div>\n"
    )


def archive_detail_page(now):
    """democracy-fitness.html: 終了したカードを「過去の開催」へ移動。戻り値=移動件数。"""
    with open(TARGET, encoding="utf-8") as f:
        html = f.read()

    if INSERT_MARKER not in html:
        print("ERROR: 挿入マーカーが見つかりません:", INSERT_MARKER, file=sys.stderr)
        return -1

    expired = []  # (end_datetime, past_card_html)

    def replace_block(m):
        block = m.group(0)
        end_str = parse_attr(block, "data-event-end")
        if not end_str:
            return block  # 日時が無いカードは触らない
        try:
            end_dt = datetime.fromisoformat(end_str).replace(tzinfo=JST)
        except ValueError:
            print(f"WARN: data-event-end を解釈できません: {end_str!r}", file=sys.stderr)
            return block
        if now <= end_dt:
            return block  # まだ終了していない
        region = parse_attr(block, "data-region") or "開催"
        expired.append((end_dt, build_past_card(block, region)))
        return ""  # 予定側から削除

    new_html = BLOCK_RE.sub(replace_block, html)

    if not expired:
        print("[democracy-fitness.html] 移動対象なし")
        return 0

    # 新しい順（終了日時の降順）に並べ、過去の開催の先頭へ差し込む
    expired.sort(key=lambda x: x[0], reverse=True)
    insert_html = "".join(card for _, card in expired)
    new_html = new_html.replace(INSERT_MARKER, INSERT_MARKER + insert_html, 1)

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new_html)

    for end_dt, _ in expired:
        print(f"[democracy-fitness.html] 過去の開催へ移動: 終了 {end_dt:%Y-%m-%d %H:%M}")
    print(f"[democracy-fitness.html] 合計 {len(expired)} 件を移動")
    return len(expired)


def prune_index_page(today):
    """index.html: 開催日が today より前のプレビューカードを削除。戻り値=削除件数。"""
    with open(INDEX_TARGET, encoding="utf-8") as f:
        html = f.read()

    removed = []

    def replace_card(m):
        block = m.group(0)
        dm = INDEX_DATE_RE.search(block)
        if not dm:
            return block  # 日付が無いカードは触らない
        d = datetime(int(dm.group(1)), int(dm.group(2)), int(dm.group(3))).date()
        if d < today:
            removed.append(d)
            return ""  # 過去の開催は削除
        return block

    new_html = INDEX_CARD_RE.sub(replace_card, html)

    if not removed:
        print("[index.html] 削除対象なし")
        return 0

    with open(INDEX_TARGET, "w", encoding="utf-8") as f:
        f.write(new_html)

    for d in sorted(removed, reverse=True):
        print(f"[index.html] 終了したプレビューを削除: {d:%Y-%m-%d}")
    print(f"[index.html] 合計 {len(removed)} 件を削除")
    return len(removed)


def main():
    now = now_jst()
    rc1 = archive_detail_page(now)
    rc2 = prune_index_page(now.date())
    if rc1 < 0 or rc2 < 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

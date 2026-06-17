#!/usr/bin/env python3
"""
終了日時を過ぎた「今後のイベント予定」カードを自動で「過去の開催」へ移動する。

対象ファイル: democracy-fitness.html
動かし方: GitHub Actions（毎日）から呼ばれる。手動なら `python3 scripts/archive-events.py`。

仕組み:
- 予定カードは <!-- EVENT START --> ... <!-- EVENT END --> で囲み、
  <div class="event-card" data-event-end="YYYY-MM-DDTHH:MM" data-region="〇〇開催"> を持つ。
- data-event-end（JST）を現在時刻（JST）が過ぎていたら、そのカードを past 形式に整形して
  <!-- PAST EVENTS INSERT --> の直後（＝過去の開催の先頭）へ新しい順で差し込み、予定側から削除する。
- 元HTMLは該当ブロックのみ文字列置換するので、差分は最小限。

テスト用: 環境変数 ARCHIVE_NOW="2026-07-01T00:00" を渡すと、その時刻を「現在」として判定する。
"""

import os
import re
import sys
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))
TARGET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "democracy-fitness.html")

INSERT_MARKER = "<!-- PAST EVENTS INSERT -->"
BLOCK_RE = re.compile(
    r"[ \t]*<!-- EVENT START -->.*?<!-- EVENT END -->[ \t]*\n(?:[ \t]*\n)?",
    re.DOTALL,
)


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


def main():
    with open(TARGET, encoding="utf-8") as f:
        html = f.read()

    if INSERT_MARKER not in html:
        print("ERROR: 挿入マーカーが見つかりません:", INSERT_MARKER, file=sys.stderr)
        return 1

    now = now_jst()
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
        print("移動対象なし（終了したイベントはありません）")
        return 0

    # 新しい順（終了日時の降順）に並べ、過去の開催の先頭へ差し込む
    expired.sort(key=lambda x: x[0], reverse=True)
    insert_html = "".join(card for _, card in expired)
    new_html = new_html.replace(INSERT_MARKER, INSERT_MARKER + insert_html, 1)

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new_html)

    for end_dt, _ in expired:
        print(f"アーカイブ: 終了 {end_dt:%Y-%m-%d %H:%M} のイベントを過去の開催へ移動")
    print(f"合計 {len(expired)} 件を移動しました。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

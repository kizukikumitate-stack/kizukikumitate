#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ロケット全体図（rocket-map.html）の「扉」リンクを data/nav.json から自動生成する。

サイト全体図のうち、コンテンツが増えていく区画（＝ハンバーガーのグループそのもの）の
扉リンクは、この台帳駆動で自動追従させる。図鑑・ソリューション・計算機などにページを足して
data/nav.json を更新すれば、ロケット図の扉も一緒に更新される（nav / footer / kaiyu と同じ思想）。

対象は rocket-map.html の SPOTS 内、各 `doors:` を
  /* AUTO:<spot> ... */   〜   /* /AUTO:<spot> */
で囲んだ4区画のみ。物語スポット（地球・平和の使者・目指すルート・協力者）は手書きのまま。

使い方:
  python3 scripts/update-rocket-map.py           # 生成（rocket-map.html を書き換え）
  python3 scripts/update-rocket-map.py --check    # 検証のみ（要更新なら exit 1）
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV = os.path.join(ROOT, "data", "nav.json")
PAGE = os.path.join(ROOT, "rocket-map.html")

# spot → (ナビのグループ label, 除外する href のセット)
#   ノーベル平和賞は鳩(平和の使者)スポットに本籍を一本化しているので、発射台(archive)からは除外。
#   眠るお金図鑑は未来への鉱脈(vein)スポットに本籍を一本化しているので、発射台(archive)からは除外。
MAPPING = {
    "belt":    ("未来のリスク計算機", set()),
    "studio":  ("手法・ワークショップ", set()),
    "engine":  ("ソリューション", set()),
    "archive": ("世界の知恵", {"nobel-peace.html", "nemuru-okane-zukan.html"}),
}


def nav_group_children(nav, label):
    for item in nav["nav"]["items"]:
        if item.get("label") == label:
            return item.get("children", [])
    raise SystemExit(f"❌ data/nav.json にグループ「{label}」が見つかりません")


def build_doors(nav):
    """spot → 生成する扉エントリ行（8スペース字下げ・末尾カンマなし）"""
    out = {}
    for spot, (group, exclude) in MAPPING.items():
        rows = []
        for child in nav_group_children(nav, group):
            if "href" not in child:
                continue  # 見出し行（{"heading": ...}）は扉にしない
            href = child["href"]
            if href.startswith(("http://", "https://", "mailto:")):
                continue  # 外部リンクは扉にしない
            if href in exclude:
                continue
            label = child["label"]
            rows.append('        [%s, %s]' % (
                json.dumps(label, ensure_ascii=False),
                json.dumps(href, ensure_ascii=False),
            ))
        if not rows:
            raise SystemExit(f"❌ spot「{spot}」の扉が0件になりました（グループ {group} を確認）")
        out[spot] = ",\n".join(rows)
    return out


def regenerate(html, doors):
    changed = []
    for spot, body in doors.items():
        pat = re.compile(
            r'(/\* AUTO:%s\b[^\n]*\*/\n)(.*?)(\n[ \t]*/\* /AUTO:%s \*/)' % (spot, spot),
            re.DOTALL,
        )
        m = pat.search(html)
        if not m:
            raise SystemExit(f"❌ rocket-map.html に AUTO:{spot} マーカーが見つかりません")
        if m.group(2) != "\n" + body:
            changed.append(spot)
        html = pat.sub(lambda mm: mm.group(1) + "\n" + body + mm.group(3), html, count=1)
    return html, changed


def main():
    check = "--check" in sys.argv
    nav = json.load(open(NAV, encoding="utf-8"))
    html = open(PAGE, encoding="utf-8").read()
    new_html, changed = regenerate(html, build_doors(nav))

    if not changed:
        print("✅ rocket-map.html の扉は data/nav.json と一致しています（更新なし）")
        return

    if check:
        print("❌ 要更新:", ", ".join(changed), "→ python3 scripts/update-rocket-map.py を実行してください")
        sys.exit(1)

    open(PAGE, "w", encoding="utf-8").write(new_html)
    print("✏️  rocket-map.html の扉を更新:", ", ".join(changed))


if __name__ == "__main__":
    main()

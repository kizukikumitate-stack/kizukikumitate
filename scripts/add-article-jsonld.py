#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add-article-jsonld.py — 図鑑・エッセイ系ページに Article 構造化データ（JSON-LD）を冪等付与する。

AI検索対策（GEO）の一環。author を必ず「事実の台帳」ページ(#yasuhito-morimoto)に、
publisher を #org に紐づけ、AIが「著者は誰か → 検証可能なプロフィールがある」と辿れるようにする。

- 対象は下の ARTICLE_PAGES のみ（トップ・計算機・イベント・妖怪・サービスLP・法定表記は対象外）。
- 各ページに既に Article JSON-LD があればスキップ（何度実行しても二重挿入しない）。
- headline は <title> から、url は <link rel="canonical"> から取得。
- datePublished / dateModified は git のコミット履歴（初回追加 / 最終更新）から取得。
    実行:  python3 scripts/add-article-jsonld.py
    検証:  python3 scripts/add-article-jsonld.py --check   （未付与ページの一覧のみ・書き込まない）
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://kizukikumitate.com/"

# 図鑑・エッセイ（長文コンテンツ）ページ。サービスLP・ツール・イベント・妖怪世界観は含めない。
ARTICLE_PAGES = [
    "dialogue-zukan.html",
    "shikumi-zukan.html",
    "poverty-zukan.html",
    "ted-collection.html",
    "nigate-zukan.html",
    "chie-zukan.html",
    "alternative-education-zukan.html",
    "education-roi-zukan.html",
    "1on1-zukan.html",
    "rest-productivity-zukan.html",
    "career-theory-zukan.html",
    "jirei.html",
    "jirei-shotengai.html",
    "jirei-kenshu.html",
    "jirei-career.html",
    "hininchi-zukan.html",
    "growth-laws-zukan.html",
    "reflection-zukan.html",
    "goikeisei-zukan.html",
    "nemuru-okane-zukan.html",
    "shinkei-busshitsu-zukan.html",
    "systems-thinking-zukan.html",
    "roadmap.html",
    "ashimoto-map.html",
    "nobel-peace.html",
]

TODAY = "2026-07-19"  # gitに履歴が無い場合のフォールバック（Date.now非依存で固定）


def git_date(path, first):
    """ファイルの初回追加日(first=True) or 最終更新日(first=False)を YYYY-MM-DD で返す。"""
    try:
        out = subprocess.run(
            ["git", "log", "--follow", "--format=%ad", "--date=short", "--", path],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip().splitlines()
        if not out:
            return TODAY
        return out[-1] if first else out[0]
    except Exception:
        return TODAY


def extract(pattern, html, default=""):
    m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else default


def headline_from_title(title):
    # サイト名・サブタイトルなどの接尾辞を落として記事見出しにする（全角｜/半角|の両対応）
    for sep in ("｜", "|"):
        if sep in title:
            title = title.split(sep)[0]
            break
    return title.strip()


def build_jsonld(headline, url, published, modified, image):
    # 手組みで整形（json.dumpsだと @id 参照の見た目が崩れるため既存テンプレに合わせる）
    image_line = f'  "image": {json_str(image)},\n' if image else ""
    return (
        '<!-- ===== AI・検索エンジン向け構造化データ（Article） ===== -->\n'
        '<script type="application/ld+json">\n'
        '{\n'
        '  "@context": "https://schema.org",\n'
        '  "@type": "Article",\n'
        f'  "headline": {json_str(headline)},\n'
        f'  "url": {json_str(url)},\n'
        f'{image_line}'
        f'  "datePublished": "{published}",\n'
        f'  "dateModified": "{modified}",\n'
        '  "author": {\n'
        '    "@type": "Person",\n'
        '    "@id": "https://kizukikumitate.com/#yasuhito-morimoto",\n'
        '    "name": "森本康仁",\n'
        '    "url": "https://kizukikumitate.com/jijitsu-daicho.html"\n'
        '  },\n'
        '  "publisher": {\n'
        '    "@type": "Organization",\n'
        '    "@id": "https://kizukikumitate.com/#org",\n'
        '    "name": "きづきくみたて工房",\n'
        '    "logo": {\n'
        '      "@type": "ImageObject",\n'
        '      "url": "https://kizukikumitate.com/logotype.png"\n'
        '    }\n'
        '  },\n'
        '  "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/"\n'
        '}\n'
        '</script>\n'
    )


def json_str(s):
    # JSON文字列としてエスケープ（" と \ のみ最低限）
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    check = "--check" in sys.argv
    missing, added, skipped = [], [], []

    for name in ARTICLE_PAGES:
        path = ROOT / name
        if not path.exists():
            print(f"⚠️  ファイルなし: {name}")
            continue
        html = path.read_text(encoding="utf-8")

        if re.search(r'"@type"\s*:\s*"Article"', html):
            skipped.append(name)
            continue

        missing.append(name)
        if check:
            continue

        title = extract(r"<title>(.*?)</title>", html)
        headline = headline_from_title(title) or name
        canonical = extract(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', html)
        url = canonical or (BASE + name)
        image = extract(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html)
        published = git_date(name, first=True)
        modified = git_date(name, first=False)
        if modified < published:  # --follow のリネーム履歴で前後する場合の保険
            modified = published

        block = build_jsonld(headline, url, published, modified, image)
        if "</head>" not in html:
            print(f"⚠️  </head> なし、スキップ: {name}")
            continue
        html = html.replace("</head>", block + "</head>", 1)
        path.write_text(html, encoding="utf-8")
        added.append(name)
        print(f"✅ Article JSON-LD 付与: {name}  ({published} / {modified})  「{headline}」")

    print("\n--- 結果 ---")
    print(f"既に付与済み(スキップ): {len(skipped)}")
    if check:
        print(f"未付与: {len(missing)}")
        for n in missing:
            print(f"  - {n}")
        sys.exit(1 if missing else 0)
    print(f"新規付与: {len(added)}")


if __name__ == "__main__":
    main()

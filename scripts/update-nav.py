#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
グローバルナビ／フッターの全ページ自動同期スクリプト。

data/nav.json（唯一の正）を読み、各ページの
  <!-- NAV START --> 〜 <!-- NAV END -->     … <nav> ＋ モバイルメニュー
  <!-- FOOTER START --> 〜 <!-- FOOTER END --> … <footer>
の間を再生成する。マーカーがまだ無いページには、既存の <nav>／<footer> を
見つけて自動でマーカーを巻く（初回導入も新ページ追加もこれだけ）。

台帳に無いページを検知したら異常終了する（新ページの登録忘れをCIで落とすため）。

冪等: 出力が現状と同一なら書き換えない（GitHub Actions で差分が無ければ commit されない）。

使い方:
  python3 scripts/update-nav.py          # 検証＋生成・更新
  python3 scripts/update-nav.py --check  # 検証のみ（書き換えない・差分があれば異常終了）
"""
import html as html_mod
import json
import os
import posixpath
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "data", "nav.json")

NAV_START, NAV_END = "<!-- NAV START -->", "<!-- NAV END -->"
FOOT_START, FOOT_END = "<!-- FOOTER START -->", "<!-- FOOTER END -->"

# 走査から外すディレクトリ（サイトのページではない）
SKIP_DIRS = {".git", ".github", ".claude", "node_modules", "_img-backup"}

EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")


# ── パス解決 ────────────────────────────────────────────────

def is_external(href):
    return href.startswith(EXTERNAL_PREFIXES)


def rel_href(from_path, target):
    """ページ from_path から target（リポジトリルート基準）への相対URL。"""
    if is_external(target):
        return target
    is_dir = target.endswith("/")
    base = posixpath.dirname(from_path) or "."
    rel = posixpath.relpath(target.rstrip("/") or ".", base)
    if is_dir:
        rel = "./" if rel == "." else rel + "/"
    if not rel.startswith("."):
        rel = "./" + rel
    return rel


def as_page(target):
    """'yokai/' → 'yokai/index.html'（active判定・存在チェック用に正規化）"""
    return target + "index.html" if target.endswith("/") else target


# ── ナビ項目のレンダリング ──────────────────────────────────

def link_attrs(item, page_path):
    href = rel_href(page_path, item["href"])
    attrs = f'href="{href}"'
    if item.get("external"):
        attrs += ' target="_blank" rel="noopener"'
    if item.get("desc"):
        attrs += f' title="{html_mod.escape(item["desc"], quote=True)}"'
    if not is_external(item["href"]) and as_page(item["href"]) == page_path:
        attrs += ' class="active"'
    return attrs


def render_desktop(items, page_path):
    out = ['  <ul class="nav-links">']
    for item in items:
        if "children" not in item:
            out.append(f'    <li><a {link_attrs(item, page_path)}>{item["label"]}</a></li>')
            continue
        out.append('    <li class="nav-dropdown">')
        out.append(f'      <button class="nav-dropdown-toggle" type="button">{item["label"]} '
                   '<span class="nav-caret">▾</span></button>')
        out.append('      <div class="nav-dropdown-menu">')
        seen_heading = 0
        for child in item["children"]:
            if "heading" in child:
                sep = "" if seen_heading == 0 else "border-top:1px solid #ececf3;margin-top:.35rem;padding-top:.55rem;"
                out.append(
                    "        <span class=\"nav-dd-heading\" style=\"display:block;"
                    "font-family:'Jost','Noto Sans JP',sans-serif;font-size:.63rem;font-weight:700;"
                    "letter-spacing:.14em;color:#9a95c0;padding:.5rem 1.5rem .2rem;white-space:nowrap;"
                    f"{sep}\">{child['heading']}</span>")
                seen_heading += 1
            else:
                out.append(f'        <a {link_attrs(child, page_path)}>{child["label"]}</a>')
        out.append('      </div>')
        out.append('    </li>')
    out.append('  </ul>')
    return "\n".join(out)


def render_mobile(items, page_path):
    out = []
    for item in items:
        if "children" not in item:
            out.append(f'  <a {link_attrs(item, page_path)}>{item["label"]}</a>')
            continue
        out.append('  <div class="mobile-acc">')
        out.append(f'    <button class="mobile-acc-toggle" type="button">{item["label"]} '
                   '<span class="mobile-acc-caret">▾</span></button>')
        out.append('    <div class="mobile-acc-panel">')
        seen_heading = 0
        for child in item["children"]:
            if "heading" in child:
                sep = "" if seen_heading == 0 else "border-top:1px solid #ececf3;margin-top:.3rem;padding-top:.5rem;"
                out.append(
                    "      <span class=\"mobile-acc-heading\" style=\"display:block;"
                    "font-family:'Jost','Noto Sans JP',sans-serif;font-size:.72rem;font-weight:700;"
                    "letter-spacing:.12em;color:#9a95c0;padding:.55rem 0 .1rem;text-align:center;"
                    f"{sep}\">{child['heading']}</span>")
                seen_heading += 1
            else:
                out.append(f'      <a {link_attrs(child, page_path)}>{child["label"]}</a>')
        out.append('    </div>')
        out.append('  </div>')
    return "\n".join(out)


# ── 3つのナビ変種（外枠だけが違い、中身のリンク集は共通） ──────
#   standard : 通常ページ（.nav-hamburger#hamburger / .mobile-menu#mobileMenu）
#   event    : イベント・申込系（.global-nav-hamburger#globalHamburger / .global-mobile-menu#globalMobileMenu）
#   topaasia : topaasia系（div.hamburger#hamburger ＋ 任意で .lang-toggle）
# 各ページのJSはこのid/classを参照しているので、変種ごとに厳密に一致させること。
VARIANTS = {
    "standard": {
        "nav_open": "<nav>",
        "hamburger": ('  <button class="nav-hamburger" id="hamburger" aria-label="メニューを開く">\n'
                      '    <span></span><span></span><span></span>\n'
                      '  </button>'),
        "menu_open": '<div class="mobile-menu" id="mobileMenu">',
        "menu_close_btn": '  <button class="mobile-menu-close" id="mobileClose">✕</button>',
    },
    "event": {
        "nav_open": '<nav class="global-nav">',
        "hamburger": ('  <button class="global-nav-hamburger" id="globalHamburger" aria-label="メニューを開く">\n'
                      '    <span></span><span></span><span></span>\n'
                      '  </button>'),
        "menu_open": '<div class="global-mobile-menu" id="globalMobileMenu">',
        "menu_close_btn": '  <button class="global-mobile-menu-close" id="globalMobileClose">✕</button>',
    },
    "topaasia": {
        "nav_open": "<nav>",
        "hamburger": '  <div class="hamburger" id="hamburger"><span></span><span></span><span></span></div>',
        "menu_open": '<div class="mobile-menu" id="mobileMenu">',
        "menu_close_btn": '  <button class="mobile-menu-close" id="mobileClose">✕</button>',
    },
}


def build_nav(cfg, page):
    v = VARIANTS[page["variant"]]
    logo = cfg["nav"]["logo"]
    path = page["path"]

    img_attrs = ""
    if page.get("logo_priority"):
        img_attrs = ' decoding="async" fetchpriority="high"'

    parts = [
        v["nav_open"],
        f'  <a href="{rel_href(path, logo["href"])}" class="nav-logo">',
        f'    <img src="{rel_href(path, logo["image"])}" alt="{logo["alt"]}"{img_attrs}>',
        f'    <span class="nav-logo-text">{logo["text"]}</span>',
        '  </a>',
        render_desktop(cfg["nav"]["items"], path),
    ]
    if page.get("lang_toggle"):
        parts.append('  <button class="lang-toggle" id="langToggle" type="button" '
                     'aria-label="Switch language">EN</button>')
    parts.append(v["hamburger"])
    parts.append('</nav>')
    parts.append(v["menu_open"])
    parts.append(v["menu_close_btn"])
    parts.append(render_mobile(cfg["nav"]["items"], path))
    parts.append('</div>')

    return f"{NAV_START}\n" + "\n".join(parts) + f"\n{NAV_END}"


def build_footer(cfg, page):
    f = cfg["footer"]
    copy = page.get("footer_copy_prefix", "") + f["copy"]
    logo_div = f'  <div class="footer-logo">{f["logo"]}</div>'
    copy_div = f'  <div class="footer-copy">{copy}</div>'

    if page.get("footer") == "topaasia":
        tm = f["variants"]["topaasia"]
        body = ("  <div>\n"
                f'    <div class="footer-logo">{f["logo"]}</div>\n'
                f'    <div class="footer-copy">{copy}</div>\n'
                "  </div>\n"
                f'  <div class="footer-tm" data-en="{tm["tm_en"]}">\n'
                f'    {tm["tm_ja"]}\n'
                "  </div>")
    else:
        body = logo_div + "\n" + copy_div

    return f"{FOOT_START}\n<footer>\n{body}\n</footer>\n{FOOT_END}"


# ── 既存HTMLへの差し込み ────────────────────────────────────

def div_end(html, start):
    """start 位置の <div> に対応する </div> の終端インデックスを返す。"""
    depth = 0
    for m in re.finditer(r"<div\b[^>]*>|</div\s*>", html[start:]):
        depth += 1 if m.group(0).startswith("<div") else -1
        if depth == 0:
            return start + m.end()
    raise ValueError("対応する </div> が見つかりません")


class BlockNotFound(Exception):
    """差し込み先を特定できなかった。黙ってスキップせず、必ずCIを落とす。"""


def splice(html, block, start_mark, end_mark, locate, label, path):
    """マーカーがあれば置換、無ければ locate() が返す既存ブロックにマーカーを巻く。"""
    has_start, has_end = start_mark in html, end_mark in html
    if has_start != has_end:
        raise BlockNotFound(
            f"{path}: {label} のマーカーが片方だけ残っています（{start_mark} / {end_mark}）。"
            f"手で修復してください（そのまま実行するとブロックが二重挿入されます）")
    if has_start:
        pattern = re.compile(re.escape(start_mark) + r".*?" + re.escape(end_mark), re.S)
        return pattern.sub(lambda m: block, html, count=1)

    span = locate(html)
    if span is None:
        raise BlockNotFound(
            f"{path}: {label} を特定できません。マーカーも既存の <nav>／<footer> も見つかりません。"
            f"（変種の想定と構造が違う可能性。台帳の variant を確認するか、exclude に移してください）")
    start, end = span
    print(f"  🔖 {path}: {label} にマーカーを初回挿入")
    return html[:start] + block + html[end:]


def locate_nav(html):
    """最初の <nav> 〜 モバイルメニュー div の終端まで（この間が生成対象）。"""
    nav = re.search(r"<nav\b[^>]*>", html)
    menu = re.search(r'<div class="(?:global-)?mobile-menu" id="(?:global)?[Mm]obileMenu">', html)
    if not nav or not menu or menu.start() < nav.start():
        return None
    return nav.start(), div_end(html, menu.start())


def locate_footer(html):
    m = re.search(r"<footer\b[^>]*>", html)
    if not m:
        return None
    end = html.find("</footer>", m.start())
    if end == -1:
        return None
    return m.start(), end + len("</footer>")


def process(cfg, page, check_only, errors):
    path = page["path"]
    fp = os.path.join(ROOT, path)
    with open(fp, encoding="utf-8") as f:
        original = f.read()

    try:
        html = splice(original, build_nav(cfg, page), NAV_START, NAV_END,
                      locate_nav, "グローバルナビ", path)
        html = splice(html, build_footer(cfg, page), FOOT_START, FOOT_END,
                      locate_footer, "フッター", path)
    except BlockNotFound as e:
        errors.append(str(e))
        return False

    if html == original:
        return False
    if check_only:
        print(f"  ✗ {path}: 台帳と中身がずれています（update-nav.py の実行が必要）")
        return True
    with open(fp, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✏️  {path}: ナビ／フッターを更新")
    return True


# ── 台帳の検証 ──────────────────────────────────────────────

def all_html():
    """サイトを構成するHTML＝git管理下のHTML。

    「ディスク上の全HTML」ではなく git 管理下を見るのが重要:
    手元の未コミットの検証用ファイルは CI のチェックアウトに存在しないため、
    ディスク基準だと「台帳にあるのにファイルが無い」で CI だけが落ちる。
    公開されるのはコミットされたものだけなので、それを唯一の基準にする。
    """
    try:
        out = subprocess.run(["git", "-C", ROOT, "ls-files", "-z", "*.html"],
                             capture_output=True, check=True).stdout
        tracked = {f for f in out.decode("utf-8").split("\0") if f}
        if tracked:
            return {f for f in tracked
                    if not any(f.split("/")[0] == d for d in SKIP_DIRS)}
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # git が使えない環境向けのフォールバック
    found = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(".html"):
                found.append(os.path.relpath(os.path.join(dirpath, name), ROOT))
    return set(found)


def validate(cfg):
    errors = []
    pages = cfg["pages"]
    excluded = cfg["exclude"]

    listed = {p["path"] for p in pages}
    skipped = {p["path"] for p in excluded}
    on_disk = all_html()

    for p in pages:
        if p["variant"] not in VARIANTS:
            errors.append(f"{p['path']}: 未知の variant '{p['variant']}'（{'/'.join(VARIANTS)} のいずれか）")

    both = listed & skipped
    for path in sorted(both):
        errors.append(f"{path}: pages と exclude の両方に載っています")

    for path in sorted((listed | skipped) - on_disk):
        errors.append(f"{path}: 台帳にありますが、ファイルが存在しません（削除したなら台帳からも消す）")

    # ★これが「新ページがナビに置いていかれる」のを防ぐ本体
    for path in sorted(on_disk - listed - skipped):
        errors.append(
            f"{path}: 台帳に未登録です。共通ナビを載せるなら data/nav.json の pages に、"
            f"載せないなら exclude に理由付きで追加してください")

    # ナビのリンク切れ
    for item in cfg["nav"]["items"]:
        for entry in ([item] if "children" not in item else item["children"]):
            if "heading" in entry:  # 見出し行（非リンク）は検証対象外
                continue
            href = entry["href"]
            if is_external(href):
                continue
            if not os.path.exists(os.path.join(ROOT, as_page(href))):
                errors.append(f"ナビ項目「{entry['label']}」のリンク先 {href} が存在しません")

    # ロゴのリンク先・画像
    logo = cfg["nav"]["logo"]
    for key in ("href", "image"):
        if not os.path.exists(os.path.join(ROOT, as_page(logo[key]))):
            errors.append(f"ロゴの {key} 「{logo[key]}」が存在しません")

    return errors


def main():
    check_only = "--check" in sys.argv
    with open(REGISTRY, encoding="utf-8") as f:
        cfg = json.load(f)

    errors = validate(cfg)
    if errors:
        print("❌ 台帳（data/nav.json）の検証に失敗しました:\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    build_errors = []
    changed = sum(process(cfg, p, check_only, build_errors) for p in cfg["pages"])

    if build_errors:
        print("\n❌ ナビ／フッターを差し込めなかったページがあります:\n")
        for e in build_errors:
            print(f"  - {e}")
        sys.exit(1)

    if check_only and changed:
        print(f"\n❌ {changed} ページが台帳とずれています。"
              f"`python3 scripts/update-nav.py` を実行して commit してください。")
        sys.exit(1)

    print(f"完了: {changed} ページを更新（対象 {len(cfg['pages'])} ページ / "
          f"対象外 {len(cfg['exclude'])} ページ）")


if __name__ == "__main__":
    main()

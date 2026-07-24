#!/usr/bin/env python3
"""カテゴリの棚（右端中央の回遊パネル）を全対象ページに生成・同期する。

- 正は data/nav.json。各ドロップダウン（目指す未来／ソリューション／…）が1つの「棚」になり、
  そのカテゴリのルート直下内部ページすべてに、同じ棚が設置される。
- 右端中央の縦タブが常時ついてくる。ホバー可能な端末ではカーソルを合わせると全リストが展開、
  タッチ端末ではタップで開閉（二段階方式・2026-07-23 森本さん確定）。
- 各ページの <!-- SHELF START --> 〜 <!-- SHELF END --> を差し替える
  （無ければ </body> 直前に挿入）。旧 <!-- ZUKAN-SHELF START/END --> ブロックは自動撤去。
- ナビに項目を足したら update-nav.py と本スクリプトを再実行するだけで棚にも反映される。
- 実行: python3 scripts/update-shelf.py
"""

import html as html_mod
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = "<!-- SHELF START -->"
END = "<!-- SHELF END -->"
LEGACY_START = "<!-- ZUKAN-SHELF START -->"
LEGACY_END = "<!-- ZUKAN-SHELF END -->"

# カテゴリ → 棚の名前（未登録は「{ラベル}の棚」）
TITLES = {
    "世界の知恵": "図鑑の棚",
    "未来のリスク計算機": "計算機の棚",
    "世界の成功と失敗事例集": "事例集の棚",
}

# 配色テーマ。正は data/kaiyu.json の theme（paper/white/night）。台帳外ページはここで補う
THEME_OVERRIDES = {
    "rocket-map.html": "night",  # 全面が夜空のSVG（kaiyu バンド非設置のため台帳に無い）
}

THEMES = {
    "paper": {
        "tab_bg": "#26215C", "tab_fg": "#fff", "tab_border": "none",
        "panel_bg": "#fffdf8", "panel_border": "#26215C",
        "title": "#3C3489", "title_line": "#26215C",
        "heading": "#9a95c0", "link": "#333", "hover": "#3C3489",
        "active_fg": "#3C3489", "active_bg": "#f1eefa", "divider": "#eae4d3",
    },
    "white": {
        "tab_bg": "#26215C", "tab_fg": "#fff", "tab_border": "none",
        "panel_bg": "#ffffff", "panel_border": "#26215C",
        "title": "#3C3489", "title_line": "#26215C",
        "heading": "#9a95c0", "link": "#333", "hover": "#3C3489",
        "active_fg": "#3C3489", "active_bg": "#f4f3fb", "divider": "#ececf3",
    },
    "night": {
        "tab_bg": "#1f1b45", "tab_fg": "#f2d489", "tab_border": "1px solid rgba(242,212,137,0.55)",
        "panel_bg": "#211c48", "panel_border": "rgba(242,212,137,0.65)",
        "title": "#f2d489", "title_line": "rgba(242,212,137,0.65)",
        "heading": "#9a95c0", "link": "#e8e6f2", "hover": "#f2d489",
        "active_fg": "#f2d489", "active_bg": "rgba(242,212,137,0.13)", "divider": "rgba(255,255,255,0.14)",
    },
}


def load_themes():
    """data/kaiyu.json の theme を正として読み、台帳外は THEME_OVERRIDES → paper の順で補う"""
    themes = {}
    kaiyu_path = os.path.join(ROOT, "data", "kaiyu.json")
    if os.path.exists(kaiyu_path):
        for p in json.load(open(kaiyu_path, encoding="utf-8"))["pages"]:
            themes[p["path"]] = p.get("theme", "paper")
    themes.update(THEME_OVERRIDES)
    return themes


# 棚を設置しないページ（理由付き）
EXCLUDE = {
    "topaasia.html": "日英バイリンガルの製品ページ。日本語のみの棚は世界観に合わないため",
    "topaasia-data-notes.html": "同上（topaasia系）",
    "kokoro-scope.html": "感情を多面的に眺める没入型セルフケアアプリ画面（overflow:hidden 全画面）。棚は世界観と操作を妨げるため設置しない",
}


def shelf_title(label):
    return TITLES.get(label, f"{label}の棚")


def esc(s):
    return html_mod.escape(s, quote=True)


def load_categories():
    cfg = json.load(open(os.path.join(ROOT, "data", "nav.json"), encoding="utf-8"))
    return [it for it in cfg["nav"]["items"] if "children" in it]


def target_pages(children):
    """棚を設置するページ = カテゴリのルート直下の内部リンク先（サブディレクトリは対象外）"""
    pages = []
    for c in children:
        href = c.get("href", "")
        if "heading" in c or not href or href.startswith(("http", "mailto")):
            continue
        if "/" in href:  # yokai/ series/ 等は独自デザインのため対象外
            continue
        if href in EXCLUDE:
            continue
        pages.append(href)
    return pages


def build_block(label, children, current, theme):
    title = esc(shelf_title(label))
    t = THEMES.get(theme, THEMES["paper"])
    rows = []
    for c in children:
        if "heading" in c:
            rows.append(f'      <span class="shelf-heading">{esc(c["heading"])}</span>')
            continue
        href = c["href"]
        attrs = f'href="{href if href.startswith(("http", "mailto")) else "./" + href}"'
        if href.startswith("http"):
            attrs += ' target="_blank" rel="noopener"'
        if c.get("desc"):
            attrs += f' title="{esc(c["desc"])}"'
        if href == current:
            attrs += ' class="active"'
        rows.append(f'      <a {attrs}>{esc(c["label"])}</a>')
    links = "\n".join(rows)

    return f"""{START}
<style>
.shelf-tab {{ position: fixed; right: 0; top: 50%; transform: translateY(-50%); z-index: 150; writing-mode: vertical-rl; display: flex; align-items: center; gap: 0.4em; background: {t['tab_bg']}; color: {t['tab_fg']}; border: {t['tab_border']}; border-right: none; border-radius: 10px 0 0 10px; padding: 1rem 0.48rem; font-family: 'Jost', 'Zen Kaku Gothic New', sans-serif; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.18em; cursor: pointer; box-shadow: -3px 3px 12px rgba(38,33,92,0.3); }}
.shelf-backdrop {{ display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 305; background: rgba(38,33,92,0.18); }}
.shelf.open .shelf-backdrop {{ display: block; }}
.shelf-panel {{ position: fixed; right: 0.7rem; top: 50%; transform: translateY(-50%) translateX(calc(100% + 2rem)); transition: transform 0.25s; z-index: 310; width: 226px; max-height: 78vh; overflow-y: auto; background: {t['panel_bg']}; border: 2px solid {t['panel_border']}; border-radius: 12px; box-shadow: -6px 8px 22px rgba(38,33,92,0.25); padding: 0.7rem 0.75rem 0.9rem; }}
.shelf.open .shelf-panel {{ transform: translateY(-50%) translateX(0); }}
.shelf-close {{ position: absolute; top: 0.35rem; right: 0.5rem; background: none; border: none; font-size: 1.05rem; cursor: pointer; color: #888; line-height: 1; padding: 0.2rem; }}
.shelf-title {{ font-family: 'Jost', 'Zen Kaku Gothic New', sans-serif; font-weight: 700; color: {t['title']}; text-align: center; font-size: 0.95rem; letter-spacing: 0.12em; padding-bottom: 0.45rem; border-bottom: 2px solid {t['title_line']}; margin-bottom: 0.3rem; }}
.shelf-heading {{ display: block; font-family: 'Jost', 'Noto Sans JP', sans-serif; font-size: 0.66rem; font-weight: 700; letter-spacing: 0.12em; color: {t['heading']}; padding: 0.5rem 0 0.12rem; text-align: center; }}
.shelf-list a {{ display: block; font-family: 'Shippori Mincho', serif; font-size: 0.8rem; font-weight: 600; color: {t['link']}; text-decoration: none; padding: 0.42rem 0.25rem; border-bottom: 1px solid {t['divider']}; line-height: 1.45; word-break: auto-phrase; overflow-wrap: break-word; line-break: strict; text-wrap: balance; hanging-punctuation: allow-end; transition: color 0.15s, background 0.15s; }}
.shelf-list a:hover {{ color: {t['hover']}; }}
.shelf-list a.active {{ color: {t['active_fg']}; font-weight: 700; background: {t['active_bg']}; border-radius: 5px; }}
@media (hover: hover) and (pointer: fine) {{
  .shelf:hover .shelf-panel {{ transform: translateY(-50%) translateX(0); }}
  .shelf-close {{ display: none; }}
  .shelf-backdrop {{ display: none !important; }}
}}
</style>
<div class="shelf" id="siteShelf">
  <button class="shelf-tab" id="shelfTab" type="button" aria-haspopup="true" aria-expanded="false">📚 {title}</button>
  <div class="shelf-backdrop" id="shelfBackdrop"></div>
  <aside class="shelf-panel" aria-label="{title}">
    <button class="shelf-close" id="shelfClose" aria-label="閉じる">✕</button>
    <div class="shelf-title">📚 {title}</div>
    <div class="shelf-list" role="navigation">
{links}
    </div>
  </aside>
</div>
<script>
(function() {{
  var shelf = document.getElementById('siteShelf');
  var tab = document.getElementById('shelfTab');
  function setOpen(open) {{
    shelf.classList.toggle('open', open);
    tab.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open && typeof gtag === 'function') gtag('event', 'shelf_open', {{ shelf: '{title}', page: location.pathname }});
  }}
  tab.addEventListener('click', function() {{ setOpen(!shelf.classList.contains('open')); }});
  var hoverSent = false;
  shelf.addEventListener('mouseenter', function() {{
    if (!hoverSent && typeof gtag === 'function') {{ hoverSent = true; gtag('event', 'shelf_open', {{ shelf: '{title}', page: location.pathname, method: 'hover' }}); }}
  }});
  document.getElementById('shelfClose').addEventListener('click', function() {{ setOpen(false); }});
  document.getElementById('shelfBackdrop').addEventListener('click', function() {{ setOpen(false); }});
  document.addEventListener('keydown', function(e) {{ if (e.key === 'Escape' && shelf.classList.contains('open')) setOpen(false); }});
}})();
</script>
{END}"""


def splice(path, block):
    full = os.path.join(ROOT, path)
    html = open(full, encoding="utf-8").read()
    orig = html
    # 旧「図鑑の棚」ブロックの撤去
    if LEGACY_START in html:
        html = re.sub(re.escape(LEGACY_START) + r".*?" + re.escape(LEGACY_END) + r"\n*",
                      "", html, count=1, flags=re.S)
    if START in html:
        html = re.sub(re.escape(START) + r".*?" + re.escape(END),
                      lambda _: block, html, count=1, flags=re.S)
    else:
        if "</body>" not in html:
            print(f"  ⚠️  {path}: </body> が見つからずスキップ")
            return False
        html = html.replace("</body>", block + "\n\n</body>", 1)
    if html != orig:
        open(full, "w", encoding="utf-8").write(html)
        return True
    return False


def main():
    updated = 0
    seen = {}
    themes = load_themes()
    for cat in load_categories():
        for page in target_pages(cat["children"]):
            if page in seen:
                print(f"  ⚠️  {page}: 複数カテゴリに属しています（{seen[page]} と {cat['label']}）。先勝ちで {seen[page]} の棚を維持")
                continue
            seen[page] = cat["label"]
            if not os.path.exists(os.path.join(ROOT, page)):
                print(f"  ⚠️  {page}: ファイルが存在しません")
                continue
            theme = themes.get(page, "paper")
            if splice(page, build_block(cat["label"], cat["children"], page, theme)):
                updated += 1
    print(f"完了: {updated} ページ更新（対象 {len(seen)} ページ / カテゴリ {len(load_categories())}）")


if __name__ == "__main__":
    main()

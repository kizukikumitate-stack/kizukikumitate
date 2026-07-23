#!/usr/bin/env python3
"""図鑑の棚（フローティング切替ボタン）を全図鑑ページに生成・同期する。

- 正は data/nav.json の「世界の知恵」ドロップダウン（見出し・リンク・desc）。
  ナビに図鑑を足せば、update-nav.py と本スクリプトの再実行だけで棚にも反映される。
- 対象ページ: 「世界の知恵」のルート直下の内部リンク先ページ自身
  （series/ などサブディレクトリは v1 では対象外）。
- 各ページの <!-- ZUKAN-SHELF START --> 〜 <!-- ZUKAN-SHELF END --> を差し替える
  （無ければ </body> 直前に挿入）。中身は自己完結（style/script 同梱）。
- 実行: python3 scripts/update-zukan-shelf.py
"""

import html as html_mod
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = "<!-- ZUKAN-SHELF START -->"
END = "<!-- ZUKAN-SHELF END -->"
SECTION_LABEL = "世界の知恵"


def load_section():
    cfg = json.load(open(os.path.join(ROOT, "data", "nav.json"), encoding="utf-8"))
    for item in cfg["nav"]["items"]:
        if item.get("label") == SECTION_LABEL and "children" in item:
            return item["children"]
    sys.exit(f"nav.json に「{SECTION_LABEL}」のドロップダウンが見つかりません")


def target_pages(children):
    pages = []
    for c in children:
        href = c.get("href", "")
        if "heading" in c or href.startswith(("http", "mailto")):
            continue
        if "/" in href:  # series/ 等のサブディレクトリは対象外（相対パスが変わるため）
            continue
        pages.append(href)
    return pages


def build_block(children, current):
    rows = []
    for c in children:
        if "heading" in c:
            rows.append(f'    <span class="zs-heading">{c["heading"]}</span>')
            continue
        href = c["href"]
        title = f' title="{html_mod.escape(c["desc"], quote=True)}"' if c.get("desc") else ""
        cls = ' class="active"' if href == current else ""
        # 棚を置くのはルート直下ページのみなので相対パスは ./ 固定でよい
        prefix = "" if href.startswith("http") else "./"
        rows.append(f'    <a href="{prefix}{href}"{title}{cls}>{c["label"]}</a>')
    links = "\n".join(rows)

    return f"""{START}
<style>
.zukan-shelf-fab {{ position: fixed; right: 1rem; bottom: 1.2rem; z-index: 150; display: flex; align-items: center; gap: 0.45em; background: #26215C; color: #fff; border: none; border-radius: 999px; padding: 0.68rem 1.15rem; font-family: 'Jost', 'Zen Kaku Gothic New', sans-serif; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.08em; box-shadow: 0 4px 14px rgba(38,33,92,0.35); cursor: pointer; transition: transform 0.15s, box-shadow 0.15s; }}
.zukan-shelf-fab:hover {{ transform: translateY(-2px); box-shadow: 0 6px 18px rgba(38,33,92,0.45); }}
.zukan-shelf-overlay {{ display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 300; background: rgba(255,255,255,0.97); backdrop-filter: blur(12px); overflow-y: auto; padding: 4.2rem 1.5rem 3rem; }}
.zukan-shelf-overlay.open {{ display: block; }}
.zs-inner {{ max-width: 34rem; margin: 0 auto; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 0.5rem; }}
.zs-title {{ grid-column: 1 / -1; text-align: center; font-family: 'Jost', 'Zen Kaku Gothic New', sans-serif; font-size: 1.15rem; font-weight: 700; letter-spacing: 0.1em; color: #3C3489; padding-bottom: 0.6rem; }}
.zs-heading {{ grid-column: 1 / -1; display: block; font-family: 'Jost', 'Noto Sans JP', sans-serif; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em; color: #9a95c0; padding: 0.75rem 0 0.15rem; text-align: center; }}
.zs-heading + .zs-heading, .zs-heading:not(:first-of-type) {{ border-top: 1px solid #ececf3; margin-top: 0.35rem; padding-top: 0.65rem; }}
.zs-inner a {{ font-family: 'Shippori Mincho', serif; font-size: 0.88rem; font-weight: 600; color: #333; text-decoration: none; padding: 0.45rem 0.1rem; text-align: center; line-height: 1.5; word-break: auto-phrase; overflow-wrap: break-word; line-break: strict; text-wrap: balance; hanging-punctuation: allow-end; transition: color 0.15s; }}
.zs-inner a:hover {{ color: #3C3489; }}
.zs-inner a.active {{ color: #3C3489; font-weight: 700; }}
.zukan-shelf-close {{ position: absolute; top: 1.2rem; right: 1.5rem; background: none; border: none; font-size: 1.6rem; cursor: pointer; color: #666; line-height: 1; padding: 0.3rem; }}
</style>
<button class="zukan-shelf-fab" id="zukanShelfFab" type="button" aria-haspopup="true" aria-expanded="false">📚 図鑑の棚</button>
<div class="zukan-shelf-overlay" id="zukanShelfOverlay" role="dialog" aria-label="図鑑の棚">
  <button class="zukan-shelf-close" id="zukanShelfClose" aria-label="閉じる">✕</button>
  <div class="zs-inner">
    <span class="zs-title">📚 図鑑の棚</span>
{links}
  </div>
</div>
<script>
(function() {{
  var fab = document.getElementById('zukanShelfFab');
  var ov = document.getElementById('zukanShelfOverlay');
  var close = document.getElementById('zukanShelfClose');
  function setOpen(open) {{
    ov.classList.toggle('open', open);
    fab.setAttribute('aria-expanded', open ? 'true' : 'false');
    document.body.style.overflow = open ? 'hidden' : '';
    if (open && typeof gtag === 'function') gtag('event', 'zukan_shelf_open', {{ page: location.pathname }});
  }}
  fab.addEventListener('click', function() {{ setOpen(!ov.classList.contains('open')); }});
  close.addEventListener('click', function() {{ setOpen(false); }});
  ov.addEventListener('click', function(e) {{ if (e.target === ov) setOpen(false); }});
  document.addEventListener('keydown', function(e) {{ if (e.key === 'Escape' && ov.classList.contains('open')) setOpen(false); }});
}})();
</script>
{END}"""


def splice(path, block):
    full = os.path.join(ROOT, path)
    html = open(full, encoding="utf-8").read()
    if START in html:
        pattern = re.escape(START) + r".*?" + re.escape(END)
        new_html = re.sub(pattern, lambda _: block, html, count=1, flags=re.S)
        changed = new_html != html
    else:
        anchor = "</body>"
        if anchor not in html:
            print(f"  ⚠️  {path}: </body> が見つからずスキップ")
            return False
        new_html = html.replace(anchor, block + "\n\n" + anchor, 1)
        changed = True
    if changed:
        open(full, "w", encoding="utf-8").write(new_html)
    return changed


def main():
    children = load_section()
    pages = target_pages(children)
    updated = 0
    for page in pages:
        if not os.path.exists(os.path.join(ROOT, page)):
            print(f"  ⚠️  {page}: ファイルが存在しません")
            continue
        if splice(page, build_block(children, page)):
            print(f"  ✏️  {page}")
            updated += 1
    print(f"完了: {updated} ページに図鑑の棚を反映（対象 {len(pages)} ページ）")


if __name__ == "__main__":
    main()

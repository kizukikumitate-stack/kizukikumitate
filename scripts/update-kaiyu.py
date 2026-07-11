#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
サイト内回遊バンド（次はこちらへ）の自動生成スクリプト。

data/kaiyu.json（台帳）を読み、band=true の各ページのフッター直前にある
<!-- KAIYU START --> 〜 <!-- KAIYU END --> の間を再生成する。
マーカーがまだ無いページには <footer> の直前に自動挿入する（初回導入も新ページ追加もこれだけ）。

構成: 手動キュレーション2枠（台帳の next）＋ 新着1枠（added が最新のページを自動選出）。
新着枠には、追加から45日以内なら「新着」バッジを付ける。

冪等: 出力が現状と同一なら書き換えない（GitHub Actions で差分が無ければ commit されない）。

使い方:
  python3 scripts/update-kaiyu.py           # 生成・更新
  KAIYU_NOW=2026-07-11 python3 scripts/... # テスト用に日付を注入
"""
import json
import os
import posixpath
import re
import sys
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "data", "kaiyu.json")
MARK_START = "<!-- KAIYU START -->"
MARK_END = "<!-- KAIYU END -->"
NEW_BADGE_DAYS = 45

# ── ブロックの自己完結CSS（kaiyu- プレフィックスで既存CSSと衝突しない） ──
STYLE = """<style>
.kaiyu{padding:3.4rem 2rem 3.8rem}
.kaiyu-inner{max-width:960px;margin:0 auto}
.kaiyu-head{text-align:center;margin-bottom:1.9rem}
.kaiyu-eyebrow{display:block;font-family:'Jost','Zen Kaku Gothic New',sans-serif;font-size:.7rem;letter-spacing:.32em;text-transform:uppercase;margin-bottom:.7rem}
.kaiyu-title{display:block;font-family:'Shippori Mincho',serif;font-weight:700;font-size:1.15rem;letter-spacing:.08em}
.kaiyu-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}
@media(max-width:860px){.kaiyu-grid{grid-template-columns:minmax(0,1fr)}}
.kaiyu-card{position:relative;display:flex;flex-direction:column;gap:.45rem;text-decoration:none;border-radius:12px;padding:1.3rem 1.2rem 1.4rem;border:1px solid transparent;transition:transform .22s ease,box-shadow .22s ease}
.kaiyu-card:hover{transform:translateY(-3px)}
.kaiyu-tag{font-family:'Jost','Zen Kaku Gothic New',sans-serif;font-size:.66rem;letter-spacing:.22em;text-transform:uppercase}
.kaiyu-name{font-family:'Shippori Mincho',serif;font-weight:700;font-size:.98rem;letter-spacing:.04em;line-height:1.6}
.kaiyu-desc{font-size:.78rem;line-height:1.9;font-weight:300}
.kaiyu-arw{margin-top:auto;align-self:flex-end;font-family:'Jost',sans-serif;font-size:.9rem}
.kaiyu-badge{position:absolute;top:-.55em;right:.9rem;font-family:'Jost','Zen Kaku Gothic New',sans-serif;font-size:.62rem;letter-spacing:.18em;padding:.18em .7em;border-radius:999px}
.kaiyu[data-kaiyu-theme=white]{background:#f4f5f9}
.kaiyu[data-kaiyu-theme=white] .kaiyu-eyebrow{color:#3C3489}
.kaiyu[data-kaiyu-theme=white] .kaiyu-title{color:#26215C}
.kaiyu[data-kaiyu-theme=white] .kaiyu-card{background:#fff;border-color:#e3e2ef;box-shadow:0 2px 10px rgba(38,33,92,.05)}
.kaiyu[data-kaiyu-theme=white] .kaiyu-card:hover{box-shadow:0 12px 26px rgba(38,33,92,.12)}
.kaiyu[data-kaiyu-theme=white] .kaiyu-tag{color:#1a5fad}
.kaiyu[data-kaiyu-theme=white] .kaiyu-name{color:#26215C}
.kaiyu[data-kaiyu-theme=white] .kaiyu-desc{color:#5a6a7a}
.kaiyu[data-kaiyu-theme=white] .kaiyu-arw{color:#3C3489}
.kaiyu[data-kaiyu-theme=white] .kaiyu-badge{background:#d85a30;color:#fff}
.kaiyu[data-kaiyu-theme=paper]{background:rgba(60,52,20,.045)}
.kaiyu[data-kaiyu-theme=paper] .kaiyu-eyebrow{color:#b8862d}
.kaiyu[data-kaiyu-theme=paper] .kaiyu-title{color:#3a3428}
.kaiyu[data-kaiyu-theme=paper] .kaiyu-card{background:#fffdf7;border-color:#ddd6c4;box-shadow:0 2px 10px rgba(90,75,30,.06)}
.kaiyu[data-kaiyu-theme=paper] .kaiyu-card:hover{box-shadow:0 12px 26px rgba(90,75,30,.13)}
.kaiyu[data-kaiyu-theme=paper] .kaiyu-tag{color:#b8862d}
.kaiyu[data-kaiyu-theme=paper] .kaiyu-name{color:#3a3428}
.kaiyu[data-kaiyu-theme=paper] .kaiyu-desc{color:#6d6455}
.kaiyu[data-kaiyu-theme=paper] .kaiyu-arw{color:#b8862d}
.kaiyu[data-kaiyu-theme=paper] .kaiyu-badge{background:#0f6e56;color:#fff}
.kaiyu[data-kaiyu-theme=night]{background:rgba(255,255,255,.03)}
.kaiyu[data-kaiyu-theme=night] .kaiyu-eyebrow{color:#c9a84c}
.kaiyu[data-kaiyu-theme=night] .kaiyu-title{color:#f2ead8}
.kaiyu[data-kaiyu-theme=night] .kaiyu-card{background:rgba(255,255,255,.045);border-color:rgba(201,168,76,.28)}
.kaiyu[data-kaiyu-theme=night] .kaiyu-card:hover{box-shadow:0 12px 26px rgba(0,0,0,.4);border-color:rgba(201,168,76,.55)}
.kaiyu[data-kaiyu-theme=night] .kaiyu-tag{color:#c9a84c}
.kaiyu[data-kaiyu-theme=night] .kaiyu-name{color:#f2ead8}
.kaiyu[data-kaiyu-theme=night] .kaiyu-desc{color:rgba(242,234,216,.66)}
.kaiyu[data-kaiyu-theme=night] .kaiyu-arw{color:#c9a84c}
.kaiyu[data-kaiyu-theme=night] .kaiyu-badge{background:#c9a84c;color:#1a1626}
</style>"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def today():
    env = os.environ.get("KAIYU_NOW")
    if env:
        return datetime.strptime(env, "%Y-%m-%d").date()
    return date.today()


def rel_href(from_path, to_path):
    """ページ from_path から to_path への相対URL（リポジトリルート基準のパス同士）"""
    rel = posixpath.relpath(to_path, posixpath.dirname(from_path))
    if not rel.startswith("."):
        rel = "./" + rel
    return rel


def pick_cards(page, pages_by_id, all_pages):
    """キュレーション2枠＋新着1枠を選ぶ。戻り値: [(entry, is_new_slot), ...]"""
    chosen = []
    for nid in page.get("next", [])[:2]:
        e = pages_by_id.get(nid)
        if e and e["id"] != page["id"]:
            chosen.append(e)
    # キュレーションが2枠に満たなければ同カテゴリの新しい順で補完
    if len(chosen) < 2:
        same_cat = [p for p in all_pages
                    if p["category"] == page["category"]
                    and p["id"] != page["id"]
                    and p not in chosen]
        same_cat.sort(key=lambda p: p["added"], reverse=True)
        chosen.extend(same_cat[: 2 - len(chosen)])
    # 新着枠: 全体で最新（自分と既出を除く）
    rest = [p for p in all_pages if p["id"] != page["id"] and p not in chosen]
    rest.sort(key=lambda p: p["added"], reverse=True)
    cards = [(e, False) for e in chosen]
    if rest:
        cards.append((rest[0], True))
    return cards[:3]


def build_block(page, pages_by_id, all_pages):
    cards_html = []
    for entry, is_new_slot in pick_cards(page, pages_by_id, all_pages):
        href = rel_href(page["path"], entry["path"])
        badge = ""
        if is_new_slot:
            added = datetime.strptime(entry["added"], "%Y-%m-%d").date()
            if (today() - added).days <= NEW_BADGE_DAYS:
                badge = '<span class="kaiyu-badge">新着</span>'
        cards_html.append(
            f'    <a class="kaiyu-card" href="{href}">{badge}'
            f'<span class="kaiyu-tag">{esc(entry["tag"])}</span>'
            f'<span class="kaiyu-name">{esc(entry["title"])}</span>'
            f'<span class="kaiyu-desc">{esc(entry["desc"])}</span>'
            f'<span class="kaiyu-arw">→</span></a>'
        )
    cards = "\n".join(cards_html)
    return f"""{MARK_START}
<aside class="kaiyu" data-kaiyu-theme="{page['theme']}" aria-label="次のおすすめページ">
{STYLE}
<div class="kaiyu-inner">
  <div class="kaiyu-head">
    <span class="kaiyu-eyebrow">Keep Exploring</span>
    <span class="kaiyu-title">次は、こちらへ。</span>
  </div>
  <div class="kaiyu-grid">
{cards}
  </div>
</div>
</aside>
{MARK_END}"""


def process_file(page, pages_by_id, all_pages):
    fp = os.path.join(ROOT, page["path"])
    if not os.path.exists(fp):
        print(f"  ⚠️ {page['path']}: ファイルが見つからないためスキップ")
        return False
    with open(fp, encoding="utf-8") as f:
        html = f.read()
    block = build_block(page, pages_by_id, all_pages)

    if MARK_START in html and MARK_END in html:
        pattern = re.compile(re.escape(MARK_START) + r".*?" + re.escape(MARK_END), re.S)
        new_html = pattern.sub(lambda m: block, html, count=1)
    else:
        # 初回: 最後の <footer の直前に挿入
        idx = html.rfind("<footer")
        if idx == -1:
            idx = html.rfind("</body>")
        if idx == -1:
            print(f"  ⚠️ {page['path']}: <footer> も </body> も無いためスキップ")
            return False
        new_html = html[:idx] + block + "\n\n" + html[idx:]

    if new_html != html:
        with open(fp, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"  ✏️  {page['path']}: 回遊バンドを更新")
        return True
    return False


def main():
    with open(REGISTRY, encoding="utf-8") as f:
        registry = json.load(f)
    all_pages = registry["pages"]
    pages_by_id = {p["id"]: p for p in all_pages}

    # 台帳の整合性チェック
    ok = True
    for p in all_pages:
        for nid in p.get("next", []):
            if nid not in pages_by_id:
                print(f"❌ {p['id']}: next の '{nid}' が台帳に存在しません")
                ok = False
    if not ok:
        sys.exit(1)

    changed = 0
    for p in all_pages:
        if p.get("band"):
            if process_file(p, pages_by_id, all_pages):
                changed += 1
    print(f"完了: {changed} ページを更新（対象 {sum(1 for p in all_pages if p.get('band'))} ページ）")


if __name__ == "__main__":
    main()

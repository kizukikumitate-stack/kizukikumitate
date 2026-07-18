#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ホモ・サピエンスの知恵図鑑（chie-zukan.html）を data/chie-zukan.json から生成する。

『ホモ・サピエンスの苦手図鑑』(nigate-zukan.html) と対になる姉妹図鑑。
苦手＝古い脳のつまずき に対して、こちらは「人がもともと持ち、育てられる力」を収蔵する。

ナビ／回遊／フッターの各マーカー間は nigate-zukan.html から流用し、
公開前に scripts/update-nav.py・scripts/update-kaiyu.py が現行台帳へ再生成する。

使い方:  python3 scripts/gen-chie-zukan.py
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "chie-zukan.json")
NIGATE = os.path.join(ROOT, "nigate-zukan.html")
OUT = os.path.join(ROOT, "chie-zukan.html")

# ── カテゴリ（3系統） ───────────────────────────────────────
CATS = {
    1: {"key": "kojin", "glyph": "個", "tab": "自分を動かす力",
        "badge": "個の力", "mcls": "m1"},
    2: {"key": "shu",   "glyph": "衆", "tab": "みんなで賢くなる",
        "badge": "衆の知", "mcls": "m2"},
    3: {"key": "chi",   "glyph": "智", "tab": "しなやかに考える",
        "badge": "智の光", "mcls": "m3"},
}

# ── 各概念の紋（emblem）に焼き入れる一字 ──────────────────────
GLYPH = {
    "自己効力感": "自", "努力効力感": "努", "組織効力感": "組", "学習性無力感": "無",
    "学習性楽観": "楽", "統制の所在": "制", "グリット": "粘", "成長マインドセット": "伸",
    "希望理論": "望", "心理的資本": "資", "自己決定理論": "決", "エージェンシー": "主", "フロー": "没",
    "心理的安全性": "安", "集合知": "衆", "集団的知性のc因子": "協", "集団思考": "同",
    "社会的手抜き": "怠", "傍観者効果": "傍", "トランザクティブ・メモリー": "憶", "分散認知": "散",
    "センスメイキング": "意", "学習する組織": "学", "ダブルループ学習": "環", "アンラーニング": "解",
    "SECIモデル(暗黙知と形式知)": "暗", "組織市民行動": "徳", "フォロワーシップ": "支",
    "シェアド・リーダーシップ": "共", "ソーシャル・キャピタル": "縁", "越境学習": "越",
    "ティール組織": "進", "心理的オーナーシップ": "当",
    "多重知能理論": "多", "EQ(感情知能)": "情", "CQ(文化的知性)": "異",
    "流動性知能と結晶性知能": "晶", "メタ認知": "観", "実践知": "践", "知恵(ウィズダム)": "慧",
    "知的謙虚さ": "謙", "ダニング=クルーガー効果": "過", "システム1とシステム2": "速",
    "批判的思考": "吟", "システム思考": "系", "ネガティブ・ケイパビリティ": "耐",
    "成人発達理論": "熟", "レジリエンス": "復", "セルフ・コンパッション": "慈",
    "ウェルビーイングとPERMA": "幸",
}


def esc(s):
    return html.escape(s or "", quote=False)


def marker_block(src, start, end):
    """nigate から <!-- X START -->〜<!-- X END --> を丸ごと取り出す（マーカー含む）。"""
    m = re.search(re.escape(start) + r".*?" + re.escape(end), src, re.S)
    if not m:
        raise SystemExit(f"marker not found: {start}")
    return m.group(0)


def build_card(idx, e):
    cat = CATS[e["cat"]]
    no = f"No.{idx:03d}"
    glyph = GLYPH.get(e["term"], e["term"][:1])
    term = esc(e["term"])
    yomi = esc(e.get("yomi", ""))
    en = esc(e.get("en", ""))
    latin = " ｜ ".join(x for x in [yomi, en] if x)
    parts = [
        f'    <article class="card" data-cat="{cat["key"]}">',
        f'      <figure class="card-fig"><span class="mon {cat["mcls"]}" aria-hidden="true">{esc(glyph)}</span></figure>',
        '      <div class="card-head">',
        '        <div>',
        f'          <span class="card-no">{no}</span>',
        f'          <h3>{term}</h3>',
        f'          <p class="latin">{latin}</p>',
        '        </div>',
        f'        <span class="badge {cat["key"]}">{cat["badge"]}</span>',
        '      </div>',
        '      <div class="card-body">',
        '        <dl>',
        f'          <div><dt>ひとことで</dt><dd>{esc(e["def"])}</dd></div>',
        f'          <div><dt>どういう力か</dt><dd>{esc(e["text"])}</dd></div>',
    ]
    if e.get("ex"):
        parts.append(f'          <div><dt>たとえば</dt><dd>{esc(e["ex"])}</dd></div>')
    if e.get("person"):
        parts.append(f'          <div><dt>提唱・研究</dt><dd>{esc(e["person"])}</dd></div>')
    parts.append('        </dl>')
    if e.get("q"):
        parts.append(f'        <p class="card-q"><span class="card-q-label">問い</span>{esc(e["q"])}</p>')
    parts += ['      </div>', '    </article>']
    return "\n".join(parts)


def main():
    data = json.load(open(DATA, encoding="utf-8"))
    nig = open(NIGATE, encoding="utf-8").read()
    nav = marker_block(nig, "<!-- NAV START -->", "<!-- NAV END -->")
    kaiyu = marker_block(nig, "<!-- KAIYU START -->", "<!-- KAIYU END -->")
    footer = marker_block(nig, "<!-- FOOTER START -->", "<!-- FOOTER END -->")

    cards = "\n\n".join(build_card(i + 1, e) for i, e in enumerate(data))
    counts = {c: sum(1 for e in data if e["cat"] == c) for c in (1, 2, 3)}

    doc = TEMPLATE.format(nav=nav, kaiyu=kaiyu, footer=footer, cards=cards,
                          n1=counts[1], n2=counts[2], n3=counts[3], total=len(data))
    open(OUT, "w", encoding="utf-8").write(doc)
    print(f"wrote {OUT}  ({len(data)} cards: 個{counts[1]}/衆{counts[2]}/智{counts[3]})")


TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ホモ・サピエンスの知恵図鑑|人がもともと持ち、育てられる力の図鑑|きづきくみたて工房</title>
<meta name="description" content="効力感、希望、心理的安全性、集合知、メタ認知、知恵。心理学と組織論が見つけてきた「人がもともと持ち、育てられる力」全50種を、たとえ話と問いつきで収蔵。『苦手図鑑』と対になる姉妹図鑑。">
<link rel="canonical" href="https://kizukikumitate.com/chie-zukan.html">
<meta property="og:title" content="ホモ・サピエンスの知恵図鑑|きづきくみたて工房">
<meta property="og:description" content="人がもともと持ち、育てられる力を50種収蔵。効力感・心理的安全性・メタ認知・知恵……『苦手図鑑』と対になる、伸びる力の図鑑。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://kizukikumitate.com/chie-zukan.html">
<meta property="og:image" content="https://kizukikumitate.com/ogp.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="ホモ・サピエンスの知恵図鑑｜きづきくみたて工房">
<meta name="twitter:description" content="人がもともと持ち、育てられる力を50種収蔵。『苦手図鑑』と対になる、伸びる力の図鑑。">
<meta name="twitter:image" content="https://kizukikumitate.com/ogp.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500&family=Noto+Serif+JP:wght@300;400;600&family=Shippori+Mincho:wght@400;600;800&family=Shippori+Mincho+B1:wght@500;700;800&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{{
  --washi:#F4F2EA;
  --washi-deep:#EBE8DC;
  --sumi:#26313A;
  --sumi-soft:#4E5A63;
  --accent:#1E4466;        /* 藍:知の主色。ヒーロー・章見出し・焼印 */
  --accent-soft:#DCE5EC;
  --c1:#96502F;            /* 個:自分を動かす力（弁柄） */
  --c2:#4E7A4E;            /* 衆:みんなで賢くなる力（萌葱） */
  --c3:#544A79;            /* 智:しなやかに考える力（紫紺） */
  --line:#C9C4B4;
  --charcoal:#1e1e1e;
  --forest:#1a5fad;
  --f-display:'Shippori Mincho B1','Hiragino Mincho ProN',serif;
  --f-body:'Zen Kaku Gothic New','Hiragino Kaku Gothic ProN',sans-serif;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{
  font-family:var(--f-body);
  background:var(--washi);
  color:var(--sumi);
  line-height:1.95;
  font-size:17px;
  hanging-punctuation:allow-end;
  background-image:radial-gradient(rgba(30,68,102,0.035) 1px, transparent 1px);
  background-size:22px 22px;
  overflow-x:hidden;
}}
img{{max-width:100%}}
a{{color:var(--accent)}}
p, dd, li{{word-break:keep-all;overflow-wrap:break-word}}

/* ===== 共通グローバルナビ（全ページ共通・sticky） ===== */
nav {{
  position: sticky; top: 0; z-index: 100;
  padding: 0.7rem 2rem; display: flex; align-items: center;
  background: rgba(255,255,255,0.97); backdrop-filter: blur(12px);
  border-bottom: 3px solid #3C3489;
}}
.nav-logo {{ display: flex; align-items: center; gap: 0.7rem; text-decoration: none; flex-shrink: 0; margin-right: 4rem; }}
.nav-logo img {{ height: 36px; width: auto; object-fit: contain; }}
.nav-logo-text {{ font-family: 'Shippori Mincho', serif; font-size: 1.1rem; font-weight: 800; white-space: nowrap; color: var(--forest); letter-spacing: 0.06em; }}
.nav-links {{ display: flex; gap: 1.2rem; list-style: none; align-items: center; margin-left: auto; flex-wrap: wrap; }}
.nav-links a {{ font-family: 'Jost', 'Noto Serif JP', sans-serif; font-size: 0.82rem; color: var(--charcoal); text-decoration: none; letter-spacing: 0.04em; }}
.nav-links a:hover, .nav-links a.active {{ color: var(--forest); }}
.nav-dropdown {{ position: relative; display: flex; align-items: center; }}
.nav-dropdown-toggle {{
  font-family: 'Jost', 'Noto Serif JP', sans-serif; font-size: 0.82rem; font-weight: 400;
  letter-spacing: 0.04em; color: var(--charcoal);
  background: none; border: none; cursor: pointer; padding: 0.4rem 0;
  display: inline-flex; align-items: center; gap: 0.35em; white-space: nowrap; transition: color 0.3s;
}}
.nav-caret {{ font-size: 0.6em; transition: transform 0.25s; }}
.nav-dropdown:hover .nav-dropdown-toggle,
.nav-dropdown:focus-within .nav-dropdown-toggle {{ color: var(--forest); }}
.nav-dropdown:hover .nav-caret,
.nav-dropdown:focus-within .nav-caret {{ transform: rotate(180deg); }}
.nav-dropdown-menu {{
  position: absolute; top: 100%; left: 50%; transform: translateX(-50%) translateY(8px);
  min-width: 210px; background: #fff; border: 1px solid #eee;
  box-shadow: 0 14px 34px rgba(38,33,92,0.14); border-radius: 12px;
  padding: 0.5rem 0; display: flex; flex-direction: column;
  opacity: 0; visibility: hidden; transition: opacity 0.2s, transform 0.2s; z-index: 300;
}}
.nav-dropdown-menu::before {{ content: ''; position: absolute; top: -10px; left: 0; right: 0; height: 10px; }}
.nav-dropdown:hover .nav-dropdown-menu,
.nav-dropdown:focus-within .nav-dropdown-menu {{ opacity: 1; visibility: visible; transform: translateX(-50%) translateY(4px); }}
.nav-dropdown-menu a {{
  font-family: 'Noto Sans JP', sans-serif; font-size: 0.84rem; font-weight: 500;
  letter-spacing: 0.02em; text-transform: none; color: #333; text-decoration: none;
  padding: 0.6rem 1.5rem; white-space: nowrap; transition: background 0.15s, color 0.15s;
}}
.nav-dropdown-menu a:hover, .nav-dropdown-menu a.active {{ background: #f4f3fb; color: var(--forest); }}
.nav-dropdown:last-child .nav-dropdown-menu {{ left: auto; right: 0; transform: translateX(0) translateY(8px); }}
.nav-dropdown:last-child:hover .nav-dropdown-menu,
.nav-dropdown:last-child:focus-within .nav-dropdown-menu {{ transform: translateX(0) translateY(4px); }}
.nav-hamburger {{ display: none; margin-left: auto; background: none; border: 0; cursor: pointer; padding: 8px; }}
.nav-hamburger span {{ display: block; width: 24px; height: 2px; background: var(--charcoal); margin: 5px 0; transition: 0.3s; }}
.mobile-menu {{ display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 199; background: rgba(255,255,255,0.98); backdrop-filter: blur(12px); flex-direction: column; justify-content: flex-start; overflow-y: auto; align-items: center; gap: 0; padding: 5rem 1.5rem 3rem; }}
.mobile-menu.open {{ display: flex; }}
.mobile-menu a {{ font-family: 'Shippori Mincho', serif; font-size: 1.12rem; font-weight: 600; color: #222; text-decoration: none; padding: 0.75rem 0; width: 100%; text-align: center; border-bottom: 1px solid #e8e8e8; transition: color 0.15s; }}
.mobile-menu a:first-child {{ border-top: 1px solid #e8e8e8; }}
.mobile-menu a:hover, .mobile-menu a.active {{ color: #3C3489; }}
.mobile-menu-close {{ position: absolute; top: 1.2rem; right: 1.5rem; background: none; border: none; font-size: 1.6rem; cursor: pointer; color: #666; line-height: 1; padding: 0.3rem; }}
.mobile-acc {{ width: 100%; border-bottom: 1px solid #e8e8e8; }}
.mobile-acc-toggle {{ width: 100%; display: flex; justify-content: center; align-items: center; gap: 0.5em; background: none; border: none; cursor: pointer; font-family: 'Jost', 'Zen Kaku Gothic New', sans-serif; font-size: 1.15rem; font-weight: 700; letter-spacing: 0.1em; color: #3C3489; padding: 1.15rem 0; }}
.mobile-acc-caret {{ font-size: 0.75em; color: #b0a8d8; transition: transform 0.25s; }}
.mobile-acc.open .mobile-acc-caret {{ transform: rotate(180deg); }}
.mobile-acc-panel {{ display: none; flex-direction: column; align-items: center; padding-bottom: 0.7rem; }}
.mobile-acc.open .mobile-acc-panel {{ display: flex; }}
.mobile-acc-panel a {{ font-family: 'Shippori Mincho', serif; font-size: 1.02rem; font-weight: 600; color: #333; text-decoration: none; padding: 0.6rem 0; width: 100%; text-align: center; border: none; transition: color 0.15s; }}
.mobile-acc-panel a:hover, .mobile-acc-panel a.active {{ color: #3C3489; }}
@media (max-width: 1250px) {{
  .nav-links {{ display: none; }}
  .nav-hamburger {{ display: block; }}
  .nav-logo {{ margin-right: 0; }}
}}

/* ===== ヒーロー ===== */
.hero{{max-width:1080px;margin:0 auto;padding:64px 24px 56px}}
.hero-title{{
  font-family:var(--f-display);font-weight:800;
  font-size:clamp(34px,6vw,68px);
  letter-spacing:.1em;line-height:1.3;
  color:var(--accent);
  border-bottom:3px solid var(--accent);
  padding-bottom:14px;margin-bottom:36px;
}}
.hero-title small{{display:block;font-size:15px;font-weight:500;letter-spacing:.4em;color:var(--sumi-soft);margin-top:8px}}
.hero-body h1{{font-family:var(--f-display);font-size:clamp(20px,3vw,26px);font-weight:700;line-height:1.7;letter-spacing:.04em;margin-bottom:20px}}
.hero-body h1 em{{font-style:normal;background:linear-gradient(transparent 62%, var(--accent-soft) 62%)}}
.hero-body p{{max-width:34em;color:var(--sumi-soft);margin-bottom:14px}}
.hero-note{{display:inline-block;margin-top:10px;padding:10px 16px;border:1px solid var(--line);background:#fff;font-size:15px;letter-spacing:.05em}}
.hero-note b{{color:var(--accent)}}
.pair-link{{display:inline-block;margin-top:18px;font-size:14.5px;letter-spacing:.03em}}

/* ===== 章見出し ===== */
.section{{max-width:1080px;margin:0 auto;padding:64px 24px}}
.sec-head{{display:flex;align-items:baseline;gap:16px;margin-bottom:8px}}
.sec-no{{font-family:var(--f-display);font-size:14px;letter-spacing:.3em;color:var(--accent);border:1px solid var(--accent);padding:2px 10px;white-space:nowrap}}
.sec-head h2{{font-family:var(--f-display);font-size:clamp(22px,3vw,30px);font-weight:700;letter-spacing:.06em}}
.sec-lead{{color:var(--sumi-soft);max-width:42em;margin-bottom:36px}}

/* ===== 前提の三箱 ===== */
.premise-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}}
.premise{{background:#fff;border:1px solid var(--line);padding:26px 24px;position:relative}}
.premise::before{{content:attr(data-mark);position:absolute;top:-15px;left:18px;font-family:var(--f-display);font-size:14px;font-weight:700;background:var(--sumi);color:var(--washi);padding:3px 12px;letter-spacing:.15em}}
.premise h3{{font-family:var(--f-display);font-size:19px;margin:8px 0 8px;letter-spacing:.04em}}
.premise p{{font-size:15.5px;color:var(--sumi-soft);line-height:1.9}}

/* ===== 三系統（焼印） ===== */
.stamp-legend{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin-top:8px}}
.legend-item{{background:#fff;border:1px solid var(--line);padding:24px 18px 20px;text-align:center;position:relative}}
.stamp{{
  width:92px;height:92px;border-radius:50%;
  display:inline-flex;align-items:center;justify-content:center;
  font-family:var(--f-display);font-weight:800;font-size:42px;
  transform:rotate(-5deg);letter-spacing:0;position:relative;margin-bottom:16px;
}}
.stamp::after{{content:"";position:absolute;inset:5px;border-radius:50%;border:1px solid currentColor;opacity:.4}}
.stamp.s1{{border:4px solid var(--c1);color:var(--c1);background:radial-gradient(circle at 32% 28%, rgba(150,80,47,.14), transparent 62%);box-shadow:0 0 0 2px rgba(150,80,47,.14) inset, 0 3px 10px rgba(150,80,47,.12)}}
.stamp.s2{{border:4px solid var(--c2);color:var(--c2);background:radial-gradient(circle at 32% 28%, rgba(78,122,78,.16), transparent 62%);box-shadow:0 0 0 2px rgba(78,122,78,.14) inset, 0 3px 10px rgba(78,122,78,.12)}}
.stamp.s3{{border:4px solid var(--c3);color:var(--c3);background:radial-gradient(circle at 32% 28%, rgba(84,74,121,.16), transparent 62%);box-shadow:0 0 0 2px rgba(84,74,121,.14) inset, 0 3px 10px rgba(84,74,121,.12)}}
.legend-item h3{{font-size:17px;font-family:var(--f-display);letter-spacing:.08em;margin-bottom:6px}}
.legend-item .count{{font-size:12.5px;letter-spacing:.18em;color:var(--sumi-soft);margin-bottom:8px}}
.legend-item p{{font-size:14.5px;color:var(--sumi-soft);line-height:1.85;text-align:left}}

/* ===== フィルタタブ ===== */
.tabs{{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 32px}}
.tab{{font-family:var(--f-body);font-size:15.5px;letter-spacing:.08em;padding:8px 20px;border:1px solid var(--sumi);background:transparent;color:var(--sumi);cursor:pointer;transition:all .18s ease}}
.tab:hover{{background:var(--washi-deep)}}
.tab.active{{background:var(--sumi);color:var(--washi)}}
.tab:focus-visible{{outline:3px solid var(--accent);outline-offset:2px}}

/* ===== 標本カード ===== */
.cards{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}}
.card{{background:#fff;border:1px solid var(--line);display:flex;flex-direction:column;transition:transform .18s ease, box-shadow .18s ease}}
.card:hover{{transform:translateY(-3px);box-shadow:0 8px 24px rgba(38,49,58,.10)}}
.card-fig{{margin:0;aspect-ratio:16/9;overflow:hidden;border-bottom:1px solid var(--line);background:var(--washi-deep);display:flex;align-items:center;justify-content:center;position:relative}}
.mon{{
  width:104px;height:104px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-family:var(--f-display);font-weight:800;font-size:50px;
  transform:rotate(-5deg);position:relative;
}}
.mon::after{{content:"";position:absolute;inset:6px;border-radius:50%;border:1px solid currentColor;opacity:.38}}
.mon.m1{{border:5px solid var(--c1);color:var(--c1);background:radial-gradient(circle at 32% 28%, rgba(150,80,47,.16), transparent 62%);box-shadow:0 0 0 2px rgba(150,80,47,.12) inset, 0 4px 14px rgba(150,80,47,.14)}}
.mon.m2{{border:5px solid var(--c2);color:var(--c2);background:radial-gradient(circle at 32% 28%, rgba(78,122,78,.18), transparent 62%);box-shadow:0 0 0 2px rgba(78,122,78,.12) inset, 0 4px 14px rgba(78,122,78,.14)}}
.mon.m3{{border:5px solid var(--c3);color:var(--c3);background:radial-gradient(circle at 32% 28%, rgba(84,74,121,.18), transparent 62%);box-shadow:0 0 0 2px rgba(84,74,121,.12) inset, 0 4px 14px rgba(84,74,121,.14)}}
.card-head{{padding:18px 20px 14px;border-bottom:1px dashed var(--line);display:flex;justify-content:space-between;gap:12px;align-items:flex-start}}
.card-head>div{{min-width:0}}
.card-no{{font-family:var(--f-display);font-size:13px;letter-spacing:.2em;color:var(--sumi-soft)}}
.card h3{{font-family:var(--f-display);font-size:20px;font-weight:700;letter-spacing:.03em;line-height:1.5;margin-top:2px;overflow-wrap:break-word}}
.card .latin{{font-size:13px;color:var(--sumi-soft);letter-spacing:.04em;margin-top:2px}}
.badge{{flex-shrink:0;font-size:13px;letter-spacing:.12em;padding:4px 10px;color:#fff;font-weight:500;white-space:nowrap}}
.badge.kojin{{background:var(--c1)}}
.badge.shu{{background:var(--c2)}}
.badge.chi{{background:var(--c3)}}
.card-body{{padding:16px 20px 20px;flex:1;display:flex;flex-direction:column;gap:12px}}
.card-body dl div{{margin-bottom:10px}}
.card-body dt{{font-size:13px;letter-spacing:.2em;color:var(--sumi-soft);font-weight:700;margin-bottom:2px}}
.card-body dd{{font-size:15px;line-height:1.9}}
.card-q{{margin-top:auto;padding:14px 16px;background:var(--washi);border:1px solid var(--line);font-size:14.5px;line-height:1.85;letter-spacing:.02em}}
.card-q-label{{display:inline-block;font-family:var(--f-display);font-size:12px;font-weight:700;letter-spacing:.2em;color:var(--accent);border:1px solid var(--accent);padding:1px 8px;margin-right:10px}}
.card.hidden{{display:none}}

/* ===== 逆引き表 ===== */
.rev-table-wrap{{overflow-x:auto;background:#fff;border:1px solid var(--line)}}
table.rev{{width:100%;border-collapse:collapse;min-width:640px}}
table.rev th, table.rev td{{padding:15px 16px;font-size:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
table.rev thead th{{font-family:var(--f-display);font-size:15.5px;letter-spacing:.08em;background:var(--sumi);color:var(--washi);border-bottom:none}}
table.rev tbody th{{font-weight:700;width:15em;background:var(--washi-deep);font-family:var(--f-display);letter-spacing:.05em}}
table.rev tr:last-child th, table.rev tr:last-child td{{border-bottom:none}}

/* ===== CTA ===== */
.cta{{background:var(--accent);color:#fff;margin-top:80px}}
.cta-inner{{max-width:1080px;margin:0 auto;padding:72px 24px;text-align:center}}
.cta h2{{font-family:var(--f-display);font-size:clamp(22px,3vw,30px);letter-spacing:.08em;margin-bottom:18px}}
.cta p{{max-width:36em;margin:0 auto 28px;color:rgba(255,255,255,.88);font-size:16.5px}}
.cta-check{{display:inline-block;text-align:left;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.25);padding:22px 30px;margin-bottom:32px;font-size:16px;line-height:2.15}}
.cta-btns{{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}}
.btn{{display:inline-block;padding:15px 34px;font-size:15px;letter-spacing:.1em;text-decoration:none;font-weight:700;transition:all .18s ease}}
.btn-primary{{background:#fff;color:var(--accent)}}
.btn-primary:hover{{background:var(--washi-deep)}}
.btn-ghost{{border:1.5px solid rgba(255,255,255,.7);color:#fff}}
.btn-ghost:hover{{background:rgba(255,255,255,.12)}}

/* ===== フッター（全ページ共通・図鑑シリーズの明色フッター） ===== */
footer{{padding:3rem 24px;text-align:center;background:#fff;border-top:1px solid var(--line)}}
.footer-logo{{font-family:var(--f-display);font-weight:800;color:var(--accent);letter-spacing:.08em}}
.footer-copy{{margin-top:.6rem;font-size:12px;color:var(--sumi-soft);letter-spacing:.06em}}
.sources{{max-width:1080px;margin:0 auto;padding:0 24px 24px;font-size:13.5px;color:var(--sumi-soft);line-height:1.9}}
.sources summary{{cursor:pointer;letter-spacing:.1em;font-weight:700}}

@media (prefers-reduced-motion: reduce){{
  html{{scroll-behavior:auto}}
  .card, .tab, .btn{{transition:none}}
  .card:hover{{transform:none}}
}}
@media (max-width:820px){{
  .hero{{padding:44px 20px 36px}}
  .hero-title{{font-size:clamp(30px,8vw,44px);letter-spacing:.06em}}
  .hero-title small{{letter-spacing:.28em}}
  .premise-grid{{grid-template-columns:minmax(0,1fr)}}
  .stamp-legend{{grid-template-columns:minmax(0,1fr)}}
  .cards{{grid-template-columns:minmax(0,1fr)}}
  .stamp{{width:78px;height:78px;font-size:36px}}
  .section{{padding:48px 20px}}
  .sec-head{{flex-wrap:wrap}}
}}
</style>
</head>
<body>

{nav}

<!-- ===== ヒーロー ===== -->
<header class="hero">
  <div class="hero-title">ホモ・サピエンスの<br>知恵図鑑<small>A FIELD GUIDE TO HUMAN WISDOM</small></div>
  <div class="hero-body">
    <h1>苦手ばかりでは、ない。<em>育てられる力</em>もまた、人の仕様である。</h1>
    <p>『ホモ・サピエンスの苦手図鑑』が、20万年前の脳がつまずくところを集めた本なら、これはその対になる一冊。心理学と組織論が見つけてきた、人がもともと持ち、そして育てられる力を収蔵する。</p>
    <p>効力感、希望、心理的安全性、集合知、メタ認知、知恵。ばらばらの専門用語に見えて、その多くは「才能」ではなく、環境と練習で伸びる筋肉である。全50種を、たとえ話と、自分に向ける問いつきで。</p>
    <span class="hero-note">知恵は、生まれつきではない。<b>育てられる</b>ものである。</span>
    <div><a class="pair-link" href="./nigate-zukan.html">→ 対になる『ホモ・サピエンスの苦手図鑑』を読む</a></div>
  </div>
</header>

<!-- ===== 第一章 前提 ===== -->
<section class="section" id="premise">
  <div class="sec-head"><span class="sec-no">第一章</span><h2>読む前の、三つの前提</h2></div>
  <p class="sec-lead">この図鑑は、優れた人を讃えるための本ではない。誰の中にもある力の育て方を、知るための本である。</p>
  <div class="premise-grid">
    <div class="premise" data-mark="其の一">
      <h3>力は、生まれつきではない</h3>
      <p>自己効力感も、粘り強さ（グリット）も、成長マインドセットも、才能の別名ではない。小さな成功、よい手本、まわりの励まし――どう育つのかが、研究でかなり分かってきている。</p>
    </div>
    <div class="premise" data-mark="其の二">
      <h3>賢さは、一人にとどまらない</h3>
      <p>安心して本音を出せる集団は、優秀な個人の寄せ集めを超えていく。知性は、頭の中だけでなく、人と人のあいだにも宿る。だから「場」の設計が、賢さを左右する。</p>
    </div>
    <div class="premise" data-mark="其の三">
      <h3>成熟は、年月まかせでは来ない</h3>
      <p>メタ認知も、知的謙虚さも、放っておいて歳とともに育つとは限らない。自分の考えをいちど疑い、ふりかえる人のところに、それは少しずつ宿っていく。</p>
    </div>
  </div>
</section>

<!-- ===== 第二章 三系統 ===== -->
<section class="section" id="families">
  <div class="sec-head"><span class="sec-no">第二章</span><h2>知恵の三系統 ─ 焼印の読み方</h2></div>
  <p class="sec-lead">この図鑑の50種は、大きく三つの系統に分かれる。自分の内側の力、人と人のあいだに生まれる力、そして考え方そのものを育てる力。各カードの焼印が、その系統を示している。</p>
  <div class="stamp-legend">
    <div class="legend-item">
      <span class="stamp s1">個</span>
      <h3>自分を動かす力</h3>
      <div class="count">全{n1}種</div>
      <p>「自分ならできそうだ」という手ごたえや、うまくいかないときにも工夫を続ける粘り。行動の火種になる、一人ひとりの内なる力。</p>
    </div>
    <div class="legend-item">
      <span class="stamp s2">衆</span>
      <h3>みんなで賢くなる力</h3>
      <div class="count">全{n2}種</div>
      <p>安心して本音を出せる場、知恵を持ち寄る仕組み、失敗から学び続ける組織。個人を超えて、集団として賢くなるための力。</p>
    </div>
    <div class="legend-item">
      <span class="stamp s3">智</span>
      <h3>しなやかに考える力</h3>
      <div class="count">全{n3}種</div>
      <p>自分の考えを一段上から眺める、わからなさに耐える、しなやかに立ち直る。深く考え、成熟していくための力。</p>
    </div>
  </div>
</section>

<!-- ===== 第三章 標本カード ===== -->
<section class="section" id="cards">
  <div class="sec-head"><span class="sec-no">第三章</span><h2>知恵 五十種</h2></div>
  <p class="sec-lead">それぞれの力には、それを見つけた研究者と、日々のくらしの中の「たとえば」がある。最後の問いは、自分の経験を思い出すための小さな入口。</p>

  <div class="tabs" role="tablist" aria-label="系統で絞り込む">
    <button class="tab active" data-filter="all" type="button">すべて</button>
    <button class="tab" data-filter="kojin" type="button">自分を動かす力</button>
    <button class="tab" data-filter="shu" type="button">みんなで賢くなる</button>
    <button class="tab" data-filter="chi" type="button">しなやかに考える</button>
  </div>

  <div class="cards">

{cards}

  </div>
</section>

<!-- ===== 第四章 逆引き ===== -->
<section class="section" id="reverse">
  <div class="sec-head"><span class="sec-no">第四章</span><h2>逆引き ─ こんなときに、効く知恵</h2></div>
  <p class="sec-lead">くらしや職場で出会う「もやもや」から、育てたい知恵を引ける。答えではなく、次の一歩を探すために。</p>
  <div class="rev-table-wrap">
    <table class="rev">
      <thead>
        <tr><th>こんなとき</th><th>手がかりになる知恵</th><th>次の一歩</th></tr>
      </thead>
      <tbody>
        <tr>
          <th>新しい挑戦に、気後れする</th>
          <td>自己効力感・成長マインドセット・希望理論</td>
          <td>小さな成功を一つ積む。うまくいっている人を、まず観察する</td>
        </tr>
        <tr>
          <th>チームで本音が出ない</th>
          <td>心理的安全性・フォロワーシップ</td>
          <td>失敗を責めない手順を、場に先に組み込む</td>
        </tr>
        <tr>
          <th>会議が、同調で流れていく</th>
          <td>集団思考・傍観者効果・批判的思考</td>
          <td>反対役を意図的に置く。「誰が」でなく「何が」を問う</td>
        </tr>
        <tr>
          <th>変化に、心が折れそう</th>
          <td>レジリエンス・セルフ・コンパッション・心理的資本</td>
          <td>自分を責めず、回復にかかる時間を待つ</td>
        </tr>
        <tr>
          <th>経験を重ねても、伸び悩む</th>
          <td>メタ認知・アンラーニング・ダブルループ学習</td>
          <td>いちど学びをほどき、前提そのものをふりかえる</td>
        </tr>
        <tr>
          <th>分かった気になって、間違える</th>
          <td>知的謙虚さ・ダニング=クルーガー効果・ネガティブ・ケイパビリティ</td>
          <td>「まだ知らない」を出発点にする。結論を、少し保留する</td>
        </tr>
      </tbody>
    </table>
  </div>
</section>

<!-- ===== CTA ===== -->
<section class="cta">
  <div class="cta-inner">
    <h2>知恵は、貯めこむものではなく、使うもの。</h2>
    <p>名前を知っただけでは、力は育たない。育つのは、実際に安心して話し、ふりかえり、試してみる場の中でだ。その練習の場を、この工房は用意しています。</p>
    <div class="cta-check">
      ・本音を出す筋肉を鍛えるなら → デモクラシーフィットネス<br>
      ・古い脳のつまずきと対にして読むなら → ホモ・サピエンスの苦手図鑑<br>
      ・話し合いの技法から学ぶなら → 世界の対話の技法図鑑へ
    </div>
    <div class="cta-btns">
      <a class="btn btn-primary" href="./democracy-fitness.html">デモクラシーフィットネスを見る</a>
      <a class="btn btn-ghost" href="./nigate-zukan.html">苦手図鑑を見る</a>
    </div>
  </div>
</section>

<details class="sources" style="margin-top:48px">
  <summary>出典・参考(主なもの)</summary>
  <p>アルバート・バンデューラ（自己効力感）/キャロル・ドゥエック（成長マインドセット）/マーティン・セリグマン（学習性無力感・楽観・PERMA）/アンジェラ・ダックワース（グリット）/リチャード・ライアン、エドワード・デシ（自己決定理論）/エイミー・エドモンドソン（心理的安全性）/ジェームズ・スロウィッキー（集合知）/ピーター・センゲ『学習する組織』/クリス・アージリス、ドナルド・ショーン（ダブルループ学習）/野中郁次郎（SECIモデル）/ロバート・パットナム（ソーシャル・キャピタル）/ハワード・ガードナー（多重知能）/ダニエル・ゴールマン（EQ）/ロバート・スタンバーグ（実践知・知恵）/ダニエル・カーネマン（システム1と2）/ウィルフレッド・ビオン、キーツ（ネガティブ・ケイパビリティ）/ロバート・キーガン（成人発達理論）/バーバラ・フレドリクソン、クリスティン・ネフ（セルフ・コンパッション）ほか。各カードの記述は公開情報をもとに、きづきくみたて工房が要約・再構成したものです。</p>
</details>

<script>
(function(){{
  var tabs = document.querySelectorAll('.tab');
  var cards = document.querySelectorAll('.card');
  tabs.forEach(function(tab){{
    tab.addEventListener('click', function(){{
      tabs.forEach(function(t){{ t.classList.remove('active'); }});
      tab.classList.add('active');
      var f = tab.getAttribute('data-filter');
      cards.forEach(function(c){{
        if(f === 'all' || c.getAttribute('data-cat') === f){{ c.classList.remove('hidden'); }}
        else{{ c.classList.add('hidden'); }}
      }});
    }});
  }});
}})();
</script>

{kaiyu}

{footer}

</body>
</html>
"""

if __name__ == "__main__":
    main()

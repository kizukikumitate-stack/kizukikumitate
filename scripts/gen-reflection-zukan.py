#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ふりかえりの技法図鑑（reflection-zukan.html）を data/reflection-techniques.json から生成する。

『世界の対話の技法図鑑』(dialogue-zukan.html) と響き合う、実践の図鑑。
ひとりで書く・問いかける・感情を扱う・チームで振り返る・深く掘り下げる の5系統で、
経験を学びに変える「ふりかえりの技法」23種を、やり方・所要時間・由来・コツつきで収蔵する。
『学びと成長の法則図鑑』(growth-laws-zukan.html) と姉妹関係にある（法則＝なぜ / 技法＝どうやって）。

ナビ／回遊／フッターの各マーカー間は nigate-zukan.html から流用し、
公開前に scripts/update-nav.py・scripts/update-kaiyu.py が現行台帳へ再生成する。

使い方:  python3 scripts/gen-reflection-zukan.py
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "reflection-techniques.json")
NIGATE = os.path.join(ROOT, "nigate-zukan.html")
OUT = os.path.join(ROOT, "reflection-zukan.html")

# ── カテゴリ（5系統・JSONの category 文字列 → 表示定義） ──────────
CATS = {
    "ひとりで書く":     {"n": 1, "key": "kaku",  "glyph": "書", "hex": "#4A5E86", "rgb": "74,94,134",
                        "lead": "紙とペンひとつで、頭の中を外に出す。ひとりで、静かに、自分と向き合うための技法。"},
    "問いかける":       {"n": 2, "key": "toi",   "glyph": "問", "hex": "#2E7D74", "rgb": "46,125,116",
                        "lead": "問いの順番で、対話を自然に深めていく。自分にも、人にも使える「問いの型」。"},
    "感情を扱う":       {"n": 3, "key": "kanjo", "glyph": "情", "hex": "#B15A5A", "rgb": "177,90,90",
                        "lead": "揺れた気持ちと、少し距離をとる。感情に飲み込まれずに考えるための技法。"},
    "チームで振り返る": {"n": 4, "key": "team",  "glyph": "衆", "hex": "#A67A2E", "rgb": "166,122,46",
                        "lead": "みんなで経験を持ち寄り、次に活かす。犯人さがしではなく、学びのための場。"},
    "深く掘り下げる":   {"n": 5, "key": "fukaku","glyph": "深", "hex": "#5E4A7C", "rgb": "94,74,124",
                        "lead": "出来事の奥にある前提まで問い直す。同じところでつまずかないための、深いふりかえり。"},
}
CAT_ORDER = ["ひとりで書く", "問いかける", "感情を扱う", "チームで振り返る", "深く掘り下げる"]

# ── 各技法の焼印（emblem）に入れる一字 ────────────────────────
GLYPH = {
    "ジャーナリング": "綴",
    "エクスプレッシブ・ライティング(筆記開示)": "筆",
    "モーニングページ": "朝",
    "感謝日記": "謝",
    "ORID(焦点会話法)": "焦",
    "GROWモデルの問い": "導",
    "What? So What? Now What?": "三",
    "4F(事実・感情・発見・未来)": "四",
    "セルフコンパッション・レター": "慈",
    "セルフトーク距離化(三人称の自己対話)": "距",
    "認知的再評価": "評",
    "脱フュージョン": "脱",
    "KPT(ケプト)": "改",
    "YWT(やったこと・わかったこと・次にやること)": "得",
    "レトロスペクティブ(ふりかえり)": "顧",
    "AAR(アフター・アクション・レビュー)": "検",
    "プレモーテム(事前検死)": "予",
    "フィードフォワード": "前",
    "コルブの経験学習サイクル": "環",
    "ギブスのリフレクティブ・サイクル": "巡",
    "ダブルループ学習": "疑",
    "行為の中の省察/行為についての省察": "察",
    "免疫マップ(変革をはばむ免疫機能)": "免",
}


def esc(s):
    return html.escape(s or "", quote=False)


def marker_block(src, start, end):
    m = re.search(re.escape(start) + r".*?" + re.escape(end), src, re.S)
    if not m:
        raise SystemExit(f"marker not found: {start}")
    return m.group(0)


def color_css():
    out = []
    for name in CAT_ORDER:
        c = CATS[name]
        n, key, rgb = c["n"], c["key"], c["rgb"]
        out.append(
            f".stamp.s{n}{{border:4px solid var(--c{n});color:var(--c{n});"
            f"background:radial-gradient(circle at 32% 28%, rgba({rgb},.15), transparent 62%);"
            f"box-shadow:0 0 0 2px rgba({rgb},.14) inset, 0 3px 10px rgba({rgb},.12)}}")
        out.append(
            f".mon.m{n}{{border:5px solid var(--c{n});color:var(--c{n});"
            f"background:radial-gradient(circle at 32% 28%, rgba({rgb},.17), transparent 62%);"
            f"box-shadow:0 0 0 2px rgba({rgb},.12) inset, 0 4px 14px rgba({rgb},.14)}}")
        out.append(f".badge.{key}{{background:var(--c{n})}}")
    return "\n".join(out)


def root_colors():
    return "\n".join(f"  --c{CATS[n]['n']}:{CATS[n]['hex']};   /* {n} */" for n in CAT_ORDER)


def legend_items(counts):
    parts = []
    for name in CAT_ORDER:
        c = CATS[name]
        parts.append(
            f'    <div class="legend-item">\n'
            f'      <span class="stamp s{c["n"]}">{c["glyph"]}</span>\n'
            f'      <h3>{esc(name)}</h3>\n'
            f'      <div class="count">全{counts[name]}種</div>\n'
            f'      <p>{esc(c["lead"])}</p>\n'
            f'    </div>')
    return "\n".join(parts)


def tabs_html():
    parts = ['    <button class="tab active" data-filter="all" type="button">すべて</button>']
    for name in CAT_ORDER:
        c = CATS[name]
        parts.append(f'    <button class="tab" data-filter="{c["key"]}" type="button">{esc(name)}</button>')
    return "\n".join(parts)


def build_card(idx, e):
    cat = CATS[e["category"]]
    no = f"No.{idx:03d}"
    glyph = GLYPH.get(e["name_ja"], cat["glyph"])
    term = esc(e["name_ja"])
    en = esc(e.get("name_en", ""))
    steps = "".join(f"<li>{esc(s)}</li>" for s in e.get("how_to", []))
    parts = [
        f'    <article class="card" data-cat="{cat["key"]}">',
        f'      <figure class="card-fig"><span class="mon m{cat["n"]}" aria-hidden="true">{esc(glyph)}</span></figure>',
        '      <div class="card-head">',
        '        <div>',
        f'          <span class="card-no">{no}</span>',
        f'          <h3>{term}</h3>',
        f'          <p class="latin">{en}</p>',
    ]
    if e.get("time"):
        parts.append(f'          <p class="card-time">⏱ 所要 {esc(e["time"])}</p>')
    parts += [
        '        </div>',
        f'        <span class="badge {cat["key"]}">{esc(e["category"])}</span>',
        '      </div>',
        '      <div class="card-body">',
        '        <dl>',
        f'          <div><dt>ひとことで</dt><dd>{esc(e["summary"])}</dd></div>',
        f'          <div><dt>どんな技法か</dt><dd>{esc(e["description"])}</dd></div>',
    ]
    if steps:
        parts.append(f'          <div><dt>やり方</dt><dd><ol class="how">{steps}</ol></dd></div>')
    if e.get("scene"):
        parts.append(f'          <div><dt>こんなときに</dt><dd>{esc(e["scene"])}</dd></div>')
    if e.get("origin"):
        parts.append(f'          <div><dt>由来</dt><dd>{esc(e["origin"])}</dd></div>')
    if e.get("evidence"):
        parts.append(f'          <div><dt>たしかめられ方</dt><dd>{esc(e["evidence"])}</dd></div>')
    parts.append('        </dl>')
    if e.get("tips"):
        parts.append(f'        <p class="card-q"><span class="card-q-label">コツ</span>{esc(e["tips"])}</p>')
    parts += ['      </div>', '    </article>']
    return "\n".join(parts)


def main():
    data = json.load(open(DATA, encoding="utf-8"))
    nig = open(NIGATE, encoding="utf-8").read()
    nav = marker_block(nig, "<!-- NAV START -->", "<!-- NAV END -->")
    kaiyu = marker_block(nig, "<!-- KAIYU START -->", "<!-- KAIYU END -->")
    footer = marker_block(nig, "<!-- FOOTER START -->", "<!-- FOOTER END -->")

    counts = {n: sum(1 for e in data if e["category"] == n) for n in CAT_ORDER}
    cards = "\n\n".join(build_card(i + 1, e) for i, e in enumerate(data))

    doc = TEMPLATE
    doc = doc.replace("%%ROOT_COLORS%%", root_colors())
    doc = doc.replace("%%COLOR_CSS%%", color_css())
    doc = doc.replace("%%NAV%%", nav)
    doc = doc.replace("%%LEGEND%%", legend_items(counts))
    doc = doc.replace("%%TABS%%", tabs_html())
    doc = doc.replace("%%CARDS%%", cards)
    doc = doc.replace("%%TOTAL%%", str(len(data)))
    doc = doc.replace("%%KAIYU%%", kaiyu)
    doc = doc.replace("%%FOOTER%%", footer)
    open(OUT, "w", encoding="utf-8").write(doc)
    counts_s = "/".join(f"{n}{counts[n]}" for n in CAT_ORDER)
    print(f"wrote {OUT}  ({len(data)} cards: {counts_s})")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ふりかえりの技法図鑑|経験を学びに変える、ふりかえりの技法|きづきくみたて工房</title>
<meta name="description" content="ジャーナリング、ORID、KPT、AAR、プレモーテム、免疫マップ。ひとりでも、チームでも使える「ふりかえりの技法」23種を、やり方・所要時間・由来・コツつきで収蔵。経験しっぱなしを、学びに変えるための図鑑。">
<link rel="canonical" href="https://kizukikumitate.com/reflection-zukan.html">
<meta property="og:title" content="ふりかえりの技法図鑑|きづきくみたて工房">
<meta property="og:description" content="ひとりでも、チームでも使えるふりかえりの技法23種。やり方・所要時間・由来・コツつきで、経験を学びに変える図鑑。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://kizukikumitate.com/reflection-zukan.html">
<meta property="og:image" content="https://kizukikumitate.com/ogp.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="ふりかえりの技法図鑑｜きづきくみたて工房">
<meta name="twitter:description" content="ひとりでも、チームでも使えるふりかえりの技法23種。やり方・所要・由来・コツつきの図鑑。">
<meta name="twitter:image" content="https://kizukikumitate.com/ogp.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500&family=Noto+Serif+JP:wght@300;400;600&family=Shippori+Mincho:wght@400;600;800&family=Shippori+Mincho+B1:wght@500;700;800&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{
  --washi:#F4F2EA;
  --washi-deep:#EBE8DC;
  --sumi:#26313A;
  --sumi-soft:#4E5A63;
  --accent:#2E6E7A;        /* 青緑:静かな水面。ヒーロー・章見出し・焼印 */
  --accent-soft:#D3E6E7;
%%ROOT_COLORS%%
  --line:#C9C4B4;
  --charcoal:#1e1e1e;
  --forest:#1a5fad;
  --f-display:'Shippori Mincho B1','Hiragino Mincho ProN',serif;
  --f-body:'Zen Kaku Gothic New','Hiragino Kaku Gothic ProN',sans-serif;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  font-family:var(--f-body);
  background:var(--washi);
  color:var(--sumi);
  line-height:1.95;
  font-size:17px;
  hanging-punctuation:allow-end;
  background-image:radial-gradient(rgba(46,110,122,0.035) 1px, transparent 1px);
  background-size:22px 22px;
  overflow-x:hidden;
}
img{max-width:100%}
a{color:var(--accent)}
p, dd, li{word-break:keep-all;overflow-wrap:break-word}

/* ===== 共通グローバルナビ（全ページ共通・sticky） ===== */
nav {
  position: sticky; top: 0; z-index: 100;
  padding: 0.7rem 2rem; display: flex; align-items: center;
  background: rgba(255,255,255,0.97); backdrop-filter: blur(12px);
  border-bottom: 3px solid #3C3489;
}
.nav-logo { display: flex; align-items: center; gap: 0.7rem; text-decoration: none; flex-shrink: 0; margin-right: 4rem; }
.nav-logo img { height: 36px; width: auto; object-fit: contain; }
.nav-logo-text { font-family: 'Shippori Mincho', serif; font-size: 1.1rem; font-weight: 800; white-space: nowrap; color: var(--forest); letter-spacing: 0.06em; }
.nav-links { display: flex; gap: 1.2rem; list-style: none; align-items: center; margin-left: auto; flex-wrap: wrap; }
.nav-links a { font-family: 'Jost', 'Noto Serif JP', sans-serif; font-size: 0.82rem; color: var(--charcoal); text-decoration: none; letter-spacing: 0.04em; }
.nav-links a:hover, .nav-links a.active { color: var(--forest); }
.nav-dropdown { position: relative; display: flex; align-items: center; }
.nav-dropdown-toggle {
  font-family: 'Jost', 'Noto Serif JP', sans-serif; font-size: 0.82rem; font-weight: 400;
  letter-spacing: 0.04em; color: var(--charcoal);
  background: none; border: none; cursor: pointer; padding: 0.4rem 0;
  display: inline-flex; align-items: center; gap: 0.35em; white-space: nowrap; transition: color 0.3s;
}
.nav-caret { font-size: 0.6em; transition: transform 0.25s; }
.nav-dropdown:hover .nav-dropdown-toggle,
.nav-dropdown:focus-within .nav-dropdown-toggle { color: var(--forest); }
.nav-dropdown:hover .nav-caret,
.nav-dropdown:focus-within .nav-caret { transform: rotate(180deg); }
.nav-dropdown-menu {
  position: absolute; top: 100%; left: 50%; transform: translateX(-50%) translateY(8px);
  min-width: 210px; background: #fff; border: 1px solid #eee;
  box-shadow: 0 14px 34px rgba(38,33,92,0.14); border-radius: 12px;
  padding: 0.5rem 0; display: flex; flex-direction: column;
  opacity: 0; visibility: hidden; transition: opacity 0.2s, transform 0.2s; z-index: 300;
}
.nav-dropdown-menu::before { content: ''; position: absolute; top: -10px; left: 0; right: 0; height: 10px; }
.nav-dropdown:hover .nav-dropdown-menu,
.nav-dropdown:focus-within .nav-dropdown-menu { opacity: 1; visibility: visible; transform: translateX(-50%) translateY(4px); }
.nav-dropdown-menu a {
  font-family: 'Noto Sans JP', sans-serif; font-size: 0.84rem; font-weight: 500;
  letter-spacing: 0.02em; text-transform: none; color: #333; text-decoration: none;
  padding: 0.6rem 1.5rem; white-space: nowrap; transition: background 0.15s, color 0.15s;
}
.nav-dropdown-menu a:hover, .nav-dropdown-menu a.active { background: #f4f3fb; color: var(--forest); }
.nav-dropdown:last-child .nav-dropdown-menu { left: auto; right: 0; transform: translateX(0) translateY(8px); }
.nav-dropdown:last-child:hover .nav-dropdown-menu,
.nav-dropdown:last-child:focus-within .nav-dropdown-menu { transform: translateX(0) translateY(4px); }
.nav-hamburger { display: none; margin-left: auto; background: none; border: 0; cursor: pointer; padding: 8px; }
.nav-hamburger span { display: block; width: 24px; height: 2px; background: var(--charcoal); margin: 5px 0; transition: 0.3s; }
.mobile-menu { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 199; background: rgba(255,255,255,0.98); backdrop-filter: blur(12px); flex-direction: column; justify-content: flex-start; overflow-y: auto; align-items: center; gap: 0; padding: 5rem 1.5rem 3rem; }
.mobile-menu.open { display: flex; }
.mobile-menu a { font-family: 'Shippori Mincho', serif; font-size: 1.12rem; font-weight: 600; color: #222; text-decoration: none; padding: 0.75rem 0; width: 100%; text-align: center; border-bottom: 1px solid #e8e8e8; transition: color 0.15s; }
.mobile-menu a:first-child { border-top: 1px solid #e8e8e8; }
.mobile-menu a:hover, .mobile-menu a.active { color: #3C3489; }
.mobile-menu-close { position: absolute; top: 1.2rem; right: 1.5rem; background: none; border: none; font-size: 1.6rem; cursor: pointer; color: #666; line-height: 1; padding: 0.3rem; }
.mobile-acc { width: 100%; border-bottom: 1px solid #e8e8e8; }
.mobile-acc-toggle { width: 100%; display: flex; justify-content: center; align-items: center; gap: 0.5em; background: none; border: none; cursor: pointer; font-family: 'Jost', 'Zen Kaku Gothic New', sans-serif; font-size: 1.15rem; font-weight: 700; letter-spacing: 0.1em; color: #3C3489; padding: 1.15rem 0; }
.mobile-acc-caret { font-size: 0.75em; color: #b0a8d8; transition: transform 0.25s; }
.mobile-acc.open .mobile-acc-caret { transform: rotate(180deg); }
.mobile-acc-panel { display: none; flex-direction: column; align-items: center; padding-bottom: 0.7rem; }
.mobile-acc.open .mobile-acc-panel { display: flex; }
.mobile-acc-panel a { font-family: 'Shippori Mincho', serif; font-size: 1.02rem; font-weight: 600; color: #333; text-decoration: none; padding: 0.6rem 0; width: 100%; text-align: center; border: none; transition: color 0.15s; }
.mobile-acc-panel a:hover, .mobile-acc-panel a.active { color: #3C3489; }
@media (max-width: 1250px) {
  .nav-links { display: none; }
  .nav-hamburger { display: block; }
  .nav-logo { margin-right: 0; }
}

/* ===== ヒーロー ===== */
.hero{max-width:1080px;margin:0 auto;padding:64px 24px 56px}
.hero-title{
  font-family:var(--f-display);font-weight:800;
  font-size:clamp(34px,6vw,68px);
  letter-spacing:.1em;line-height:1.3;
  color:var(--accent);
  border-bottom:3px solid var(--accent);
  padding-bottom:14px;margin-bottom:36px;
}
.hero-title small{display:block;font-size:15px;font-weight:500;letter-spacing:.4em;color:var(--sumi-soft);margin-top:8px}
.hero-body h1{font-family:var(--f-display);font-size:clamp(20px,3vw,26px);font-weight:700;line-height:1.7;letter-spacing:.04em;margin-bottom:20px}
.hero-body h1 em{font-style:normal;background:linear-gradient(transparent 62%, var(--accent-soft) 62%)}
.hero-body p{max-width:34em;color:var(--sumi-soft);margin-bottom:14px}
.hero-note{display:inline-block;margin-top:10px;padding:10px 16px;border:1px solid var(--line);background:#fff;font-size:15px;letter-spacing:.05em}
.hero-note b{color:var(--accent)}
.pair-link{display:inline-block;margin-top:18px;font-size:14.5px;letter-spacing:.03em}

/* ===== 章見出し ===== */
.section{max-width:1080px;margin:0 auto;padding:64px 24px}
.sec-head{display:flex;align-items:baseline;gap:16px;margin-bottom:8px}
.sec-no{font-family:var(--f-display);font-size:14px;letter-spacing:.3em;color:var(--accent);border:1px solid var(--accent);padding:2px 10px;white-space:nowrap}
.sec-head h2{font-family:var(--f-display);font-size:clamp(22px,3vw,30px);font-weight:700;letter-spacing:.06em}
.sec-lead{color:var(--sumi-soft);max-width:42em;margin-bottom:36px}

/* ===== 前提の三箱 ===== */
.premise-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
.premise{background:#fff;border:1px solid var(--line);padding:26px 24px;position:relative}
.premise::before{content:attr(data-mark);position:absolute;top:-15px;left:18px;font-family:var(--f-display);font-size:14px;font-weight:700;background:var(--sumi);color:var(--washi);padding:3px 12px;letter-spacing:.15em}
.premise h3{font-family:var(--f-display);font-size:19px;margin:8px 0 8px;letter-spacing:.04em}
.premise p{font-size:15.5px;color:var(--sumi-soft);line-height:1.9}

/* ===== 系統（焼印） ===== */
.stamp-legend{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:18px;margin-top:8px}
.legend-item{background:#fff;border:1px solid var(--line);padding:24px 18px 20px;text-align:center;position:relative}
.stamp{
  width:92px;height:92px;border-radius:50%;
  display:inline-flex;align-items:center;justify-content:center;
  font-family:var(--f-display);font-weight:800;font-size:42px;
  transform:rotate(-5deg);letter-spacing:0;position:relative;margin-bottom:16px;
}
.stamp::after{content:"";position:absolute;inset:5px;border-radius:50%;border:1px solid currentColor;opacity:.4}
.legend-item h3{font-size:17px;font-family:var(--f-display);letter-spacing:.08em;margin-bottom:6px}
.legend-item .count{font-size:12.5px;letter-spacing:.18em;color:var(--sumi-soft);margin-bottom:8px}
.legend-item p{font-size:14.5px;color:var(--sumi-soft);line-height:1.85;text-align:left}

/* ===== フィルタタブ ===== */
.tabs{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 32px}
.tab{font-family:var(--f-body);font-size:15.5px;letter-spacing:.08em;padding:8px 20px;border:1px solid var(--sumi);background:transparent;color:var(--sumi);cursor:pointer;transition:all .18s ease}
.tab:hover{background:var(--washi-deep)}
.tab.active{background:var(--sumi);color:var(--washi)}
.tab:focus-visible{outline:3px solid var(--accent);outline-offset:2px}

/* ===== 標本カード ===== */
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}
.card{background:#fff;border:1px solid var(--line);display:flex;flex-direction:column;transition:transform .18s ease, box-shadow .18s ease}
.card:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(38,49,58,.10)}
.card-fig{margin:0;aspect-ratio:16/9;overflow:hidden;border-bottom:1px solid var(--line);background:var(--washi-deep);display:flex;align-items:center;justify-content:center;position:relative}
.mon{
  width:104px;height:104px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-family:var(--f-display);font-weight:800;font-size:50px;
  transform:rotate(-5deg);position:relative;
}
.mon::after{content:"";position:absolute;inset:6px;border-radius:50%;border:1px solid currentColor;opacity:.38}
%%COLOR_CSS%%
.card-head{padding:18px 20px 14px;border-bottom:1px dashed var(--line);display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
.card-head>div{min-width:0}
.card-no{font-family:var(--f-display);font-size:13px;letter-spacing:.2em;color:var(--sumi-soft)}
.card h3{font-family:var(--f-display);font-size:20px;font-weight:700;letter-spacing:.03em;line-height:1.5;margin-top:2px;overflow-wrap:break-word}
.card .latin{font-size:13px;color:var(--sumi-soft);letter-spacing:.04em;margin-top:2px}
.card-time{font-size:12px;color:var(--accent);letter-spacing:.06em;margin-top:5px;font-weight:500}
.badge{flex-shrink:0;font-size:13px;letter-spacing:.12em;padding:4px 10px;color:#fff;font-weight:500;white-space:nowrap}
.card-body{padding:16px 20px 20px;flex:1;display:flex;flex-direction:column;gap:12px}
.card-body dl div{margin-bottom:10px}
.card-body dt{font-size:13px;letter-spacing:.2em;color:var(--sumi-soft);font-weight:700;margin-bottom:2px}
.card-body dd{font-size:15px;line-height:1.9}
.card-body ol.how{margin:4px 0 0;padding-left:1.4em}
.card-body ol.how li{font-size:14.5px;line-height:1.82;margin-bottom:5px}
.card-q{margin-top:auto;padding:14px 16px;background:var(--washi);border:1px solid var(--line);font-size:14.5px;line-height:1.85;letter-spacing:.02em}
.card-q-label{display:inline-block;font-family:var(--f-display);font-size:12px;font-weight:700;letter-spacing:.2em;color:var(--accent);border:1px solid var(--accent);padding:1px 8px;margin-right:10px}
.card.hidden{display:none}

/* ===== 逆引き表 ===== */
.rev-table-wrap{overflow-x:auto;background:#fff;border:1px solid var(--line)}
table.rev{width:100%;border-collapse:collapse;min-width:640px}
table.rev th, table.rev td{padding:15px 16px;font-size:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
table.rev thead th{font-family:var(--f-display);font-size:15.5px;letter-spacing:.08em;background:var(--sumi);color:var(--washi);border-bottom:none}
table.rev tbody th{font-weight:700;width:15em;background:var(--washi-deep);font-family:var(--f-display);letter-spacing:.05em}
table.rev tr:last-child th, table.rev tr:last-child td{border-bottom:none}

/* ===== CTA ===== */
.cta{background:var(--accent);color:#fff;margin-top:80px}
.cta-inner{max-width:1080px;margin:0 auto;padding:72px 24px;text-align:center}
.cta h2{font-family:var(--f-display);font-size:clamp(22px,3vw,30px);letter-spacing:.08em;margin-bottom:18px}
.cta p{max-width:36em;margin:0 auto 28px;color:rgba(255,255,255,.88);font-size:16.5px}
.cta-check{display:inline-block;text-align:left;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.25);padding:22px 30px;margin-bottom:32px;font-size:16px;line-height:2.15}
.cta-btns{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}
.btn{display:inline-block;padding:15px 34px;font-size:15px;letter-spacing:.1em;text-decoration:none;font-weight:700;transition:all .18s ease}
.btn-primary{background:#fff;color:var(--accent)}
.btn-primary:hover{background:var(--washi-deep)}
.btn-ghost{border:1.5px solid rgba(255,255,255,.7);color:#fff}
.btn-ghost:hover{background:rgba(255,255,255,.12)}

/* ===== フッター前の出典 ===== */
footer{padding:3rem 24px;text-align:center;background:#fff;border-top:1px solid var(--line)}
.footer-logo{font-family:var(--f-display);font-weight:800;color:var(--accent);letter-spacing:.08em}
.footer-copy{margin-top:.6rem;font-size:12px;color:var(--sumi-soft);letter-spacing:.06em}
.sources{max-width:1080px;margin:0 auto;padding:0 24px 24px;font-size:13.5px;color:var(--sumi-soft);line-height:1.9}
.sources summary{cursor:pointer;letter-spacing:.1em;font-weight:700}

@media (prefers-reduced-motion: reduce){
  html{scroll-behavior:auto}
  .card, .tab, .btn{transition:none}
  .card:hover{transform:none}
}
@media (max-width:820px){
  .hero{padding:44px 20px 36px}
  .hero-title{font-size:clamp(30px,8vw,44px);letter-spacing:.06em}
  .hero-title small{letter-spacing:.28em}
  .premise-grid{grid-template-columns:minmax(0,1fr)}
  .stamp-legend{grid-template-columns:minmax(0,1fr)}
  .cards{grid-template-columns:minmax(0,1fr)}
  .stamp{width:78px;height:78px;font-size:36px}
  .section{padding:48px 20px}
  .sec-head{flex-wrap:wrap}
}
</style>
</head>
<body>

%%NAV%%

<!-- ===== ヒーロー ===== -->
<header class="hero">
  <div class="hero-title">ふりかえりの<br>技法図鑑<small>A FIELD GUIDE TO REFLECTION</small></div>
  <div class="hero-body">
    <h1>経験は、積むだけでは<em>学びにならない</em>。</h1>
    <p>同じ経験をしても、そこから学べる量は「ふりかえるかどうか」で変わる。忙しいと「ふりかえる暇があれば一件でも多くこなしたい」と思いがちだが、実験では、その直感はくり返し裏切られてきた。数分立ち止まる人のほうが、次に伸びる。</p>
    <p>この図鑑は、経験を学びに変える「ふりかえりの技法」を23種おさめたもの。ひとりで書くものから、チームで囲むもの、前提そのものを問い直す深いものまで。やり方・所要時間・由来・つまずかないコツを添えた。</p>
    <span class="hero-note">ふりかえりは、反省ではない。<b>次の一歩を、取り出す</b>作業である。</span>
    <div><a class="pair-link" href="./growth-laws-zukan.html">→ 対になる『学びと成長の法則図鑑』を読む</a></div>
  </div>
</header>

<!-- ===== 第一章 前提 ===== -->
<section class="section" id="premise">
  <div class="sec-head"><span class="sec-no">第一章</span><h2>ふりかえる前の、三つの前提</h2></div>
  <p class="sec-lead">この図鑑は、過ぎたことを悔やむための本ではない。経験から「使える一歩」を取り出すための、道具箱である。</p>
  <div class="premise-grid">
    <div class="premise" data-mark="其の一">
      <h3>ふりかえりは、反省ではない</h3>
      <p>「何がダメだったか」を数えるのがふりかえりではない。うまくいったことも、意外だったことも並べて、「次にどうするか」を取り出す。自分を責めるためではなく、次の自分を助けるために立ち止まる。</p>
    </div>
    <div class="premise" data-mark="其の二">
      <h3>事実と、感情を分ける</h3>
      <p>多くの技法が、まず「何が起きたか（事実）」と「どう感じたか（感情）」を分けることから始まる。混ぜたまま考えると、話が空中戦になりやすい。分けるからこそ、そこから学びを取り出せる。</p>
    </div>
    <div class="premise" data-mark="其の三">
      <h3>「次の一歩」まで書いて、完成</h3>
      <p>気づきを出しただけでは、ふりかえりは半分。「では、次に何を、いつ試すか」まで具体にして、はじめて経験が前に進む。行動の一歩を決めるところまでを、ひとつのセットとして扱う。</p>
    </div>
  </div>
</section>

<!-- ===== 第二章 五系統 ===== -->
<section class="section" id="families">
  <div class="sec-head"><span class="sec-no">第二章</span><h2>ふりかえりの五系統 ─ 焼印の読み方</h2></div>
  <p class="sec-lead">この図鑑の技法は、大きく五つの系統に分かれる。ひとりで書く、問いで深める、感情を扱う、チームで囲む、前提まで掘り下げる。各カードの焼印が、その系統を示している。</p>
  <div class="stamp-legend">
%%LEGEND%%
  </div>
</section>

<!-- ===== 第三章 標本カード ===== -->
<section class="section" id="cards">
  <div class="sec-head"><span class="sec-no">第三章</span><h2>ふりかえりの技法 二十三種</h2></div>
  <p class="sec-lead">それぞれの技法に、やり方・所要時間・生まれた由来がある。所要時間の短いものから試すのがおすすめ。最後の「コツ」は、つまずかないための小さな一言。</p>

  <div class="tabs" role="tablist" aria-label="系統で絞り込む">
%%TABS%%
  </div>

  <div class="cards">

%%CARDS%%

  </div>
</section>

<!-- ===== 第四章 逆引き ===== -->
<section class="section" id="reverse">
  <div class="sec-head"><span class="sec-no">第四章</span><h2>逆引き ─ こんなときに、この技法</h2></div>
  <p class="sec-lead">その日の状況から、合いそうな技法を引ける。迷ったら、所要時間の短いものから試すとよい。</p>
  <div class="rev-table-wrap">
    <table class="rev">
      <thead>
        <tr><th>こんなとき</th><th>合いそうな技法</th><th>はじめの一歩</th></tr>
      </thead>
      <tbody>
        <tr>
          <th>ひとりで、頭の中を整理したい</th>
          <td>ジャーナリング・モーニングページ・エクスプレッシブ・ライティング</td>
          <td>タイマーをかけ、手を止めず数分書き出す。うまく書こうとしない</td>
        </tr>
        <tr>
          <th>気持ちがざわついて、動けない</th>
          <td>セルフコンパッション・レター・セルフトーク距離化・認知的再評価</td>
          <td>自分を友人のように扱う。別の見方を、最低3つ考えてみる</td>
        </tr>
        <tr>
          <th>チームの経験を、次に活かしたい</th>
          <td>KPT・YWT・レトロスペクティブ・AAR</td>
          <td>「人ではなく出来事」を見る。次の一手を1〜3個に絞る</td>
        </tr>
        <tr>
          <th>大事な計画の、失敗を防ぎたい</th>
          <td>プレモーテム</td>
          <td>「もう失敗した」と仮定して、その理由を先に洗い出す</td>
        </tr>
        <tr>
          <th>同じ失敗を、くり返してしまう</th>
          <td>ダブルループ学習・免疫マップ・経験学習サイクル</td>
          <td>対処ではなく、その裏にある前提そのものを問い直す</td>
        </tr>
        <tr>
          <th>人に、助言を贈りたい</th>
          <td>フィードフォワード・GROWモデルの問い</td>
          <td>過去の批評ではなく、これからできる提案を渡す</td>
        </tr>
      </tbody>
    </table>
  </div>
</section>

<!-- ===== CTA ===== -->
<section class="cta">
  <div class="cta-inner">
    <h2>ふりかえりは、ひとりでも。深まるのは、対話の中で。</h2>
    <p>技法を知っただけでは、学びは深まらない。深まるのは、実際に安心して話し、問い、ふりかえる場の中でだ。その練習の場を、この工房は用意しています。</p>
    <div class="cta-check">
      ・本音を出し、ふりかえる筋肉を鍛えるなら → デモクラシーフィットネス<br>
      ・話し合いそのものの技法を知るなら → 世界の対話の技法図鑑<br>
      ・成長のしくみと対にして読むなら → 学びと成長の法則図鑑へ
    </div>
    <div class="cta-btns">
      <a class="btn btn-primary" href="./democracy-fitness.html">デモクラシーフィットネスを見る</a>
      <a class="btn btn-ghost" href="./growth-laws-zukan.html">学びと成長の法則図鑑を見る</a>
    </div>
  </div>
</section>

<details class="sources" style="margin-top:48px">
  <summary>出典・参考(主なもの)</summary>
  <p>ジェームズ・ペネベイカー（筆記開示）/ロバート・エモンズ＆マイケル・マカロー（感謝日記）/ジュリア・キャメロン（モーニングページ）/文化事業協会ICA、ブライアン・スタンフィールド（ORID）/ジョン・ウィットモア（GROWモデル）/テリー・ボートン、ゲイリー・ロルフ（What/So What/Now What）/ロジャー・グリーナウェイ（4F）/クリスティン・ネフ（セルフコンパッション）/イーサン・クロス（セルフトーク距離化）/ジェームズ・グロス（認知的再評価）/スティーブン・ヘイズ（脱フュージョン・ACT）/平鍋健児、アリスター・コーバーン（KPT）/日本能率協会コンサルティング（YWT）/ノーマン・カース、エスター・ダービー＆ダイアナ・ラーセン（レトロスペクティブ）/米陸軍（AAR）/ゲイリー・クライン（プレモーテム）/マーシャル・ゴールドスミス（フィードフォワード）/デイヴィッド・コルブ（経験学習サイクル）/グラハム・ギブス（リフレクティブ・サイクル）/クリス・アージリス、ドナルド・ショーン（ダブルループ学習・行為の中の省察）/ロバート・キーガン＆リサ・ラスコウ・レイヒー（免疫マップ）ほか。各カードの記述は公開された書籍・研究をもとに、きづきくみたて工房が要約・再構成したものです。</p>
</details>

<script>
(function(){
  var tabs = document.querySelectorAll('.tab');
  var cards = document.querySelectorAll('.card');
  tabs.forEach(function(tab){
    tab.addEventListener('click', function(){
      tabs.forEach(function(t){ t.classList.remove('active'); });
      tab.classList.add('active');
      var f = tab.getAttribute('data-filter');
      cards.forEach(function(c){
        if(f === 'all' || c.getAttribute('data-cat') === f){ c.classList.remove('hidden'); }
        else{ c.classList.add('hidden'); }
      });
    });
  });
})();
</script>

%%KAIYU%%

%%FOOTER%%

<script>
  /* グローバルナビ開閉（standard variant・台帳生成対象外なので各ページに持つ） */
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileClose = document.getElementById('mobileClose');
  if (hamburger && mobileMenu) {
    function openMenu() { hamburger.classList.add('open'); mobileMenu.classList.add('open'); document.body.style.overflow = 'hidden'; }
    function closeMenu() { hamburger.classList.remove('open'); mobileMenu.classList.remove('open'); document.body.style.overflow = ''; }
    hamburger.addEventListener('click', () => { mobileMenu.classList.contains('open') ? closeMenu() : openMenu(); });
    if (mobileClose) mobileClose.addEventListener('click', closeMenu);
    mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
    mobileMenu.querySelectorAll('.mobile-acc-toggle').forEach(function(btn){ btn.addEventListener('click', function(){ btn.parentElement.classList.toggle('open'); }); });
  }
</script>

</body>
</html>
"""

if __name__ == "__main__":
    main()

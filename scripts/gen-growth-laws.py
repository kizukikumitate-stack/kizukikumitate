#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学びと成長の法則図鑑（growth-laws-zukan.html）を data/growth-laws.json から生成する。

心理学・学習科学・組織論が「実験でくり返し確かめてきた」学びと成長のしくみを、
根拠（evidence）と、過信を戒める但し書き（caveat）と、今日ためせる一手（action）つきで収蔵する。
『ふりかえりの技法図鑑』(reflection-zukan.html) と姉妹関係にある。

ナビ／回遊／フッターの各マーカー間は nigate-zukan.html から流用し、
公開前に scripts/update-nav.py・scripts/update-kaiyu.py が現行台帳へ再生成する。

使い方:  python3 scripts/gen-growth-laws.py
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "growth-laws.json")
NIGATE = os.path.join(ROOT, "nigate-zukan.html")
OUT = os.path.join(ROOT, "growth-laws-zukan.html")

# ── カテゴリ（5系統・JSONの category 文字列 → 表示定義） ──────────
CATS = {
    "学び方":     {"n": 1, "key": "manabi", "glyph": "学", "hex": "#2E5E86",
                  "rgb": "46,94,134",  "lead": "覚える・練習する・上達する。記憶と技能をどう積むかという、学習そのもののしくみ。"},
    "心の持ち方": {"n": 2, "key": "kokoro", "glyph": "心", "hex": "#B4602F",
                  "rgb": "180,96,47",  "lead": "やる気・自信・粘り。挑戦を続けるか、あきらめるかを左右する、内側のかまえ。"},
    "習慣":       {"n": 3, "key": "shukan", "glyph": "習", "hex": "#9A7A22",
                  "rgb": "154,122,34", "lead": "意志の力ではなく、しくみで続ける。行動が自動化し、前進が積み重なるための設計。"},
    "体と脳":     {"n": 4, "key": "karada", "glyph": "脳", "hex": "#2E7D6B",
                  "rgb": "46,125,107", "lead": "睡眠・運動・緊張・回復。学ぶ脳を支える、からだ側のコンディション。"},
    "人との関わり": {"n": 5, "key": "hito",  "glyph": "人", "hex": "#6E4A78",
                  "rgb": "110,74,120", "lead": "ふりかえり、経験を回し、安心して話せる場。人と人のあいだで、学びは深まる。"},
}
CAT_ORDER = ["学び方", "心の持ち方", "習慣", "体と脳", "人との関わり"]

# ── 各法則の焼印（emblem）に入れる一字 ────────────────────────
GLYPH = {
    "思い出す練習の法則(テスト効果)": "想",
    "忘却曲線の法則": "忘",
    "間隔をあける法則(分散学習)": "間",
    "混ぜて練習する法則(インターリービング)": "混",
    "あえて苦労する法則(望ましい困難)": "難",
    "自分でつくると忘れない法則(生成効果)": "創",
    "教える人が一番学ぶ法則(プロテジェ効果)": "教",
    "量より質の練習の法則(意図的練習)": "質",
    "「まだ」の力の法則(成長マインドセット)": "未",
    "「できそう」が先の法則(自己効力感)": "効",
    "夢中ゾーンの法則(フロー)": "没",
    "やり抜く力の法則(グリット)": "粘",
    "ご褒美が逆効果になる法則(自己決定理論)": "決",
    "66日の法則(習慣形成)": "慣",
    "「もしXならY」の法則(実装意図)": "契",
    "小さな前進の法則(進捗の原理)": "進",
    "寝ている間に上達する法則(睡眠と記憶固定)": "眠",
    "運動が脳を育てる法則": "動",
    "ちょうどいい緊張の法則(逆U字)": "張",
    "回復してこそ強くなる法則(負荷と回復)": "復",
    "振り返りが伸びを生む法則(リフレクション)": "省",
    "経験は回して学ぶ法則(経験学習サイクル)": "環",
    "安心して発言できるチームの法則(心理的安全性)": "安",
}


def esc(s):
    return html.escape(s or "", quote=False)


def marker_block(src, start, end):
    m = re.search(re.escape(start) + r".*?" + re.escape(end), src, re.S)
    if not m:
        raise SystemExit(f"marker not found: {start}")
    return m.group(0)


def color_css():
    """5系統ぶんの焼印・バッジの色ルールをまとめて生成する。"""
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
    parts = [
        f'    <article class="card" data-cat="{cat["key"]}">',
        f'      <figure class="card-fig"><span class="mon m{cat["n"]}" aria-hidden="true">{esc(glyph)}</span></figure>',
        '      <div class="card-head">',
        '        <div>',
        f'          <span class="card-no">{no}</span>',
        f'          <h3>{term}</h3>',
        f'          <p class="latin">{en}</p>',
        '        </div>',
        f'        <span class="badge {cat["key"]}">{esc(e["category"])}</span>',
        '      </div>',
        '      <div class="card-body">',
        '        <dl>',
        f'          <div><dt>ひとことで</dt><dd>{esc(e["summary"])}</dd></div>',
        f'          <div><dt>どういう法則か</dt><dd>{esc(e["description"])}</dd></div>',
        f'          <div><dt>たしかめられ方</dt><dd>{esc(e["evidence"])}</dd></div>',
        f'          <div><dt>気をつけたいこと</dt><dd>{esc(e["caveat"])}</dd></div>',
        '        </dl>',
        f'        <p class="card-q"><span class="card-q-label">やってみる</span>{esc(e["action"])}</p>',
    ]
    if e.get("source"):
        parts.append(f'        <p class="card-src">出典：{esc(e["source"])}</p>')
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
<title>学びと成長の法則図鑑|科学が確かめた、学びと成長のしくみ|きづきくみたて工房</title>
<meta name="description" content="テスト効果、忘却曲線、成長マインドセット、心理的安全性。心理学と学習科学が実験でくり返し確かめてきた学びと成長の法則23種を、根拠と、過信を戒める但し書きと、今日ためせる一手つきで収蔵。">
<link rel="canonical" href="https://kizukikumitate.com/growth-laws-zukan.html">
<meta property="og:title" content="学びと成長の法則図鑑|きづきくみたて工房">
<meta property="og:description" content="科学が確かめてきた、学びと成長のしくみ23種。根拠と、過信を戒める但し書きと、今日ためせる一手つきの図鑑。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://kizukikumitate.com/growth-laws-zukan.html">
<meta property="og:image" content="https://kizukikumitate.com/ogp.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="学びと成長の法則図鑑｜きづきくみたて工房">
<meta name="twitter:description" content="科学が確かめてきた、学びと成長のしくみ23種。根拠と但し書きと、今日ためせる一手つき。">
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
  --accent:#2F6B4C;        /* 常磐:育つ力の主色。ヒーロー・章見出し・焼印 */
  --accent-soft:#D7E7DD;
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
  background-image:radial-gradient(rgba(47,107,76,0.035) 1px, transparent 1px);
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
.badge{flex-shrink:0;font-size:13px;letter-spacing:.12em;padding:4px 10px;color:#fff;font-weight:500;white-space:nowrap}
.card-body{padding:16px 20px 20px;flex:1;display:flex;flex-direction:column;gap:12px}
.card-body dl div{margin-bottom:10px}
.card-body dt{font-size:13px;letter-spacing:.2em;color:var(--sumi-soft);font-weight:700;margin-bottom:2px}
.card-body dd{font-size:15px;line-height:1.9}
.card-q{margin-top:auto;padding:14px 16px;background:var(--washi);border:1px solid var(--line);font-size:14.5px;line-height:1.85;letter-spacing:.02em}
.card-q-label{display:inline-block;font-family:var(--f-display);font-size:12px;font-weight:700;letter-spacing:.2em;color:var(--accent);border:1px solid var(--accent);padding:1px 8px;margin-right:10px}
.card-src{font-size:11.5px;color:var(--sumi-soft);line-height:1.7;letter-spacing:.01em;opacity:.82}
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
  <div class="hero-title">学びと成長の<br>法則図鑑<small>A FIELD GUIDE TO THE LAWS OF LEARNING & GROWTH</small></div>
  <div class="hero-body">
    <h1>「がんばり方」には、<em>科学が確かめたコツ</em>がある。</h1>
    <p>覚えたそばから忘れる。スラスラ進んだのに身についていない。同じ失敗をくり返す――それは根性の問題ではなく、脳と心のもともとの仕様である。心理学と学習科学は、そのしくみを実験でくり返し確かめてきた。</p>
    <p>この図鑑は、そうして見つかった「学びと成長の法則」を23種おさめたもの。ひとつひとつに、確かめられ方（根拠）と、言い過ぎを戒める但し書きと、今日ためせる一手を添えた。魔法は載っていない。だが、遠回りを減らすヒントは載っている。</p>
    <span class="hero-note">効くやり方は、たいてい<b>その場では手ごたえが薄い</b>。手ごたえと成果は、別ものである。</span>
    <div><a class="pair-link" href="./reflection-zukan.html">→ 対になる『ふりかえりの技法図鑑』を読む</a></div>
  </div>
</header>

<!-- ===== 第一章 前提 ===== -->
<section class="section" id="premise">
  <div class="sec-head"><span class="sec-no">第一章</span><h2>読む前の、三つの前提</h2></div>
  <p class="sec-lead">この図鑑は、才能のある人をうらやむための本ではない。誰にでも効く「学び方の道具」を、手に取るための本である。</p>
  <div class="premise-grid">
    <div class="premise" data-mark="其の一">
      <h3>手ごたえは、あてにならない</h3>
      <p>読み返すと「わかった気」になるのに、記憶には残らない。思い出そうとする練習は苦しいのに、よく残る。その場の手ごたえと、あとに残る力は、しばしば逆を向く。だから直感だけで勉強法を選ぶと、効かない方に流れやすい。</p>
    </div>
    <div class="premise" data-mark="其の二">
      <h3>法則にも、限界がある</h3>
      <p>ここに載る法則は、実験で確かめられたもの。それでも「万能薬」ではない。再現性が議論されているもの、条件つきでしか効かないものもある。だから各カードには、あえて「気をつけたいこと」を添えた。過信は、学びを遠ざける。</p>
    </div>
    <div class="premise" data-mark="其の三">
      <h3>成長は、頭だけの話ではない</h3>
      <p>睡眠、運動、緊張、回復。学ぶ脳は、からだの上に乗っている。徹夜で覚えたことは定着しにくく、休みは成長の一部である。心・習慣・体を、ひとつながりのものとして扱うのが、この図鑑の立場だ。</p>
    </div>
  </div>
</section>

<!-- ===== 第二章 五系統 ===== -->
<section class="section" id="families">
  <div class="sec-head"><span class="sec-no">第二章</span><h2>法則の五系統 ─ 焼印の読み方</h2></div>
  <p class="sec-lead">この図鑑の法則は、大きく五つの系統に分かれる。学び方そのもの、心のかまえ、続けるしくみ、体のコンディション、そして人とのあいだ。各カードの焼印が、その系統を示している。</p>
  <div class="stamp-legend">
%%LEGEND%%
  </div>
</section>

<!-- ===== 第三章 標本カード ===== -->
<section class="section" id="cards">
  <div class="sec-head"><span class="sec-no">第三章</span><h2>成長の法則 二十三種</h2></div>
  <p class="sec-lead">それぞれの法則には、それを確かめた研究と、言い過ぎないための但し書きがある。最後の「やってみる」は、明日からの小さな一歩。</p>

  <div class="tabs" role="tablist" aria-label="系統で絞り込む">
%%TABS%%
  </div>

  <div class="cards">

%%CARDS%%

  </div>
</section>

<!-- ===== 第四章 逆引き ===== -->
<section class="section" id="reverse">
  <div class="sec-head"><span class="sec-no">第四章</span><h2>逆引き ─ こんなときに、効く法則</h2></div>
  <p class="sec-lead">学びや育成でぶつかる「もやもや」から、手がかりになる法則を引ける。答えではなく、次の一歩を探すために。</p>
  <div class="rev-table-wrap">
    <table class="rev">
      <thead>
        <tr><th>こんなとき</th><th>手がかりになる法則</th><th>次の一歩</th></tr>
      </thead>
      <tbody>
        <tr>
          <th>覚えても、すぐ忘れてしまう</th>
          <td>思い出す練習・忘却曲線・間隔をあける</td>
          <td>読み返すより、閉じて思い出す。忘れかけた頃に、数分だけ復習する</td>
        </tr>
        <tr>
          <th>練習しても、本番で使えない</th>
          <td>混ぜて練習する・あえて苦労する・量より質</td>
          <td>種類を混ぜ、少し難しくする。弱点をひとつ決めて練習する</td>
        </tr>
        <tr>
          <th>やる気が、続かない</th>
          <td>「できそう」が先・小さな前進・ご褒美が逆効果</td>
          <td>確実にできるサイズに刻み、最初の成功を早くつくる</td>
        </tr>
        <tr>
          <th>新しい習慣が、身につかない</th>
          <td>66日の法則・「もしXならY」・小さな前進</td>
          <td>既にある日課を引き金にする。1日抜けても誤差として続ける</td>
        </tr>
        <tr>
          <th>がんばっているのに、消耗する</th>
          <td>寝ている間に上達・回復してこそ強くなる・ちょうどいい緊張</td>
          <td>睡眠を削らない。全力のあとに、意識して回復を予定に入れる</td>
        </tr>
        <tr>
          <th>チームや後輩が、育たない</th>
          <td>教える人が一番学ぶ・振り返りが伸びを生む・安心して発言できるチーム</td>
          <td>説明する側を任せる。責める前に「何が起きたか」を一緒に見る</td>
        </tr>
      </tbody>
    </table>
  </div>
</section>

<!-- ===== CTA ===== -->
<section class="cta">
  <div class="cta-inner">
    <h2>法則は、知るためではなく、試すためにある。</h2>
    <p>名前を覚えただけでは、力は育たない。育つのは、実際に思い出し、間をあけ、ふりかえり、安心して話す――その練習の中でだ。その場づくりを、この工房は手伝っています。</p>
    <div class="cta-check">
      ・本音を出し、ふりかえる筋肉を鍛えるなら → デモクラシーフィットネス<br>
      ・学びを深める「ふりかえりの技法」を知るなら → ふりかえりの技法図鑑<br>
      ・古い脳のつまずきと対にして読むなら → ホモ・サピエンスの苦手図鑑へ
    </div>
    <div class="cta-btns">
      <a class="btn btn-primary" href="./democracy-fitness.html">デモクラシーフィットネスを見る</a>
      <a class="btn btn-ghost" href="./reflection-zukan.html">ふりかえりの技法図鑑を見る</a>
    </div>
  </div>
</section>

<details class="sources" style="margin-top:48px">
  <summary>出典・参考(主なもの)</summary>
  <p>ローディガー＆カーピキ（テスト効果）/エビングハウス、ムーレ＆ドロス（忘却曲線）/セペダら（分散学習）/ローラー＆テイラー（インターリービング）/ロバート・ビョーク（望ましい困難）/スラメカ＆グラフ（生成効果）/ネストイコら（プロテジェ効果）/エリクソンら、マクナマラら（意図的練習）/キャロル・ドゥエック、イェーガーら、シスクら（成長マインドセット）/アルバート・バンデューラ、スタイコビッチ＆ルーサンス（自己効力感）/チクセントミハイ（フロー）/ダックワースら、クレデら（グリット）/デシ、デシ＆コスナー＆ライアン（自己決定理論）/ラリーら（習慣形成）/ゴルヴィツァー＆シーラン（実装意図）/アマビール＆クレイマー（進捗の原理）/ウォーカーら、スティックゴールド（睡眠と記憶）/エリクソンら（運動と脳）/ヤーキーズ＆ドッドソン（逆U字）/マスラック＆ジャクソン（バーンアウト）/ディ・ステファノら（リフレクション）/デイヴィッド・コルブ（経験学習）/エイミー・エドモンドソン（心理的安全性）ほか。各カードの記述は公開された研究・論文をもとに、きづきくみたて工房が要約・再構成したものです。数値や効果量は研究条件によって幅があります。</p>
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

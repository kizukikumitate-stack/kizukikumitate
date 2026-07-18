#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ホモ・サピエンスの苦手図鑑 カードイラスト(SVG)ジェネレータ。
Canvaクォータ待ちの間のイラストとして、同一画風の12枚を images/nigate/*.svg に生成する。
パレット: 和紙クリーム/藍/金/青緑/焦茶橙。4:3 (800x600)。
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "images", "nigate")

WASHI = "#faf8f2"
WASHI_D = "#efe9da"
AI = "#16132a"        # 藍(深)
AI_M = "#2c3555"      # 藍(中)
GOLD = "#d9a441"
GOLD_L = "#ecc678"
TEAL = "#0f6e56"
TEAL_L = "#3f8f79"
DAWN = "#d85a30"      # 焦茶橙
CREAM = "#f0dcc0"     # 肌・面

HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" role="img">\n'
GRAIN = ('<filter id="g"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/>'
         '<feColorMatrix type="saturate" values="0"/></filter>\n')
TAIL = '<rect width="800" height="600" filter="url(#g)" opacity="0.05"/>\n</svg>\n'


def bg(color=WASHI):
    return f'<rect width="800" height="600" fill="{color}"/>\n'


def fig_stand(x, y, h, body, head=CREAM, tilt=0):
    """立ち姿。(x,y)=足元中心, h=身長。"""
    r = h * 0.16
    w = h * 0.42
    parts = f'<g transform="translate({x},{y}) rotate({tilt})">'
    parts += f'<path d="M{-w/2},0 L{-w/2},{-h+2.1*r} Q{-w/2},{-h+1.2*r} 0,{-h+1.2*r} Q{w/2},{-h+1.2*r} {w/2},{-h+2.1*r} L{w/2},0 Z" fill="{body}"/>'
    parts += f'<circle cx="0" cy="{-h+0.55*r}" r="{r}" fill="{head}"/>'
    parts += '</g>\n'
    return parts


def card_001():
    """今: 目の前の果実に手を伸ばす人。地平線に嵐と高潮。"""
    s = bg()
    # 地平線の嵐(左奥)
    s += f'<rect x="0" y="330" width="800" height="270" fill="{WASHI_D}"/>\n'
    s += f'<path d="M0,340 Q120,300 260,338 L260,600 L0,600 Z" fill="{TEAL}" opacity="0.25"/>\n'
    s += f'<path d="M0,362 Q100,330 230,360 L230,600 L0,600 Z" fill="{TEAL}" opacity="0.35"/>\n'
    for i, (cx, cy, rx) in enumerate([(90, 260, 80), (170, 230, 95), (60, 205, 65)]):
        s += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{rx*0.55}" fill="{AI_M}" opacity="{0.75-0.1*i}"/>\n'
    s += f'<path d="M120,300 L100,345 L118,345 L96,395" stroke="{GOLD}" stroke-width="6" fill="none" stroke-linecap="round"/>\n'
    # 地面(手前の丘)
    s += f'<path d="M0,600 L0,480 Q400,420 800,470 L800,600 Z" fill="{TEAL}" opacity="0.5"/>\n'
    # 木と果実(右)
    s += f'<path d="M620,470 Q612,360 628,300" stroke="{AI}" stroke-width="16" fill="none" stroke-linecap="round"/>\n'
    s += f'<ellipse cx="640" cy="255" rx="120" ry="85" fill="{TEAL_L}"/>\n'
    s += f'<ellipse cx="700" cy="300" rx="80" ry="55" fill="{TEAL}"/>\n'
    s += f'<line x1="565" y1="290" x2="560" y2="318" stroke="{AI}" stroke-width="5"/>\n'
    s += f'<circle cx="560" cy="336" r="20" fill="{GOLD}"/>\n'
    s += f'<circle cx="553" cy="329" r="6" fill="{GOLD_L}"/>\n'
    # 人(中央左・右腕を果実へ)
    s += fig_stand(440, 505, 160, DAWN, tilt=6)
    s += f'<path d="M470,395 Q515,360 542,342" stroke="{DAWN}" stroke-width="17" fill="none" stroke-linecap="round"/>\n'
    return s


def card_002():
    """惜: 包みを抱きしめる人と、通り過ぎる金の鳥。"""
    s = bg()
    s += f'<path d="M0,600 L0,470 Q400,430 800,475 L800,600 Z" fill="{WASHI_D}"/>\n'
    s += f'<circle cx="640" cy="150" r="90" fill="{GOLD}" opacity="0.12"/>\n'
    # 人(中央・前かがみで包みを抱く)
    s += f'<g transform="translate(370,505) rotate(-4)">'
    s += f'<path d="M-45,0 L-45,-150 Q-45,-190 0,-190 Q45,-190 45,-150 L45,0 Z" fill="{AI}"/>'
    s += f'<circle cx="8" cy="-205" r="30" fill="{CREAM}"/>'
    s += f'<path d="M-14,-208 Q-8,-202 -2,-208" stroke="{AI}" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
    s += f'<path d="M12,-208 Q18,-202 24,-208" stroke="{AI}" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
    s += f'<circle cx="14" cy="-120" r="46" fill="#a9803e"/>'
    s += f'<path d="M-6,-140 L34,-100 M-6,-100 L34,-140" stroke="{GOLD_L}" stroke-width="6" stroke-linecap="round"/>'
    s += f'<path d="M-45,-150 Q-14,-108 14,-160 M45,-150 Q40,-92 -10,-92" stroke="{AI}" stroke-width="18" fill="none" stroke-linecap="round"/>'
    s += '</g>\n'
    # 金の鳥(右上へ)
    s += f'<g transform="translate(590,200) rotate(-12)">'
    s += f'<ellipse cx="0" cy="0" rx="42" ry="20" fill="{GOLD}"/>'
    s += f'<path d="M-8,-6 Q-30,-42 8,-34 Q2,-16 -8,-6 Z" fill="{GOLD_L}"/>'
    s += f'<path d="M38,-4 L62,-14 L58,4 Z" fill="{GOLD}"/>'
    s += f'<circle cx="-32" cy="-6" r="11" fill="{GOLD}"/>'
    s += '</g>\n'
    for d in ['M470,250 Q520,225 560,222', 'M455,290 Q515,268 552,262']:
        s += f'<path d="{d}" stroke="{GOLD}" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.55"/>\n'
    return s


def card_003():
    """据: 踏み固められた道と、光へ向かう脇道。"""
    s = bg()
    s += f'<rect x="0" y="300" width="800" height="300" fill="{TEAL}" opacity="0.35"/>\n'
    s += f'<rect x="0" y="300" width="800" height="16" fill="{TEAL}" opacity="0.25"/>\n'
    # 脇道(右へ、光へ)
    s += f'<circle cx="690" cy="270" r="70" fill="{GOLD}" opacity="0.8"/>\n'
    s += f'<circle cx="690" cy="270" r="105" fill="{GOLD}" opacity="0.25"/>\n'
    s += f'<path d="M415,600 Q520,430 660,315 L695,330 Q560,455 495,600 Z" fill="{GOLD_L}" opacity="0.55"/>\n'
    # 本道(深い溝)
    s += f'<path d="M300,600 Q330,430 372,308 L442,308 Q420,440 470,600 Z" fill="#8b6b4f"/>\n'
    s += f'<path d="M330,600 Q352,440 385,315 L428,315 Q412,445 442,600 Z" fill="#6f5138"/>\n'
    for i in range(6):
        y = 560 - i * 44
        w = 15 - i * 1.6
        s += f'<ellipse cx="{372+i*4}" cy="{y}" rx="{w*0.55}" ry="{w}" fill="{AI}" opacity="0.5"/>\n'
        s += f'<ellipse cx="{402+i*2}" cy="{y-20}" rx="{w*0.55}" ry="{w}" fill="{AI}" opacity="0.5"/>\n'
    # 歩く人(本道の中程・下を向く)
    s += fig_stand(398, 400, 120, AI, tilt=3)
    return s


def card_004():
    """顔: 焚き火を囲む輪。外は闇に溶ける影。"""
    s = bg(AI)
    # 外周の影(薄い)
    import math
    for k, (rr, n, op) in enumerate([(315, 16, 0.14), (255, 12, 0.22)]):
        for i in range(n):
            a = (i / n) * 2 * math.pi + k
            x = 400 + rr * math.cos(a)
            y = 340 + rr * 0.62 * math.sin(a)
            h = 54 - k * 6
            s += f'<g opacity="{op}">' + fig_stand(x, y + h / 2, h, "#5a628c", head="#5a628c") + '</g>'
    # 火の明かり
    s += f'<ellipse cx="400" cy="352" rx="235" ry="150" fill="{GOLD}" opacity="0.10"/>\n'
    s += f'<ellipse cx="400" cy="352" rx="160" ry="102" fill="{GOLD}" opacity="0.14"/>\n'
    # 輪になって座る人々(12人)
    for i in range(12):
        a = (i / 12) * 2 * math.pi + 0.26
        x = 400 + 128 * math.cos(a)
        y = 345 + 82 * math.sin(a)
        warm = DAWN if i % 3 else GOLD
        s += fig_stand(x, y + 30, 62, warm, head=CREAM)
    # 焚き火
    s += f'<ellipse cx="400" cy="368" rx="34" ry="10" fill="#3a2c20"/>\n'
    s += f'<path d="M400,304 Q424,330 412,356 Q406,366 400,366 Q394,366 388,356 Q376,330 400,304 Z" fill="{DAWN}"/>\n'
    s += f'<path d="M400,322 Q412,338 406,354 Q400,362 394,354 Q388,338 400,322 Z" fill="{GOLD}"/>\n'
    return s


def card_005():
    """数: 手前の一人の子と、点に溶ける群衆。"""
    s = bg()
    s += f'<rect x="0" y="250" width="800" height="350" fill="{WASHI_D}"/>\n'
    # 群衆→点(奥ほど小さく薄く)
    import random
    random.seed(5)
    for row in range(9):
        y = 268 + row * 34
        n = 26 - row * 2
        r = 3.2 + row * 1.5
        op = 0.22 + row * 0.055
        for i in range(n):
            x = 40 + (720 / max(n - 1, 1)) * i + random.uniform(-9, 9)
            if row >= 6 and 90 < x < 320:
                continue  # 子どもの立ち位置を空ける
            s += f'<circle cx="{x:.0f}" cy="{y}" r="{r:.1f}" fill="{AI}" opacity="{op:.2f}"/>\n'
    # 手前の子ども(左)
    s += f'<g transform="translate(200,545)">'
    s += f'<path d="M-52,0 L-52,-165 Q-52,-210 0,-210 Q52,-210 52,-165 L52,0 Z" fill="{DAWN}"/>'
    s += f'<circle cx="0" cy="-232" r="40" fill="{CREAM}"/>'
    s += f'<path d="M-40,-252 Q0,-286 40,-252 L40,-238 Q0,-262 -40,-238 Z" fill="{AI}"/>'
    s += f'<path d="M52,-150 Q80,-120 74,-86" stroke="{DAWN}" stroke-width="20" fill="none" stroke-linecap="round"/>'
    s += '</g>\n'
    return s


def card_006():
    """共: 水位の下がった湖と、網を引く小舟。"""
    s = bg()
    # 干上がった岸(旧水位の輪)
    s += f'<ellipse cx="400" cy="360" rx="360" ry="185" fill="#cbb98f"/>\n'
    s += f'<ellipse cx="400" cy="368" rx="300" ry="150" fill="#b7a276"/>\n'
    # いまの水面
    s += f'<ellipse cx="400" cy="375" rx="250" ry="120" fill="{TEAL}"/>\n'
    s += f'<ellipse cx="400" cy="375" rx="250" ry="120" fill="{TEAL_L}" opacity="0.3"/>\n'
    # 魚(わずか)
    s += f'<path d="M375,392 Q390,384 402,392 Q390,400 375,392 Z M402,392 L412,386 L412,398 Z" fill="{GOLD}" opacity="0.85"/>\n'
    # 小舟と網(6艘)
    boats = [(215, 330, 1), (400, 288, 1), (575, 330, -1), (250, 430, 1), (545, 435, -1), (400, 468, 1)]
    for bx, by, flip in boats:
        s += f'<g transform="translate({bx},{by}) scale({flip},1)">'
        s += f'<path d="M-52,0 Q0,26 52,0 L38,16 Q0,34 -38,16 Z" fill="{AI}"/>'
        s += fig_stand(-8, 4, 52, DAWN)
        s += f'<path d="M6,-24 Q40,-6 58,26" stroke="{AI}" stroke-width="5" fill="none"/>'
        s += f'<path d="M58,26 q-8,18 8,30 q16,-8 10,-28 Z" fill="none" stroke="{AI}" stroke-width="3.5"/>'
        s += f'<path d="M52,36 l18,10 M56,46 l14,-6" stroke="{AI}" stroke-width="2.5"/>'
        s += '</g>\n'
    return s


def card_007():
    """垣: 生け垣をはさむ、よく似た二つの群れ。"""
    s = bg()
    s += f'<path d="M0,600 L0,455 Q400,425 800,455 L800,600 Z" fill="{WASHI_D}"/>\n'
    # 生け垣(中央)
    s += f'<rect x="384" y="330" width="32" height="180" fill="#7a6a45"/>\n'
    for i, (cx, cy, r) in enumerate([(400, 315, 52), (400, 268, 42), (368, 340, 34), (432, 340, 34)]):
        s += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{TEAL}"/>\n'
        s += f'<circle cx="{cx-8}" cy="{cy-8}" r="{r*0.55}" fill="{TEAL_L}" opacity="0.5"/>\n'
    # 左の群れ(暖色)・右の群れ(寒色) — 同じ配置
    for side, colors in [(-1, (DAWN, GOLD, DAWN)), (1, (AI, TEAL, AI_M))]:
        for i, c in enumerate(colors):
            x = 400 + side * (135 + i * 85)
            h = 150 - i * 14
            s += fig_stand(x, 520, h, c, tilt=side * -3)
    return s


def card_008():
    """奪: 一つのパンを引き合う二人。背後に実る麦畑。"""
    s = bg()
    # 麦畑
    s += f'<rect x="0" y="315" width="800" height="130" fill="{GOLD}" opacity="0.30"/>\n'
    import random
    random.seed(8)
    for i in range(46):
        x = 12 + i * 17.3 + random.uniform(-4, 4)
        h = random.uniform(52, 74)
        s += f'<path d="M{x:.0f},440 L{x:.0f},{440-h:.0f}" stroke="{GOLD}" stroke-width="3.4" opacity="0.75"/>\n'
        s += f'<ellipse cx="{x:.0f}" cy="{440-h-9:.0f}" rx="5.5" ry="13" fill="{GOLD}"/>\n'
    s += f'<path d="M0,600 L0,452 Q400,430 800,452 L800,600 Z" fill="{WASHI_D}"/>\n'
    # 引き合う二人(後傾)
    for side, c in [(-1, AI), (1, DAWN)]:
        x = 400 + side * 165
        s += f'<g transform="translate({x},540) rotate({side*-14})">'
        s += f'<path d="M-38,0 L-38,-130 Q-38,-165 0,-165 Q38,-165 38,-130 L38,0 Z" fill="{c}"/>'
        s += f'<circle cx="{-side*6}" cy="-182" r="27" fill="{CREAM}"/>'
        s += '</g>\n'
        s += f'<path d="M{400+side*140},420 Q{400+side*70},408 {400+side*38},414" stroke="{c}" stroke-width="16" fill="none" stroke-linecap="round"/>\n'
    # パン(中央)
    s += f'<ellipse cx="400" cy="416" rx="52" ry="30" fill="#c98f4b"/>\n'
    s += f'<path d="M368,406 Q400,394 432,406" stroke="#a9713a" stroke-width="5" fill="none"/>\n'
    s += f'<path d="M362,428 l-10,7 M438,428 l10,7" stroke="{AI}" stroke-width="3.5" opacity="0.5"/>\n'
    return s


def card_009():
    """較: 高さの違うはしごと、上ばかり見る人々。"""
    s = bg()
    s += f'<path d="M0,600 L0,505 Q200,472 420,498 Q640,522 800,492 L800,600 Z" fill="{TEAL}" opacity="0.4"/>\n'
    ladders = [(140, 250, DAWN), (330, 350, AI), (530, 440, GOLD), (700, 190, TEAL)]
    for x, h, c in ladders:
        top = 540 - h
        s += f'<line x1="{x-26}" y1="540" x2="{x-26}" y2="{top}" stroke="{AI_M}" stroke-width="8"/>\n'
        s += f'<line x1="{x+26}" y1="540" x2="{x+26}" y2="{top}" stroke="{AI_M}" stroke-width="8"/>\n'
        n = max(3, int(h / 46))
        for i in range(n):
            y = 540 - (h / n) * (i + 0.5)
            s += f'<line x1="{x-26}" y1="{y:.0f}" x2="{x+26}" y2="{y:.0f}" stroke="{AI_M}" stroke-width="6"/>\n'
        # 上を見上げる人(はしご中程)
        py = 540 - h * 0.52
        s += f'<g transform="translate({x},{py}) rotate(-8)">'
        s += f'<path d="M-20,0 L-20,-64 Q-20,-84 0,-84 Q20,-84 20,-64 L20,0 Z" fill="{c}"/>'
        s += f'<circle cx="10" cy="-96" r="15" fill="{CREAM}"/>'
        s += '</g>\n'
        s += f'<path d="M{x+18},{py-100} q14,-12 24,-24" stroke="{c}" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.6"/>\n'
    return s


def card_010():
    """信: 暗い壁の小さな窓から、風景の一片だけを見る人。"""
    s = bg()
    # 壁(ほぼ全面)
    s += f'<rect x="0" y="0" width="800" height="600" fill="{AI}"/>\n'
    s += f'<rect x="0" y="0" width="800" height="600" fill="{AI_M}" opacity="0.25"/>\n'
    # 窓(そこだけ風景が見える)
    s += f'<g><rect x="470" y="150" width="150" height="120" rx="8" fill="{WASHI}"/>'
    s += f'<circle cx="588" cy="182" r="20" fill="{GOLD}"/>'
    s += f'<path d="M470,242 Q520,208 560,236 Q590,214 620,232 L620,270 L470,270 Z" fill="{TEAL}"/>'
    s += f'<path d="M470,256 Q530,236 620,252 L620,270 L470,270 Z" fill="{TEAL_L}" opacity="0.7"/></g>\n'
    s += f'<rect x="470" y="150" width="150" height="120" rx="8" fill="none" stroke="{GOLD}" stroke-width="6"/>\n'
    s += f'<rect x="470" y="150" width="150" height="120" rx="8" fill="{GOLD}" opacity="0.08"/>\n'
    # 窓明かりのこぼれ
    s += f'<path d="M470,270 L400,600 L700,600 L620,270 Z" fill="{GOLD}" opacity="0.07"/>\n'
    # 見る人(後ろ姿・窓に向く)
    s += f'<g transform="translate(540,600)">'
    s += f'<path d="M-52,0 L-52,-185 Q-52,-232 0,-232 Q52,-232 52,-185 L52,0 Z" fill="#3a4066"/>'
    s += f'<circle cx="0" cy="-258" r="36" fill="#2a2f4e"/>'
    s += '</g>\n'
    return s


def card_011():
    """空: 円卓を囲み、同じ仮面を掲げる人々。"""
    s = bg()
    import math
    # 卓
    s += f'<ellipse cx="400" cy="392" rx="225" ry="95" fill="#c9b183"/>\n'
    s += f'<ellipse cx="400" cy="380" rx="225" ry="95" fill="#dcc79b"/>\n'
    # 囲む6人+仮面
    cols = [AI, TEAL, AI_M, DAWN, AI, TEAL]
    for i in range(6):
        a = (i / 6) * 2 * math.pi + math.pi / 6
        x = 400 + 295 * math.cos(a)
        y = 372 + 168 * math.sin(a)
        sc = 0.82 + 0.3 * (math.sin(a) * 0.5 + 0.5)
        s += f'<g transform="translate({x:.0f},{y:.0f}) scale({sc:.2f})">'
        s += f'<path d="M-40,60 L-40,-70 Q-40,-105 0,-105 Q40,-105 40,-70 L40,60 Z" fill="{cols[i]}"/>'
        s += f'<circle cx="0" cy="-124" r="27" fill="{CREAM}"/>'
        # 掲げた仮面(顔の少し手前=下方にずらす)
        s += f'<path d="M40,-70 Q66,-92 52,-118" stroke="{cols[i]}" stroke-width="13" fill="none" stroke-linecap="round"/>'
        s += f'<g transform="translate(52,-132) rotate(8)">'
        s += f'<ellipse cx="0" cy="0" rx="21" ry="27" fill="{WASHI}" stroke="{GOLD}" stroke-width="3"/>'
        s += f'<path d="M-9,-4 Q-5,-8 -1,-4 M3,-4 Q7,-8 11,-4" stroke="{AI}" stroke-width="2.4" fill="none"/>'
        s += f'<path d="M-8,10 Q1,15 10,10" stroke="{AI}" stroke-width="2.4" fill="none"/>'
        s += '</g></g>\n'
    return s


def card_012():
    """従: 大きな影へ向かう列と、一人だけ振り返る人。"""
    s = bg()
    s += f'<path d="M0,600 L0,470 Q300,440 560,452 Q700,428 800,368 L800,600 Z" fill="{TEAL}" opacity="0.35"/>\n'
    # 丘の上の大きな影
    s += f'<path d="M800,368 Q740,392 690,388 L690,600 L800,600 Z" fill="{TEAL}" opacity="0.2"/>\n'
    s += f'<g transform="translate(716,404)">'
    s += f'<path d="M-58,0 L-58,-215 Q-58,-272 0,-272 Q58,-272 58,-215 L58,0 Z" fill="{AI}"/>'
    s += f'<circle cx="0" cy="-302" r="42" fill="{AI}"/>'
    s += '</g>\n'
    # 影へ向かう列(2列)
    for row, (y0, sc, op) in enumerate([(452, 0.72, 0.75), (516, 1.0, 1.0)]):
        for i in range(5):
            x = 80 + i * 118 + row * 40
            c = AI_M if (i + row) % 2 else TEAL
            s += f'<g opacity="{op}" transform="translate({x},{y0}) scale({sc})">'
            s += f'<path d="M-24,0 L-24,-80 Q-24,-104 0,-104 Q24,-104 24,-80 L24,0 Z" fill="{c}"/>'
            s += f'<circle cx="7" cy="-118" r="18" fill="{CREAM}"/>'
            s += '</g>\n'
    # 振り返る一人(逆向き・暖色)
    s += f'<g transform="translate(196,516)">'
    s += f'<path d="M-24,0 L-24,-80 Q-24,-104 0,-104 Q24,-104 24,-80 L24,0 Z" fill="{DAWN}"/>'
    s += f'<circle cx="-9" cy="-118" r="18" fill="{CREAM}"/>'
    s += '</g>\n'
    return s


CARDS = {
    "001-ima": card_001, "002-oshimi": card_002, "003-sue": card_003,
    "004-kao": card_004, "005-kazu": card_005, "006-tomo": card_006,
    "007-kaki": card_007, "008-ubai": card_008, "009-kurabe": card_009,
    "010-shin": card_010, "011-kuuki": card_011, "012-shitagai": card_012,
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in CARDS.items():
        svg = HEAD + GRAIN + fn() + TAIL
        path = os.path.join(OUT, name + ".svg")
        with open(path, "w") as f:
            f.write(svg)
        print("✏️ ", path, f"({len(svg)//1024}KB)")

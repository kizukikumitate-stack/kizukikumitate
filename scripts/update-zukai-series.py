#!/usr/bin/env python3
"""図解シリーズの「シリーズ帯」（番号つき相互リンク）を各ページに生成する。

正は下の SERIES（番号順）。図解を足すときは SERIES に1行足して実行するだけで、
全ページの帯に新しい回が並び、前後リンクも張り替わる。
前後リンクは周回する（最後の回の「次」は1へ、1の「前」は最後の回へ）。
各ページの <!-- ZUKAI-SERIES START --> 〜 <!-- ZUKAI-SERIES END --> の中身は生成物なので
手で書き換えないこと。初回は <!-- KAIYU START --> の直前に差し込む。

冒頭の紹介カード（全回を並べ、いまの回に印を付ける）も同じ SERIES から生成する。
各ページの <!-- ZUKAI-INTRO START --> 〜 <!-- ZUKAI-INTRO END --> が生成物。置き場所はページごとに
違うので、新しい回を作るときは冒頭の好きな位置にこの2行のマーカーを置いてから実行する
（マーカーが無いページは --check で失敗する）。

  python3 scripts/update-zukai-series.py          生成
  python3 scripts/update-zukai-series.py --check  差分があれば exit 1
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERIES = [
    ("ima-hitsuyona-gakushu.html", "今、この社会に必要な学習とは？", "社会の加速に組織が追いつけない構造を眺め、これから必要になる学び方を考えます。"),
    ("minshushugi-kyoiku-rekishi.html", "日本の民主主義教育の歴史", "学校が民主主義をどう教えてきたのかを、制度と、変わりにくい土台の二層でたどります。"),
    ("minshushugi-kyoiku-roadmap.html", "日本の民主主義教育を広げるロードマップ", "学校、職場、地域、家庭。学ぶ場を、誰が、誰のお金で、誰に届けるのかを描きます。"),
    ("taiwa-towa.html", "対話とは何であって、何でないのか", "対話を討論や雑談と分け、6つの動きと3つの難所に分解して、どこに投資するかを考えます。"),
    ("shain-kyoiku-kikai.html", "社員が求めている教育機会", "求めるものと届くもののずれ、介入のタイミング、投資の返り方を図と計算機で確かめます。"),
    ("tou-chikara.html", "問う力とは何か", "疑問が生まれる2つの条件、頭の問いと身体の問い、世界の鍛え方を図で整理します。"),
]
START, END = "<!-- ZUKAI-SERIES START -->", "<!-- ZUKAI-SERIES END -->"
# 色はリテラル。ページごとに var() の値が違うため（シリーズ1は独自パレット）。
CSS = """<style>
.zsn{background:#14191E;color:#F6F5F0;font-family:"Noto Sans JP","Hiragino Kaku Gothic ProN",system-ui,sans-serif;line-height:1.7;padding:72px 24px;box-sizing:border-box}
.zsn *{box-sizing:border-box}
.zsn .zsn-in{max-width:1008px;margin:0 auto;display:flex;flex-direction:column;align-items:stretch;gap:22px}
.zsn .zsn-h{margin:0;display:flex;justify-content:space-between;align-items:baseline;gap:16px;font-weight:900;font-size:20px;letter-spacing:.12em;color:#F5C542}
.zsn .zsn-h a{font-size:15px;letter-spacing:0;color:#F6F5F0}
.zsn .zsn-g{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.zsn .zsn-c{display:flex;flex-direction:column;align-items:stretch;gap:8px;background:#222A32;color:#F6F5F0;border-radius:14px;padding:22px;text-decoration:none;border:3px solid transparent}
.zsn a.zsn-c:hover{border-color:#F5C542;color:#F6F5F0}
.zsn .zsn-c.cur{background:#F5C542;color:#14191E}
.zsn .zsn-n{font-weight:900;font-size:40px;line-height:1;color:#F5C542}
.zsn .zsn-c.cur .zsn-n{color:#14191E}
.zsn .zsn-t{font-weight:900;font-size:17.5px;line-height:1.45;word-break:auto-phrase;line-break:strict;text-wrap:balance;hanging-punctuation:allow-end}
.zsn .zsn-d{font-size:14.5px;line-height:1.7}
.zsn .zsn-pn{margin:0;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-weight:700;font-size:16px}
.zsn .zsn-pn a{color:#F5C542;text-decoration:none;padding:10px 0;min-height:44px}
.zsn .zsn-pn a:hover{text-decoration:underline}
@media (max-width:1180px){
.zsn .zsn-g{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media (max-width:760px){
.zsn{padding:52px 22px}
.zsn .zsn-g{grid-template-columns:minmax(0,1fr);gap:12px}
.zsn .zsn-t{font-size:18px}
}
</style>"""


ISTART, IEND = "<!-- ZUKAI-INTRO START -->", "<!-- ZUKAI-INTRO END -->"
# 冒頭の紹介カード。地色の違う区画（黄・水色・濃紺・図解1の独自配色）に置くので色はリテラル。
ICSS = """<style>
.zin{display:flex;flex-direction:column;align-items:stretch;gap:12px;font-family:"Noto Sans JP","Hiragino Kaku Gothic ProN",system-ui,sans-serif;line-height:1.6;box-sizing:border-box}
.zin *{box-sizing:border-box}
.zin .zin-h{font-weight:900;font-size:15px;letter-spacing:.12em;text-align:left}
.zin .zin-g{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.zin .zin-c{display:flex;flex-direction:column;align-items:stretch;gap:6px;background:#FFFFFF;color:#14191E;border-radius:14px;padding:18px 20px;text-decoration:none;border:3px solid transparent;text-align:left}
.zin a.zin-c:hover{border-color:#1B4FA8;color:#14191E}
.zin .zin-c.cur{background:#14191E;color:#F6F5F0;border-color:#F5C542}
.zin .zin-n{font-weight:900;font-size:13px;letter-spacing:.1em;color:#1B4FA8}
.zin .zin-c.cur .zin-n{color:#F5C542}
.zin .zin-t{font-weight:900;font-size:18px;line-height:1.45;word-break:auto-phrase;line-break:strict;text-wrap:balance;hanging-punctuation:allow-end}
@media (max-width:760px){
.zin .zin-g{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.zin .zin-c{padding:14px}
.zin .zin-t{font-size:15px}
}
</style>"""


def intro(cur: int) -> str:
    cards = []
    for i, (path, title, _desc) in enumerate(SERIES):
        if i == cur:
            cards.append(f'<div class="zin-c cur" aria-current="page"><span class="zin-n">図解 {i + 1}　この回</span><span class="zin-t">{title}</span></div>')
        else:
            cards.append(f'<a class="zin-c" href="{path}"><span class="zin-n">図解 {i + 1}</span><span class="zin-t">{title}</span></a>')
    return "\n".join([
        ISTART,
        '<div class="zin" role="group" aria-label="図解シリーズの全回">',
        ICSS,
        f'<div class="zin-h">図解シリーズ　全{len(SERIES)}回</div>',
        '<div class="zin-g">',
        *cards,
        "</div>",
        "</div>",
        IEND,
    ])


def block(cur: int) -> str:
    cards = []
    for i, (path, title, desc) in enumerate(SERIES):
        n = i + 1
        inner = f'<span class="zsn-n">{n}</span><span class="zsn-t">{title}</span>'
        if i == cur:
            cards.append(f'<div class="zsn-c cur" aria-current="page">{inner}<span class="zsn-d">いま読んでいるページです。</span></div>')
        else:
            cards.append(f'<a class="zsn-c" href="{path}">{inner}<span class="zsn-d">{desc}</span></a>')
    # 前後リンクは周回する：1の「前」は最後の回、最後の回の「次」は1。
    last = len(SERIES) - 1
    p, n = (cur - 1) % len(SERIES), (cur + 1) % len(SERIES)
    pl = "最後の図解" if cur == 0 else "前の図解"
    nl = "最初の図解に戻る" if cur == last else "次の図解"
    pn = [
        f'<a href="{SERIES[p][0]}">← {pl}（{p + 1}）{SERIES[p][1]}</a>',
        f'<a href="{SERIES[n][0]}">{nl}（{n + 1}）{SERIES[n][1]} →</a>',
    ]
    return "\n".join([
        START,
        '<section class="zsn" aria-label="図解シリーズ">',
        CSS,
        '<div class="zsn-in">',
        '<p class="zsn-h"><span>図解シリーズ</span><a href="zukai-series.html">一覧を見る</a></p>',
        '<div class="zsn-g">',
        *cards,
        "</div>",
        f'<p class="zsn-pn">{"".join(pn)}</p>',
        "</div>",
        "</section>",
        END,
    ])


def main() -> int:
    check = "--check" in sys.argv
    dirty = []
    for i, (path, _, _) in enumerate(SERIES):
        f = ROOT / path
        s = f.read_text(encoding="utf-8")
        b = block(i)
        if START in s:
            new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _m: b, s, count=1, flags=re.S)
        else:
            anchor = "<!-- KAIYU START -->"
            if s.count(anchor) != 1:
                print(f"❌ {path}: 差し込み位置（{anchor}）が見つかりません")
                return 1
            new = s.replace(anchor, b + "\n\n" + anchor)
        if ISTART in new:
            ib = intro(i)
            new = re.sub(re.escape(ISTART) + r".*?" + re.escape(IEND), lambda _m: ib, new, count=1, flags=re.S)
        else:
            print(f"❌ {path}: 冒頭の紹介カードのマーカー（{ISTART}）がありません")
            return 1
        if new != s:
            dirty.append(path)
            if not check:
                f.write_text(new, encoding="utf-8")
    if check and dirty:
        print("❌ シリーズ帯が古いページ:", ", ".join(dirty))
        return 1
    print("✅ 図解シリーズ帯:", "更新 " + ", ".join(dirty) if dirty else "変更なし")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""図解シリーズの「シリーズ帯」（番号つき相互リンク）を各ページに生成する。

正は下の SERIES（番号順）。図解を足すときは SERIES に1行足して実行するだけで、
全ページの帯に新しい回が並び、前後リンクも張り替わる。
各ページの <!-- ZUKAI-SERIES START --> 〜 <!-- ZUKAI-SERIES END --> の中身は生成物なので
手で書き換えないこと。初回は <!-- KAIYU START --> の直前に差し込む。

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
]
START, END = "<!-- ZUKAI-SERIES START -->", "<!-- ZUKAI-SERIES END -->"
# 色はリテラル。ページごとに var() の値が違うため（シリーズ1は独自パレット）。
CSS = """<style>
.zsn{background:#14191E;color:#F6F5F0;font-family:"Noto Sans JP","Hiragino Kaku Gothic ProN",system-ui,sans-serif;line-height:1.7;padding:72px 24px;box-sizing:border-box}
.zsn *{box-sizing:border-box}
.zsn .zsn-in{max-width:1008px;margin:0 auto;display:flex;flex-direction:column;align-items:stretch;gap:22px}
.zsn .zsn-h{margin:0;display:flex;justify-content:space-between;align-items:baseline;gap:16px;font-weight:900;font-size:20px;letter-spacing:.12em;color:#F5C542}
.zsn .zsn-h a{font-size:15px;letter-spacing:0;color:#F6F5F0}
.zsn .zsn-g{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.zsn .zsn-c{display:flex;flex-direction:column;align-items:stretch;gap:8px;background:#222A32;color:#F6F5F0;border-radius:14px;padding:22px;text-decoration:none;border:3px solid transparent}
.zsn a.zsn-c:hover{border-color:#F5C542;color:#F6F5F0}
.zsn .zsn-c.cur{background:#F5C542;color:#14191E}
.zsn .zsn-n{font-weight:900;font-size:40px;line-height:1;color:#F5C542}
.zsn .zsn-c.cur .zsn-n{color:#14191E}
.zsn .zsn-t{font-weight:900;font-size:19px;line-height:1.45}
.zsn .zsn-d{font-size:14.5px;line-height:1.7}
.zsn .zsn-pn{margin:0;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-weight:700;font-size:16px}
.zsn .zsn-pn a{color:#F5C542;text-decoration:none;padding:10px 0;min-height:44px}
.zsn .zsn-pn a:hover{text-decoration:underline}
@media (max-width:760px){
.zsn{padding:52px 22px}
.zsn .zsn-g{grid-template-columns:minmax(0,1fr);gap:12px}
.zsn .zsn-t{font-size:18px}
}
</style>"""


def block(cur: int) -> str:
    cards = []
    for i, (path, title, desc) in enumerate(SERIES):
        n = i + 1
        inner = f'<span class="zsn-n">{n}</span><span class="zsn-t">{title}</span>'
        if i == cur:
            cards.append(f'<div class="zsn-c cur" aria-current="page">{inner}<span class="zsn-d">いま読んでいるページです。</span></div>')
        else:
            cards.append(f'<a class="zsn-c" href="{path}">{inner}<span class="zsn-d">{desc}</span></a>')
    pn = []
    if cur > 0:
        pn.append(f'<a href="{SERIES[cur - 1][0]}">← 前の図解（{cur}）{SERIES[cur - 1][1]}</a>')
    else:
        pn.append("<span></span>")
    if cur < len(SERIES) - 1:
        pn.append(f'<a href="{SERIES[cur + 1][0]}">次の図解（{cur + 2}）{SERIES[cur + 1][1]} →</a>')
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

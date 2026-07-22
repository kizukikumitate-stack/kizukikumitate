#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界の成功と失敗事例集 ── 稟議用要約PDF（A4一枚もの）ジェネレーター（冪等）

  python3 scripts/gen-jirei-pdf.py            # 4本すべて再生成
  python3 scripts/gen-jirei-pdf.py kenshu     # slug に kenshu を含むものだけ

生成物（リポジトリルート）:
  jirei-series-summary.pdf     … シリーズ紹介の一枚もの（ハブに設置）
  jirei-shotengai-summary.pdf / jirei-kenshu-summary.pdf / jirei-career-summary.pdf

仕組み:
  DATA（このファイル内）→ A4のHTMLを組み立て → .claude/scripts/render-pdf.mjs
  （Playwright Chromium の page.pdf）でPDF化。QRコードは qrcode ライブラリで
  生成し data URI で埋め込む。事例を追加したら DATA に1エントリ足して再実行。

注意: Chromium はサンドボックス内で起動できないことがある（SIGTRAP）。
      失敗したらサンドボックス無効で実行し直すこと。
"""
import base64, io, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RENDER = ROOT / '.claude/scripts/render-pdf.mjs'
BASE_URL = 'https://kizukikumitate.com/'

CAT = {
    'ko':  ('個', '個人の事例', '#2E5E86'),
    'so':  ('組', '組織の事例', '#9A7A22'),
    'sha': ('社', '社会の事例', '#2E7D6B'),
}

DATA = [
 dict(
  slug='jirei-shotengai', no='No.001', cat='sha',
  title='商店街の立て直し',
  subtitle='再開発した街と、アーケードだけ替えた街',
  win_head='成功：高松丸亀町商店街（香川県高松市）',
  win=['1988年の開町400年祭で「この賑わいが100年続くのか」と問い、1990年に再開発委員会を発足。',
       '土地の「所有」と「利用」を分離。地権者は土地を手放さず、まちづくり会社（1998年設立・行政出資5%）と定期借地権契約。',
       '建物はまちづくり会社が所有・運営し、収益を地権者に分配。売上連動の変動地代でリスクも共有。',
       '2006年に最初の街区「丸亀町壱番街」竣工。時間の大半は地権者の合意形成に投じた。'],
  lose_head='失敗：ハード先行のアーケード改修（典型パターン）',
  lose=['補助金の期限に合わせ、アーケードの架け替えを先行。「きれいになれば人が戻る」という見立て。',
        '地権者・店主への説明会は数回のみ。「もう決まったことですから」で進行。',
        '空き店舗の持ち主は「そのまま持っておく」を選び続け、テナント構成は変わらず。',
        '半年で人通りは元の下降線へ。残ったのは立派な屋根と、変わらないシャッター通り。'],
  fork='建物より先に、地権者の対話に時間を使ったか。',
  questions=['自分たちの地域で、いちばん「動かしにくい事情」を抱えているのは誰か。工事の話より先に、どんな対話の場を持てるか。',
             'いま予定している「説明会」は、決まったことを伝える場か。決めるまえに聴く場か。',
             '「手放したくない」と戦わずにすむ仕組み（所有と利用の分離のような発明）は、この現場では何にあたるか。'],
  source='出典：高松丸亀町商店街 公式サイト「再開発について」（www.kame3.jp/redevelopment/）。失敗事例は複数の実例から再構成した匿名の典型パターン。',
 ),
 dict(
  slug='jirei-kenshu', no='No.002', cat='so',
  title='研修の成功と失敗',
  subtitle='行動が変わった研修と、感想文で終わった研修',
  win_head='成功：「転移」を設計した研修',
  win=['受講前に上司と「現場の何を変えるために行くのか」をすり合わせ、自部署の実課題を持ち込む。',
       '研修内では実課題を教材に演習。学びが最初から現場の文脈につながっている。',
       '翌週に上司と実践計画を確認、30日後に実践報告会。事後のフォローまでが研修。',
       '満足度でなく「行動が変わったか」（カークパトリックのレベル3）を測り、翌年度も予算が残る。'],
  lose_head='失敗：感想文で終わった一日研修（典型パターン）',
  lose=['評判のよい外部講師を招いた一日研修。満足度アンケートは5点満点の4.5。',
        '翌朝から通常業務。上司は部下が何を学んだか知らず、職場のやり方は昨日までと同じ。',
        '3ヶ月後、行動は元通り。経営陣の「で、何が変わったの？」に満足度しか出せない。',
        '翌年度、研修予算は削られた。'],
  fork='研修の前後を設計したか、当日だけを設計したか。',
  questions=['次の研修で、受講者の上司は「部下が何を学びに行くか」を知っているか。事前に一往復の会話を仕込めるか。',
             '研修の30日後に「何かが起きる」設計になっているか。',
             '経営陣に問われたとき、満足度以外に出せる数字はあるか。「行動が変わったか」を誰がいつ確かめるか。'],
  source='根拠：Baldwin & Ford (1988) 研修転移レビュー／Kirkpatrick 4段階評価／中原淳ほか『研修開発入門「研修転移」の理論と実践』(2018)。失敗事例は複数の実例から再構成した匿名の典型パターン。',
 ),
 dict(
  slug='jirei-career', no='No.003', cat='ko',
  title='キャリアの転機',
  subtitle='降りて幸せになった人と、しがみついて消耗した人',
  win_head='成功：働きながら軸を増やした転身（楠木新さん）',
  win=['大手生保の会社員として勤めるなか、40代後半にこころの不調で休職を経験。',
       '会社を辞めるのでも競争に戻るのでもなく、勤務の外で取材・執筆というもう一つの軸を育てた。',
       '二足のわらじを十年以上続け、社外の人脈と実績を静かに積み上げた。',
       '定年後は作家・大学教授へ。『定年後』（中公新書）はベストセラーに。'],
  lose_head='失敗：降りられなかった人（典型パターン）',
  lose=['同期トップで昇進を重ね、ものさしは社内の序列ただ一本。家族も趣味も「上がってから」。',
        'ポストオフの内示で、自分が何者か分からなくなる。それでも積み上げた地位が惜しくて辞められない。',
        '健康と眠りが崩れ、名刺の外に自分を語る言葉がない。',
        '退職の日に残ったのは「あんなに頑張ったのに」という言葉だけ。'],
  fork='評価軸を、一本から多本に組み替えられたか。',
  questions=['いまの自分を測っているものさしは何本あるか。会社が無くなっても残るのは何本か。',
             '「上がってから」と後回しにしているものは、本当に上がってからでないとできないか。',
             '今週、社外のものさしに触れる30分をつくれるか。小ささは問題にならない。'],
  source='出典：楠木新『定年後』中公新書(2017)ほか本人の著書・公開インタビュー。失敗事例は複数の実例から再構成した匿名の典型パターン。',
 ),
]

SERIES = dict(
  slug='jirei-series',
  title='世界の成功と失敗事例集',
  subtitle='成功と失敗の分岐点を見極めるケースブック',
  promises=[
    ('約束一：失敗を、成功と同じ棚に置きます', '成功事例だけの棚は、それ自体が一つのバイアス。すべてのテーマで成功と失敗を併記します。'),
    ('約束二：失敗した人を、名指ししません', '成功は実名と出典を明記。失敗は複数の実例から合成した匿名の「典型パターン」として描きます。'),
    ('約束三：犯人ではなく、仕様をさがします', '失敗の原因を個人の資質に求めず、働いていた認知バイアス（苦手）と効いた知恵を図鑑へ逆引きします。'),
  ],
  cases=[
    ('社', '#2E7D6B', 'No.001 商店街の立て直し', '分岐点：建物より先に、地権者の対話に時間を使ったか'),
    ('組', '#9A7A22', 'No.002 研修の成功と失敗', '分岐点：研修の前後を設計したか、当日だけを設計したか'),
    ('個', '#2E5E86', 'No.003 キャリアの転機', '分岐点：評価軸を一本から多本に組み替えられたか'),
  ],
  coming=['学校統廃合の分かれ道（社会）', '1on1の定着（組織）', '離職が止まった会社、止まらなかった会社（組織）', '住民参加のくじ引き民主主義（社会）'],
)

FOOT_NOTE = '本資料は社内検討・会議資料への添付にご利用いただけます（出典表記のままご利用ください）。CC BY-NC-SA 4.0'
CREDIT = 'きづきくみたて工房（森本康仁）／お問い合わせ: y.morimoto@kizukikumitate.com'


def qr_data_uri(url: str) -> str:
    import qrcode
    qr = qrcode.QRCode(border=1, box_size=6)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#26313A', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


CSS = """
@page{size:A4;margin:0;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:210mm;height:297mm;}
body{font-family:'Zen Kaku Gothic New','Hiragino Kaku Gothic ProN',sans-serif;color:#26313A;
 background:#F5F2EA;font-size:9.4pt;line-height:1.7;padding:11mm 12mm 9mm;display:flex;flex-direction:column;}
.serif{font-family:'Shippori Mincho B1','Hiragino Mincho ProN',serif;}
header{display:flex;align-items:center;gap:5mm;border-bottom:2px solid #9E4A33;padding-bottom:3.5mm;margin-bottom:4mm;}
.stamp{width:15mm;height:15mm;border-radius:50%;border:1.2mm solid;display:flex;align-items:center;justify-content:center;
 font-family:'Shippori Mincho B1',serif;font-size:17pt;font-weight:800;background:#fff;flex-shrink:0;}
.h-series{font-size:8pt;letter-spacing:.18em;color:#4E5A63;}
.h-no{font-size:9pt;letter-spacing:.2em;font-weight:700;}
h1{font-family:'Shippori Mincho B1',serif;font-size:19pt;font-weight:800;line-height:1.3;}
.h-sub{font-family:'Shippori Mincho B1',serif;font-size:10pt;color:#4E5A63;margin-top:1mm;}
.cols{display:flex;gap:4mm;margin-bottom:4mm;}
.col{flex:1;background:#fff;border:1px solid #C9C4B4;padding:3.5mm 4mm;}
.col.win{border-top:1.4mm solid #2E7D6B;}
.col.lose{border-top:1.4mm solid #9E4A33;}
.col h2{font-family:'Shippori Mincho B1',serif;font-size:10pt;font-weight:700;margin-bottom:2mm;line-height:1.5;}
.col.win h2{color:#2E7D6B;}
.col.lose h2{color:#9E4A33;}
.col ul{list-style:none;}
.col li{font-size:8.6pt;line-height:1.65;padding-left:3.2mm;position:relative;margin-bottom:1.6mm;}
.col li::before{content:"・";position:absolute;left:0;}
.fork{border:0.7mm solid #9E4A33;background:#fff;text-align:center;padding:4.5mm 6mm 4mm;position:relative;margin:2mm 0 4mm;}
.fork-label{position:absolute;top:-3.2mm;left:50%;transform:translateX(-50%);background:#9E4A33;color:#fff;
 font-family:'Shippori Mincho B1',serif;font-size:8pt;letter-spacing:.24em;padding:0.6mm 5mm;}
.fork p{font-family:'Shippori Mincho B1',serif;font-size:13.5pt;font-weight:800;line-height:1.6;}
.qs{background:#fff;border:1px solid #C9C4B4;padding:3.5mm 4.5mm;margin-bottom:4mm;}
.qs h2{font-family:'Shippori Mincho B1',serif;font-size:10pt;font-weight:700;margin-bottom:2mm;color:#26313A;}
.qs ol{padding-left:5mm;}
.qs li{font-size:8.8pt;line-height:1.7;margin-bottom:1.4mm;}
footer{margin-top:auto;border-top:1px solid #C9C4B4;padding-top:2.5mm;display:flex;gap:5mm;align-items:flex-end;}
.f-text{flex:1;font-size:6.9pt;color:#4E5A63;line-height:1.65;}
.f-qr{flex-shrink:0;text-align:center;font-size:6.5pt;color:#4E5A63;}
.f-qr img{width:17mm;height:17mm;display:block;margin:0 auto 1mm;}
/* series */
.promises{display:flex;gap:3.5mm;margin-bottom:4mm;}
.promise{flex:1;background:#fff;border:1px solid #C9C4B4;border-top:1.2mm solid #9E4A33;padding:3mm 3.5mm;}
.promise h3{font-family:'Shippori Mincho B1',serif;font-size:9pt;font-weight:700;margin-bottom:1.5mm;line-height:1.5;}
.promise p{font-size:8pt;color:#4E5A63;line-height:1.65;}
.caselist{background:#fff;border:1px solid #C9C4B4;padding:3.5mm 4.5mm;margin-bottom:4mm;}
.caselist h2{font-family:'Shippori Mincho B1',serif;font-size:10.5pt;font-weight:700;margin-bottom:2.5mm;}
.crow{display:flex;align-items:center;gap:3mm;padding:2mm 0;border-bottom:1px dashed #C9C4B4;}
.crow:last-of-type{border-bottom:none;}
.cstamp{width:8.5mm;height:8.5mm;border-radius:50%;border:0.7mm solid;display:flex;align-items:center;justify-content:center;
 font-family:'Shippori Mincho B1',serif;font-size:9.5pt;font-weight:800;background:#fff;flex-shrink:0;}
.crow .ct{font-family:'Shippori Mincho B1',serif;font-size:10pt;font-weight:700;}
.crow .cf{font-size:8.2pt;color:#4E5A63;}
.coming{font-size:8pt;color:#4E5A63;line-height:1.8;}
.lead{font-size:9pt;line-height:1.8;margin-bottom:4mm;}
"""


def build_case_html(d: dict) -> str:
    mark, catlabel, color = CAT[d['cat']]
    url = BASE_URL + d['slug'] + '.html'
    win = ''.join(f'<li>{x}</li>' for x in d['win'])
    lose = ''.join(f'<li>{x}</li>' for x in d['lose'])
    qs = ''.join(f'<li>{x}</li>' for x in d['questions'])
    return f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@700;800&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header>
  <span class="stamp" style="color:{color};border-color:{color}">{mark}</span>
  <div>
    <div class="h-series serif">世界の成功と失敗事例集</div>
    <div class="h-no serif" style="color:{color}">{d['no']}【{catlabel[:2]}】</div>
    <h1>{d['title']}</h1>
    <div class="h-sub">─ {d['subtitle']}</div>
  </div>
</header>
<div class="cols">
  <div class="col win"><h2>{d['win_head']}</h2><ul>{win}</ul></div>
  <div class="col lose"><h2>{d['lose_head']}</h2><ul>{lose}</ul></div>
</div>
<div class="fork"><span class="fork-label">分岐点</span><p>{d['fork']}</p></div>
<div class="qs"><h2>自社・自組織に当てはめると（検討事項欄にどうぞ）</h2><ol>{qs}</ol></div>
<footer>
  <div class="f-text">{d['source']}<br>{FOOT_NOTE}<br>{CREDIT}</div>
  <div class="f-qr"><img src="{qr_data_uri(url)}" alt="QR">{url.replace('https://','')}</div>
</footer>
</body></html>"""


def build_series_html(s: dict) -> str:
    url = BASE_URL + 'jirei.html'
    promises = ''.join(f'<div class="promise"><h3>{t}</h3><p>{b}</p></div>' for t, b in s['promises'])
    rows = ''.join(
        f'<div class="crow"><span class="cstamp" style="color:{c};border-color:{c}">{m}</span>'
        f'<div><div class="ct">{t}</div><div class="cf">{f}</div></div></div>'
        for m, c, t, f in s['cases'])
    coming = '／'.join(s['coming'])
    return f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@700;800&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header>
  <span class="stamp" style="color:#9E4A33;border-color:#9E4A33">辻</span>
  <div>
    <div class="h-series serif">A CASEBOOK OF FORKS IN THE ROAD</div>
    <h1>{s['title']}</h1>
    <div class="h-sub">─ {s['subtitle']}</div>
  </div>
</header>
<p class="lead">世に出回る事例は、成功したものばかりです。この事例集は、成功と失敗を必ず併記し、両者を分けた「分岐点」を特定します。そこで働いていた認知バイアス（苦手）と、効いていた知恵を図鑑へ逆引きできるケースブックです。</p>
<div class="promises">{promises}</div>
<div class="caselist"><h2>収蔵事例（第一弾）</h2>{rows}</div>
<div class="qs"><h2>準備中の事例</h2><p class="coming">{coming}</p></div>
<footer>
  <div class="f-text">各事例の詳細・出典は個別ページに明記。失敗事例は複数の実例から再構成した匿名の典型パターンです。<br>{FOOT_NOTE}<br>{CREDIT}</div>
  <div class="f-qr"><img src="{qr_data_uri(url)}" alt="QR">{url.replace('https://','')}</div>
</footer>
</body></html>"""


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else ''
    jobs = []
    for d in DATA:
        if only and only not in d['slug']:
            continue
        jobs.append((d['slug'] + '-summary.pdf', build_case_html(d)))
    if not only or only in 'jirei-series-summary':
        jobs.append(('jirei-series-summary.pdf', build_series_html(SERIES)))
    with tempfile.TemporaryDirectory() as td:
        for name, html in jobs:
            src = Path(td) / (name + '.html')
            src.write_text(html, encoding='utf-8')
            out = ROOT / name
            subprocess.run(['node', str(RENDER), str(src), str(out)], check=True,
                           cwd=str(RENDER.parent))
            print('✓', name)


if __name__ == '__main__':
    main()

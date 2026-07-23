#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界の成功と失敗事例集 ── 稟議用要約PDF（A4一枚もの）ジェネレーター（冪等）

  python3 scripts/gen-jirei-pdf.py            # 全事例＋シリーズ紹介を再生成
  python3 scripts/gen-jirei-pdf.py kenshu     # slug に kenshu を含むものだけ

生成物（リポジトリルート）:
  jirei-series-summary.pdf     … シリーズ紹介の一枚もの（ハブに設置）
  jirei-<slug>-summary.pdf     … 各事例の一枚もの（DATA の件数ぶん）

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
 dict(
  slug='jirei-rinen-sakutei', no='No.004', cat='so',
  title='理念の策定',
  subtitle='社員とつくった理念と、社員に配った理念',
  win_head='成功：11万人との対話からつくったパーパス（ソニー）',
  win=['2018年、就任まもない吉田憲一郎社長が社内ブログで「存在意義を見直したい」と全社員に呼びかけ。',
       '世界約11万人の従業員から意見を集め、約半年の対話を経て2019年1月にパーパスを発表。',
       '発表後の社内調査では、従業員の8割以上がパーパスを肯定的に受け止めたと報じられる。',
       '研究の裏付け：パーパスは「明瞭さ」がミドル層に届いている企業ほど後の業績が高い（ガーテンバーグら2019）。'],
  lose_head='失敗：額縁で終わった理念（典型パターン）',
  lose=['経営企画と外部支援会社が密室で数ヶ月かけて言葉を磨き、役員会は満場一致。',
        '盛大な発表会でカードを配布し、額縁を受付に掲示。ここで施策は「完了」に。',
        '会議の議題も稟議の基準も評価の項目も変わらず、現場の翌朝は昨日と同じ。',
        '1年後、理念を言える社員はまばら。「また何か始まって、終わったね」だけが残った。'],
  fork='理念を、社員とつくったか。社員に、配ったか。',
  questions=['案を「発表」する前に、現場が手を入れられる余地を残しているか。',
             '策定メンバーの名簿に、現場の名前は何人あるか。',
             '発表の日は「完成の日」か「運用初日」か。発表後1年の計画は発表前に決まっているか。'],
  source='出典：日経クロストレンド・Biz/Zineのソニー取材記事／パーソル総合研究所「企業理念と人事制度の浸透に関する定量調査」(2023)／Gartenberg, Prat & Serafeim (2019)。失敗事例は複数の実例から再構成した匿名の典型パターン。',
 ),
 dict(
  slug='jirei-rinen-shinto', no='No.005', cat='so',
  title='理念の浸透',
  subtitle='毎日問いかけた会社と、唱和で終わった会社',
  win_head='成功：クレドを毎日の「問いかけ」に変えたホテル（ザ・リッツ・カールトン）',
  win=['世界中のホテルで毎日短いミーティング「ラインナップ」。クレドの一節を取り上げ対話する。',
       '「あなたはこの一文をどう理解するか」「この場面ならどう動くか」——唱和ではなく問いかけ。',
       'スタッフ一人ひとりに、上司の承認なしに使える2,000ドルまでの決裁権。理念が「実行できる」ように設計。',
       'J&Jも「我が信条」を全社員サーベイで定期的に測定し、部門ごとの改善計画へ。理念が制度の中に住む。'],
  lose_head='失敗：唱和で終わったクレド（典型パターン）',
  lose=['クレドカード全員配布・朝礼の唱和・eラーニング一巡。チェックリストは全て「完了」。',
        '評価面談で語られるのは今期の数字だけ。理念に沿った行動は褒められも測られもしない。',
        '掲示物と評価表が食い違うとき、社員は必ず評価表を信じる。',
        '2年後も唱和は続くが、言葉と日々の判断は別々に暮らす。浸透度を測ったことは一度もない。'],
  fork='理念を日々の判断に接続したか、唱和と掲示で終えたか。',
  questions=['自社の理念を、自分の言葉で語れるか。最後に誰かと理念について「対話」したのはいつか。',
             '理念に沿った行動は、評価・表彰・昇進のどこかで報われる設計か。',
             '浸透の度合いを測っているか。測らないものは、たいてい良くならない。'],
  source='出典：高野登『リッツ・カールトンが大切にするサービスを超える瞬間』／J&J「我が信条」公式ページ／HR総研調査(2013)。失敗事例は複数の実例から再構成した匿名の典型パターン。',
 ),
 dict(
  slug='jirei-purpose', no='No.006', cat='so',
  title='パーパス経営と風土改革',
  subtitle='仕組みまで変えた会社と、言葉だけ替えた会社',
  win_head='成功：対話と手挙げで風土を変えた小売（丸井グループ）',
  win=['2005年就任の青井浩社長が企業理念の明文化と対話の場から着手。ほぼ全社員が対話を経験。',
       '会議・プロジェクト・研修への参加を指名制から「手挙げ制」へ。手挙げ率は85%水準に。',
       '意識調査10年比較：仕事への「期待」46%→80%、「尊重」28%→66%。3年以内離職率20%→11%。',
       'ここまで約15年。手挙げ率という定点観測を毎年数えて開示し続けた。'],
  lose_head='失敗：ポスターで終わった風土改革（典型パターン）',
  lose=['盛大な発表イベント、ブランドムービー、ポスター。風土改革委員会がスローガンを選定。',
        '投資の判断基準も会議の進め方も評価の項目も変わらない。委員会は半年で議題が尽きる。',
        '初年度の熱を「変わった証拠」と数えて早すぎる勝利宣言。',
        '2年目、パーパスはメールの署名にだけ残り、現場の語彙から消えた。'],
  fork='意思決定の仕組みまで変えたか、掲げる言葉だけ替えたか。',
  questions=['パーパスを理由に「やめた事業・断った案件・変えた基準」はあるか。なければまだ言葉の段階。',
             '風土の変化を測る定点観測（意識調査・参加率・手挙げ率）はあるか。',
             '10年単位の覚悟はあるか。1年での結論は、種を蒔いた翌週に畑を諦めるのに似ている。'],
  source='出典：丸井グループ「人的資本経営」開示資料／リクルートワークス研究所の取材記事／コッター『企業変革力』。失敗事例は複数の実例から再構成した匿名の典型パターン。',
 ),
 dict(
  slug='jirei-hyoka', no='No.007', cat='so',
  title='評価制度の改訂',
  subtitle='対話とセットで変えた会社と、制度だけ差し替えた会社',
  win_head='成功：年次評価をやめて対話に置き換えた（アドビ）',
  win=['2012年、年1回の格付け評価を廃止。マネジャー約2,000人が年間約8万時間を評価作業に費やしていた。',
       '置き換えたのは高頻度の対話「チェックイン」。期待のすり合わせ・フィードバック・成長の相談を都度行う。',
       'マネジャーたちから集めた声をもとに設計。評価を「格付けの儀式」から「育成の対話」へ再定義。',
       '「勤め先として勧める」が10ポイント上昇、自発的離職は過去最低水準に。GEも2016年に9ブロックを廃止。'],
  lose_head='失敗：制度だけ差し替えた改訂（典型パターン）',
  lose=['他社の最新事例を研究し精緻な評価シートを設計。全社説明会を開き翌期から一斉切替。',
        'マネジャーに配られたのは分布の目安と締切だけ。面談やフィードバックの訓練はない。',
        '「制度がそうなっているから」の説明で、部下は制度と上司の両方への信頼を失う。目標は静かに低くなる。',
        '3年後、「新制度にも納得感がない」の調査結果を受けて次の改訂プロジェクトが立ち上がる。'],
  fork='評価を育成の対話につくり替えたか、点のつけ方だけ替えたか。',
  questions=['「何点をつけるか」と「誰がどんな対話をするか」、どちらの議論に時間を使っているか。',
             '評価者になるマネジャーに、フィードバックと面談の訓練は用意されているか。',
             '本人が「なぜこの評価か」を説明されて納得できる透明さはあるか。'],
  source='出典：アドビ公式ブログ／HR NOTEほか取材記事／アデコ調査(2018)／高橋伸夫『虚妄の成果主義』。失敗事例は複数の実例から再構成した匿名の典型パターン。',
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
    ('組', '#9A7A22', 'No.004 理念の策定', '分岐点：理念を社員とつくったか、社員に配ったか'),
    ('組', '#9A7A22', 'No.005 理念の浸透', '分岐点：理念を日々の判断に接続したか、唱和と掲示で終えたか'),
    ('組', '#9A7A22', 'No.006 パーパス経営と風土改革', '分岐点：意思決定の仕組みまで変えたか、掲げる言葉だけ替えたか'),
    ('組', '#9A7A22', 'No.007 評価制度の改訂', '分岐点：評価を育成の対話につくり替えたか、点のつけ方だけ替えたか'),
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

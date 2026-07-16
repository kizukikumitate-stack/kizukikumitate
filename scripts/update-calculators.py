#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
未来のリスク計算機シリーズ（6本）の共通パーツを一括で入れる／更新する。

6本は CSS も JS もコピペで共有しているため、共通の文言を1本ずつ手で直すと必ず
どれかが取り残される。このスクリプトが「共通パーツの正」を持ち、冪等に流し込む。

入れているもの:
  1. ソース冒頭のライセンスコメント（シリーズ番号つき）
  2. 大きな数字の隣の「簡易試算」バッジ  ── 数字だけスクショされたときの保険
  3. ※注記の末尾に 出典リンク＋免責  ── 出典は必ず生きているURLだけを書く
  4. ライセンス表記＋版（ver）＋ハブページへの導線

使い方:
    python3 scripts/update-calculators.py            # 反映
    python3 scripts/update-calculators.py --check    # 差分が出るかだけ確認（CI用）

版を上げるとき: VERSION と VERSION_DATE を書き換えて実行し、
risk-calculators.html の変更履歴に1項目足す。
"""
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VERSION = "1.1"
VERSION_DATE = "2026-07-16"
VERSION_DATE_JA = "2026年7月16日"
HUB = "risk-calculators.html"

# 出典はすべて到達確認済みのURLのみ。リンク切れを載せるのは本末転倒なので、
# 追加するときは必ず curl で 200 を確認してから書くこと。
IPSS = '<a href="https://www.ipss.go.jp/pp-zenkoku/j/zenkoku2023/pp_zenkoku2023.asp" target="_blank" rel="noopener">日本の将来推計人口（令和5年推計・出生中位）</a>'
MHLW_VITAL = '<a href="https://www.mhlw.go.jp/toukei/list/81-1a.html" target="_blank" rel="noopener">人口動態統計</a>'
MHLW_LIFE = '<a href="https://www.mhlw.go.jp/toukei/saikin/hw/life/life24/index.html" target="_blank" rel="noopener">簡易生命表</a>'
MHLW_KAIGO = '<a href="https://www.mhlw.go.jp/topics/kaigo/toukei/joukyou.html" target="_blank" rel="noopener">介護保険事業状況報告</a>'
EGOV_SCHOOL = '<a href="https://laws.e-gov.go.jp/law/333AC0000000116" target="_blank" rel="noopener">義務教育標準法</a>'

# ===== 意思決定期限 =====
# 「2038年に問題が起きる」と出すと「まだ12年ある」と読まれる。実際に効くのは
# 「いつまでに決めないと打ち手が間に合わないか」。04（技能承継）は着手デッドラインを
# 最初から持っており、シリーズで最も強い設計だったので、他のページへ横展開する。
#
# path -> (render() 内で「問題の年」を保持している式, 問題の呼び名)
#   04 は既にネイティブの着手デッドラインを持つので対象外。
#   06 は「あなたが85歳になる年」＝個人の話で、組織の打ち手のリードタイムという
#   概念が当てはまらないので対象外。
DEADLINE = {
    "customer-age-timebomb.html":         ("halfYear",           "顧客基盤が半減する"),
    "recruitment-extinction.html":        ("breachYear",         "採用目標を割り込む"),
    "tax-revenue-countdown.html":         ("burdenYear",         "ひとりが負う固定費が1.5倍になる"),
    "school-consolidation-countdown.html": ("sim.touhaigouYear", "統廃合が検討される規模になる"),
}

DEADLINE_CSS = """  /* 意思決定期限。「問題が起きる年」と「決められなくなる年」を並べる */
  .deadline { margin-top: 1.4rem; padding-top: 1.2rem; border-top: 1px solid rgba(250,248,242,0.18); }
  .deadline-head { display: flex; justify-content: space-between; align-items: baseline; gap: 0.6rem; font-size: 0.76rem; opacity: 0.75; margin-bottom: 0.2rem; }
  .deadline-head b { font-family: 'Jost', sans-serif; color: var(--gold); font-size: 0.95rem; opacity: 1; }
  .deadline input[type=range] { width: 100%; accent-color: var(--gold); }
  .deadline-out { font-size: 0.84rem; line-height: 1.95; margin-top: 0.7rem; }
  .deadline-out b { color: var(--gold); }
  .deadline-out b.dl-past { color: var(--dawn); }"""

DEADLINE_HTML = """      <div class="deadline">
        <div class="deadline-head"><span>打ち手が効き始めるまでの年数（あなたの想定）</span><span><b id="leadVal">5</b>年</span></div>
        <input type="range" id="lead" min="1" max="15" step="1" value="5" aria-label="打ち手が効き始めるまでの年数">
        <p class="deadline-out" id="deadlineOut">—</p>
      </div>"""


DL_JS_START = "/* DEADLINE-JS START */"
DL_JS_END = "/* DEADLINE-JS END */"


def deadline_js(problem_label):
    # ★ .replace() は末尾の文字列リテラルにしか掛からないので、全体を括弧で囲むこと
    #   （囲み忘れて PROBLEM が置換されず、そのまま表示されるバグを踏んだ）
    return ("""
""" + DL_JS_START + """
/* ===== 意思決定期限 =====
   「問題が起きる年」だけを出すと「まだ◯年ある」と読まれて先送りされる。
   打ち手が効き始めるまでの年数を引いた「決められなくなる年」を併記する。
   ★リードタイムは利用者の想定であって、計算機が知っている値ではない（＝仮定と明記する） */
let leadYears = 5;
document.getElementById('lead').addEventListener('input', e => { leadYears = Number(e.target.value); render(); });

function renderDeadline(problemYear){
  document.getElementById('lead').value = leadYears;
  document.getElementById('leadVal').textContent = leadYears;
  const el = document.getElementById('deadlineOut');
  if (problemYear === null || problemYear === undefined) {
    el.innerHTML = 'この条件では、PROBLEM年に届きません。いまは時間の余裕がある側です。';
    return;
  }
  // すでに問題が起きている年は「間に合わせる」話にならない。
  // 打ち手が効くまでの年数は、これから何年それが続くかの話になる
  if (problemYear <= START_YEAR) {
    el.innerHTML = '<b class="dl-past">PROBLEM状態には、すでに入っています。</b>'
      + 'いま打ち手を決めても、効き始めるまでに' + leadYears + '年（' + (START_YEAR + leadYears) + '年ごろまで）はこの状態が続く見込みです。'
      + '先に「何を諦め、何を守るか」を決める局面です。'
      + '<a href="./HUB#too-late" style="color:var(--gold)">この状態でできること</a>をまとめています。';
    return;
  }
  const deadline = problemYear - leadYears;
  const rest = deadline - START_YEAR;
  if (rest > 0) {
    el.innerHTML = '問題が起きるのは' + problemYear + '年でも、打ち手が効くまでに' + leadYears + '年かかるなら、'
      + '<b>決められるのはあと' + rest + '年（' + deadline + '年まで）</b>です。';
  } else if (rest === 0) {
    el.innerHTML = '<b>今年が、決められる最後の年です。</b>' + problemYear + '年に間に合わせるには、いま着手する必要があります。';
  } else {
    el.innerHTML = '<b class="dl-past">着手の期限は、すでに' + (-rest) + '年過ぎています。</b>'
      + problemYear + '年に間に合わせるには' + deadline + '年までに始めている必要がありました。'
      + '間に合わせるなら、リードタイムの短い打ち手に変えるしかありません。'
      + '<a href="./HUB#too-late" style="color:var(--gold)">手遅れだったときにできること</a>をまとめています。';
  }
}
""" + DL_JS_END + """
""").replace("PROBLEM", problem_label).replace("HUB", HUB)


# ===== 感度レンジ =====
# 点推定の「2038年」は確定的に読まれる。かといって「2036〜2041年」と幅を出すには
# 不確実性の分布が要るが、それは持っていない（適当な幅を書けば、根拠のない精度を
# 装うことになり、出典の誤りと同じ失敗になる）。
# 代わりに「利用者が入れた主要な数字を±20%動かすと、年が何年動くか」なら、
# 計算で出せて根拠も言える。＝感度分析であって、予測の信頼区間ではない。
#
# path -> (±20%を適用して「問題の年」を返すJS式, 振る入力の呼び名)
SENS = {
    "customer-age-timebomb.html": (
        "m => simulate(shares, newRate * m, newBand, exitAge, shrinkInflow).halfYear",
        "年間の新規顧客の割合"),
    "recruitment-extinction.html": (
        "m => simulate(Object.assign({}, P, { entries: P.entries * m }), futureDecline, competition).breachYear",
        "年間エントリー数"),
    "tax-revenue-countdown.html": (
        # 基準が「ひとりが負う固定費」になったので、振るのは税収ではなく人口の元＝出生数
        "m => simulate(Object.assign({}, P, { births: P.births * m }), birthDecline).burdenYear",
        "年間出生数"),
    "skill-succession-timebomb.html": (
        "m => simulate(holders, retire, Math.max(1, Math.round(handover * m)), succ).lossYear",
        "技の継承にかかる年数"),
    "school-consolidation-countdown.html": (
        "m => simulate(P.births * m, P.decline, P.rate).touhaigouYear",
        "校区の年間出生数"),
    # 06 は「あなたが85歳になる年」＝年齢から決まる確定値で、振る前提がないので対象外
}

SENS_CSS = """  /* 感度レンジ。点推定を確定的に読ませないための、根拠のある幅 */
  .sens { font-size: 0.74rem; line-height: 1.9; opacity: 0.75; margin-top: 0.8rem; }
  .sens b { color: var(--gold); opacity: 1; }"""

SENS_HTML = '      <p class="sens" id="sensOut"></p>'

SENS_JS_START = "/* SENS-JS START */"
SENS_JS_END = "/* SENS-JS END */"


def sens_js(input_label):
    return ("""
""" + SENS_JS_START + """
/* ===== 感度レンジ =====
   「2038年」と1点で出すと確定的に読まれる。かといって信頼区間は出せない
   （不確実性の分布を持っていないので、幅をでっち上げることになる）。
   出せるのは「入力を±20%動かすと年がどう動くか」＝感度分析だけ。予測の幅ではない。 */
function renderSens(f){
  const el = document.getElementById('sensOut');
  let lo, hi;
  try { lo = f(0.8); hi = f(1.2); } catch (e) { el.textContent = ''; return; }
  const ys = [lo, hi].filter(y => y !== null && y !== undefined);
  if (ys.length === 0) {
    el.innerHTML = 'INPUT（あなたが入れた値）を±20％動かしても、この期間内には届きません。';
    return;
  }
  const a = Math.min.apply(null, ys), b = Math.max.apply(null, ys);
  if (ys.length === 1) {
    el.innerHTML = 'INPUT（あなたが入れた値）を±20％動かすと、この年は <b>' + a + '年から「この期間内には届かない」まで</b> 動きます。'
      + '年そのものより、動かせる前提はどれかを見てください。';
  } else if (a === b) {
    el.innerHTML = 'INPUT（あなたが入れた値）を±20％動かしても、この年は <b>' + a + '年のまま</b> です。'
      + 'この結果は、その前提にはあまり左右されていません。効くのは別の前提です。';
  } else {
    el.innerHTML = 'INPUT（あなたが入れた値）を±20％動かすと、この年は <b>' + a + '〜' + b + '年</b> に動きます。'
      + '前提が少し違うだけで年は動きます。年そのものより、動かせる前提はどれかを見てください。';
  }
}
""" + SENS_JS_END + """
""").replace("INPUT", input_label)


# ===== 対話の問い（立場の切り替え） =====
# フューチャー・デザイン（矢巾町）の「仮想将来世代」の考え方。同じ人が立場を変えると
# 違う結論を出す、という実証がある（risk-calculators.html の事例を参照）。
# path -> その計算機に固有の「将来の当事者」の問い
ROLE_Q = {
    "customer-age-timebomb.html":
        "あなたは2045年に、この会社の商品を選ぶかどうかを決める人です。いまの品ぞろえと売り方は、あなたに届いていますか。",
    "recruitment-extinction.html":
        "あなたは2040年に就職先を選ぶ22歳です。この会社の求人を見て、応募したいと思いますか。何があれば応募しますか。",
    "tax-revenue-countdown.html":
        "あなたは2050年にこのまちで子育てをしている住民です。2026年の意思決定者に、何をしておいてほしかったと言いますか。",
    "skill-succession-timebomb.html":
        "あなたは、この技を教わらないまま現場を任された10年後の担当者です。いまの引き継ぎ計画に何を言いますか。",
    "school-consolidation-countdown.html":
        "あなたは2040年にこの校区で暮らす子どもです。いまの大人たちの話し合いに、何を望みますか。",
    "caregiving-capacity-calculator.html":
        "あなたは、支えられる側になった自分自身です。そのときの自分は、いまの自分に何を頼みますか。",
}

DIALOGUE_CSS = """  /* 対話の問い・意思決定シート。回答はブラウザにだけ残す（送信しない） */
  .talk { background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 1.4rem 1.4rem 1.5rem; }
  .talk h2 { font-family: 'Shippori Mincho', serif; font-size: 1.05rem; font-weight: 800; color: var(--ink); margin-bottom: 0.5rem; }
  .talk-lead { font-size: 0.82rem; line-height: 1.95; color: var(--ink-soft); margin-bottom: 1.2rem; }
  .q { margin-bottom: 1rem; }
  .q-label { display: block; font-size: 0.84rem; font-weight: 600; color: var(--ink); margin-bottom: 0.3rem; line-height: 1.75; }
  .q-hint { display: block; font-size: 0.72rem; color: var(--ink-soft); font-weight: 400; margin-top: 0.1rem; line-height: 1.8; }
  .q textarea { width: 100%; min-height: 3.4em; padding: 0.6rem 0.7rem; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); font-family: 'Noto Serif JP', serif; font-size: 0.84rem; line-height: 1.9; color: var(--charcoal); resize: vertical; }
  .q textarea:focus { outline: 2px solid var(--teal); outline-offset: 1px; }
  .q.role { background: rgba(217,164,65,0.09); border-radius: 10px; padding: 0.9rem 1rem; }
  .q.role .q-label { color: var(--gold-deep); }
  .talk-actions { display: flex; flex-wrap: wrap; gap: 0.6rem; align-items: center; margin-top: 1.2rem; }
  .talk-btn { font-family: 'Noto Serif JP', serif; font-size: 0.82rem; padding: 0.5rem 1.3rem; border-radius: 999px; cursor: pointer; border: 1.5px solid var(--ink); background: var(--ink); color: var(--paper); }
  .talk-btn:hover { background: var(--ink-deep); }
  .talk-btn.ghost { background: transparent; color: var(--ink-soft); border-color: var(--line); }
  .talk-btn.ghost:hover { border-color: var(--dawn); color: var(--dawn); }
  .talk-saved { font-size: 0.72rem; color: var(--teal); }
  .talk-note { font-size: 0.7rem; color: var(--ink-soft); margin-top: 0.7rem; line-height: 1.85; }
  /* 印刷＝意思決定記録。計算機のUIは落とし、問いと答えだけを1枚に */
  @media print {
    nav, .mobile-menu, footer, .kaiyu, .fuse, .card, .chart-box, .scene-frame, .presets, .talk-actions, .license { display: none !important; }
    .talk { display: block !important; border: none; padding: 0; }
    #printHead { display: block !important; }
    body { background: #fff; }
    .q textarea { border: none; border-bottom: 1px solid #ccc; background: #fff; min-height: 0; }
  }
  #printHead { display: none; }"""


def dialogue_html(num, title, role_q):
    qs = [
        ("q1", "この結果を見て、いちばん驚いたことは何ですか。", "「思ったより早い」「思ったより遅い」でも構いません。"),
        ("q2", "この未来が起きると、いちばん困るのは誰ですか。", "その人は、いまこの話し合いの場にいますか。"),
        ("q3", "この計算が置いている前提のうち、自分たちで変えられるものはどれですか。", "変えられない前提と、変えられる前提を分けます。"),
        ("q4", "いま決めなければ、いつから選択肢が減りますか。", "上の「決められるのはあと◯年」を見ながら書きます。"),
        ("q5", "30日以内に試せる、いちばん小さな行動は何ですか。", "大きな計画ではなく、来週できることを1つ。"),
        ("q6", "それは誰が、いつまでにやりますか。", "担当と期限がない行動は、実行されません。"),
    ]
    rows = "\n".join(
        f'      <div class="q"><label class="q-label" for="{k}">{q}<span class="q-hint">{h}</span></label>'
        f'<textarea id="{k}" data-k="{k}"></textarea></div>'
        for k, q, h in qs)
    return f"""{TALK_START}
<section>
  <div class="wrap">
    <div class="talk">
      <div id="printHead">
        <p style="font-size:0.7rem;letter-spacing:0.2em;color:#888">未来リスク計算機 {num}／{title}</p>
        <h1 style="font-family:'Shippori Mincho',serif;font-size:1.3rem;margin:0.3rem 0 1rem">未来リスク対話記録</h1>
      </div>
      <h2>数字を見たあとに、話すこと</h2>
      <p class="talk-lead">ここまでの数字は、話し合いを始めるためのものです。以下に答えて印刷すると、そのまま会議で配れる1枚の記録になります。答えはこのブラウザにだけ保存され、どこにも送信されません。</p>
      <div class="q role"><label class="q-label" for="q0">立場を変えて考える<span class="q-hint">{role_q}</span></label><textarea id="q0" data-k="q0"></textarea></div>
{rows}
      <div class="talk-actions">
        <button class="talk-btn" type="button" id="printBtn">印刷／PDFで保存する</button>
        <button class="talk-btn ghost" type="button" id="clearBtn">回答を消す</button>
        <span class="talk-saved" id="savedMsg"></span>
      </div>
      <p class="talk-note">※ 回答はこの端末のブラウザ内（localStorage）にのみ保存されます。サーバーには送信していません。共有したいときは印刷／PDFをお使いください。端末やブラウザを変えると消えます。</p>
    </div>
  </div>
</section>
{TALK_END}"""


DIALOGUE_JS = """
/* TALK-JS START */
/* ===== 対話の問い =====
   数字を見て「厳しいですね」で終わらせないための導線。回答はサーバーに送らず
   localStorage にだけ置く（「数字はどこにも送信されません」を崩さないため） */
(function(){
  const KEY = 'kk-talk-' + location.pathname.split('/').pop();
  const fields = [...document.querySelectorAll('.talk textarea')];
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { saved = {}; }
  fields.forEach(t => { if (saved[t.dataset.k]) t.value = saved[t.dataset.k]; });

  let timer = null;
  const msg = document.getElementById('savedMsg');
  function save(){
    const out = {};
    fields.forEach(t => { if (t.value.trim()) out[t.dataset.k] = t.value; });
    try {
      localStorage.setItem(KEY, JSON.stringify(out));
      msg.textContent = 'この端末に保存しました';
      clearTimeout(timer);
      timer = setTimeout(() => { msg.textContent = ''; }, 2000);
    } catch (e) { msg.textContent = '保存できませんでした（ブラウザの設定をご確認ください）'; }
  }
  fields.forEach(t => t.addEventListener('input', save));

  document.getElementById('printBtn').addEventListener('click', () => window.print());
  document.getElementById('clearBtn').addEventListener('click', () => {
    if (!confirm('入力した回答をすべて消します。よろしいですか。')) return;
    fields.forEach(t => { t.value = ''; });
    try { localStorage.removeItem(KEY); } catch (e) {}
    msg.textContent = '消しました';
  });
})();
/* TALK-JS END */
"""

TALK_START = "<!-- TALK START -->"
TALK_END = "<!-- TALK END -->"


# ===== シリーズ6本のフッター帯 =====
# 計算機を見ている人が、ナビを開かずに他の5本へ移れるようにする。
# 出すのは「計算機6本＋ハブ」の7ページだけ（森本さん判断）。PTAキットや妖怪診断の
# 下に「税収カウントダウン」が並ぶのは筋が悪いので、サイト全体には出さない。
# 置き場所は回遊バンドとサイト共通フッターの間（どちらも別スクリプトの生成物なので、
# その外側に自前のマーカーを持つ）。
SERIES_START = "<!-- SERIES START -->"
SERIES_END = "<!-- SERIES END -->"

# (ファイル名, 番号, 表示名)
SERIES = [
    ("customer-age-timebomb.html", "01", "顧客の平均年齢時限爆弾"),
    ("recruitment-extinction.html", "02", "採用市場消滅計算機"),
    ("tax-revenue-countdown.html", "03", "税収カウントダウン"),
    ("skill-succession-timebomb.html", "04", "技能承継時限爆弾"),
    ("school-consolidation-countdown.html", "05", "学校統廃合カウントダウン"),
    ("caregiving-capacity-calculator.html", "06", "介護の支え手計算機"),
]

SERIES_CSS = """  /* シリーズ6本のフッター帯（scripts/update-calculators.py の生成物） */
  .series-band { background: rgba(60,52,20,0.045); border-top: 1px solid var(--line); padding: 2.4rem 1.5rem 2.6rem; }
  .series-inner { max-width: 880px; margin: 0 auto; }
  .series-head { font-family: 'Jost', 'Noto Serif JP', sans-serif; font-size: 0.7rem; letter-spacing: 0.24em; color: #b8862d; margin-bottom: 1rem; }
  .series-list { list-style: none; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.5rem; }
  @media (max-width: 760px) { .series-list { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 420px) { .series-list { grid-template-columns: minmax(0, 1fr); } }
  .series-list a, .series-list .now { display: flex; align-items: baseline; gap: 0.5rem; padding: 0.6rem 0.7rem; border-radius: 9px; border: 1px solid #ddd6c4; background: #fffdf7; text-decoration: none; transition: border-color 0.18s, transform 0.18s; }
  .series-list a:hover { border-color: var(--gold); transform: translateY(-2px); }
  .series-list .now { background: var(--ink); border-color: var(--ink); }
  .series-no { font-family: 'Jost', sans-serif; font-size: 0.7rem; color: var(--gold-deep); flex-shrink: 0; }
  .series-list .now .series-no { color: var(--gold); }
  .series-name { font-family: 'Shippori Mincho', serif; font-size: 0.8rem; font-weight: 700; color: var(--ink); line-height: 1.55; }
  .series-list .now .series-name { color: var(--paper); }
  .series-foot { font-size: 0.74rem; margin-top: 0.9rem; }
  .series-foot a { color: var(--teal); }
  .series-foot .now-hub { color: var(--ink-soft); }
  @media print { .series-band { display: none !important; } }"""


def series_band(current, prefix="./"):
    """current = 現在のページのファイル名。ハブなら 'hub'。"""
    items = []
    for path, num, name in SERIES:
        inner = f'<span class="series-no">{num}</span><span class="series-name">{name}</span>'
        if path == current:
            items.append(f'        <li><span class="now" aria-current="page">{inner}</span></li>')
        else:
            items.append(f'        <li><a href="{prefix}{path}">{inner}</a></li>')
    hub = ('<span class="now-hub">このシリーズについて（前提・出典・免責・変更履歴）― いまご覧のページです</span>'
           if current == "hub" else
           f'<a href="{prefix}{HUB}">このシリーズについて（前提・出典・免責・変更履歴）</a>')
    return (SERIES_START + '\n'
            '<aside class="series-band" aria-label="未来のリスク計算機シリーズ">\n'
            '  <div class="series-inner">\n'
            '    <p class="series-head">未来のリスク計算機（全6本）</p>\n'
            '    <ul class="series-list">\n'
            + "\n".join(items) + '\n'
            '    </ul>\n'
            f'    <p class="series-foot">{hub}</p>\n'
            '  </div>\n'
            '</aside>\n' + SERIES_END)


def put_series(s, path, current):
    """回遊バンドとサイト共通フッターの間に差す（どちらの生成物も壊さない）。"""
    band = series_band(current)
    if SERIES_START in s:
        return re.sub(re.escape(SERIES_START) + r".*?" + re.escape(SERIES_END),
                      lambda m: band, s, count=1, flags=re.S)
    anchor = "<!-- FOOTER START -->"
    if s.count(anchor) != 1:
        raise SystemExit(f"{path}: FOOTER マーカーが {s.count(anchor)} 個")
    return s.replace(anchor, band + "\n\n" + anchor, 1)


# path -> (シリーズ番号, タイトル, 出典の一文)
PAGES = {
    "customer-age-timebomb.html": (
        "01", "顧客の平均年齢時限爆弾",
        f"出典：年齢帯別の死亡率は厚生労働省「{MHLW_LIFE}」の近似値。",
    ),
    "recruitment-extinction.html": (
        "02", "採用市場消滅計算機",
        f"出典：出生数は厚生労働省「{MHLW_VITAL}」の実績値。",
    ),
    "tax-revenue-countdown.html": (
        "03", "税収カウントダウン",
        # 人口は利用者入力。IPSS の推計値は使っていない（使っているのは生命表近似の死亡率だけ）
        f"出典：人口・財政の数値は利用者が入力したもので、外部の統計データは使っていません。"
        f"加齢にともなう年齢帯別の死亡率のみ、厚生労働省「{MHLW_LIFE}」の近似値を使っています。",
    ),
    "skill-succession-timebomb.html": (
        "04", "技能承継時限爆弾",
        "出典：外部の統計データは使っていません（入力された数字だけで計算しています）。",
    ),
    "school-consolidation-countdown.html": (
        "05", "学校統廃合カウントダウン",
        # 出生数は利用者入力のみ。人口動態統計の実績値は読み込んでいない
        f"出典：出生数は利用者が入力したもので、外部の統計データは使っていません。"
        f"学級編制の考え方は{EGOV_SCHOOL}を参照していますが、"
        "本ページの目安（48人・24人）は簡略化したもので、実際の基準は各自治体の方針で異なります。",
    ),
    "caregiving-capacity-calculator.html": (
        "06", "介護の支え手計算機",
        # 2070年までは基本推計 表1-9A、2071〜2120年は長期参考推計 参考表1-9A の公表値
        # （以前は「近似値・2070年以降は横ばい」としていたが、実データに置き換えた）
        f"出典：人口は国立社会保障・人口問題研究所「{IPSS}」の公表値"
        f"（2070年までは基本推計、2071〜2120年は同研究所の長期参考推計）、"
        f"要介護認定率・介護職員数は厚生労働省「{MHLW_KAIGO}」の概数。",
    ),
}

DISCLAIMER = (
    "本計算機の結果は簡易な試算であり、将来を保証するものではありません。"
    "これに基づく判断・意思決定の結果について当工房は責任を負いかねます。"
)

# 技術・制度の変化を織り込んでいないこと。
# ★書き方に注意: 「技術が解決するかも」と書きすぎると先送りの免罪符になり、
#   このツールが戦っている当のものになる。「前提は変わりうる／ただし待つのは
#   打ち手にならない」の両方を必ずセットで書く（詳細はハブの前提5）。
INNOVATION = (
    "いまのやり方・いまの生産性が続く前提で計算しており、"
    "技術や制度の変化（介護ロボットや自動化など）は織り込んでいません。"
    "変われば前提そのものが変わりますが、いつ来るか分からないものはリードタイムを見積もれないため、"
    "待つことは打ち手になりません。"
)

MARK_START = "<!-- CALC-COMMON START -->"
MARK_END = "<!-- CALC-COMMON END -->"

BADGE_CSS_ANCHOR = "  .note { font-size: 0.72rem; line-height: 1.95; color: var(--ink-soft); }"
BADGE_CSS = """  /* 「簡易試算」バッジ。大きな数字と但し書きは画面にして数スクロール離れているため、
     数字だけスクショされると前提が一切伝わらない。数字の隣に置いて一緒に写るようにする */
  .approx { display: inline-block; font-family: 'Jost', 'Noto Serif JP', sans-serif; font-size: 0.62rem; letter-spacing: 0.12em; padding: 0.15em 0.7em; border-radius: 999px; border: 1px solid rgba(250,248,242,0.45); color: rgba(250,248,242,0.8); white-space: nowrap; align-self: center; }
  /* ライセンス表記。サイト共通フッターとは別物なので footer 要素ではなく div で作る
     （footer 要素にすると scripts/update-nav.py の locate_footer がこちらを先に掴み、
     マーカー破損時に誤置換される。同じ理由でこのコメントにもタグ名を書かない） */
  .license { margin-top: 1.8rem; padding-top: 1rem; border-top: 1px solid var(--line); font-size: 0.7rem; line-height: 1.85; color: var(--ink-soft); }
  .license a { color: var(--teal); }
  .license .ver { font-family: 'Jost', sans-serif; letter-spacing: 0.06em; color: var(--ink); font-weight: 600; }"""

BADGE_HTML = '<span class="approx">簡易試算</span>'


def build_common(num, title, source):
    """※注記の下に入る共通ブロック（出典・免責・ライセンス・版）。

    ★ <p> は必ず1行で書く。句読点の後で改行すると mobile-preflight の
      Pattern A（句読点孤立・widow の原因）に引っかかる。
    """
    note = (f'{source}<br>{DISCLAIMER}{INNOVATION}'
            f'前提・出典の詳細と変更履歴は <a href="./{HUB}" style="color:var(--teal)">未来のリスク計算機について</a> にまとめています。')
    return f"""{MARK_START}
    <p class="note" style="margin-top:0.8rem">{note}</p>
    <div class="license">
      &copy; 2026 きづきくみたて工房（<a href="./index.html">kizukikumitate.com</a>）　<span class="ver">ver {VERSION}</span>（{VERSION_DATE_JA}）<br>
      この計算機は、いただくご意見を反映しながら育てています。前提や数字におかしな点があれば <a href="mailto:y.morimoto@kizukikumitate.com?subject=%E6%9C%AA%E6%9D%A5%E3%81%AE%E3%83%AA%E3%82%B9%E3%82%AF%E8%A8%88%E7%AE%97%E6%A9%9F%E3%81%B8%E3%81%AE%E3%81%94%E6%84%8F%E8%A6%8B%EF%BC%88{urllib.parse.quote(title)}%20ver%20{VERSION}%EF%BC%89">ご意見</a> をお寄せください。<br>
      本計算機は <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ja" rel="license noopener" target="_blank">CC BY-NC-SA 4.0</a> で公開しています。非営利での利用・改変・再配布は、クレジット表記と同条件での公開を条件に自由です。改変した場合はその旨を明記し、当工房の試算としては示さないでください。商用利用をご希望の場合は <a href="./index.html#contact">お問い合わせ</a> ください。
    </div>
{MARK_END}"""


def header_comment(num, title):
    return (
        "<!DOCTYPE html>\n"
        "<!--\n"
        f"  未来リスク計算機シリーズ {num} {title}\n"
        "  (c) 2026 きづきくみたて工房 森本康仁 (kizukikumitate.com)\n"
        f"  version: {VERSION} ({VERSION_DATE})\n"
        "  License: CC BY-NC-SA 4.0\n"
        "  https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ja\n"
        "  非営利利用: クレジット表記＋同ライセンス継承で自由\n"
        "  商用利用: 要事前許諾 → kizukikumitate.com へご相談ください\n"
        "-->"
    )


def process(path, num, title, source):
    p = ROOT / path
    s = orig = p.read_text(encoding="utf-8")

    # --- 1. 冒頭コメント（版つきに置き換え。既存の版なしコメントも拾う） ---
    s = re.sub(r"^<!DOCTYPE html>\n<!--\n  未来リスク計算機シリーズ.*?-->",
               lambda m: header_comment(num, title), s, count=1, flags=re.S)
    if not s.startswith("<!DOCTYPE html>\n<!--"):
        s = s.replace("<!DOCTYPE html>", header_comment(num, title), 1)

    # --- 2. CSS ---
    if ".approx {" not in s:
        if BADGE_CSS_ANCHOR not in s:
            raise SystemExit(f"{path}: note の CSS が見つかりません")
        s = s.replace(BADGE_CSS_ANCHOR, BADGE_CSS_ANCHOR + "\n" + BADGE_CSS, 1)
    # 旧版（ライセンス追加時）の .license CSS が残っていれば重複するので消す
    s = re.sub(
        r"\n  /\* ライセンス表記（CC BY-NC-SA 4\.0）。.*?\n  \.license a \{ color: var\(--teal\); \}",
        "", s, count=1, flags=re.S)

    # --- 3. バッジを大きな数字の隣に ---
    if BADGE_HTML not in s:
        m = re.search(r'(<span class="fuse-big" id="fuseBig">.*?</span>)', s)
        if not m:
            raise SystemExit(f"{path}: fuse-big が見つかりません")
        s = s.replace(m.group(1), m.group(1) + "\n        " + BADGE_HTML, 1)

    # --- 3.5 意思決定期限（対象ページのみ） ---
    if path in DEADLINE:
        var, label = DEADLINE[path]
        if 'class="deadline"' not in s:
            # 導火線バーの目盛り（<div class="ends">）の直後、fuse ブロックの中に置く。
            # 最初の1個が fuse のもの（scene 側にも ends を持つページがあるため count=1）
            m = re.search(r'<div class="ends">.*?</div>\n', s, re.S)
            if not m:
                raise SystemExit(f"{path}: fuse の ends が見つかりません")
            s = s[:m.end()] + DEADLINE_HTML + "\n" + s[m.end():]
        if ".deadline {" not in s:
            s = s.replace(BADGE_CSS_ANCHOR, BADGE_CSS_ANCHOR + "\n" + DEADLINE_CSS, 1)
        if f"renderDeadline({var});" not in s:
            # render() 内、fuseBig を書くすぐ手前に呼び出しを差す（そこなら var がスコープ内）
            anchor = "  document.getElementById('fuseBig').textContent ="
            if s.count(anchor) != 1:
                raise SystemExit(f"{path}: fuseBig の行が {s.count(anchor)} 個")
            s = s.replace(anchor, f"  renderDeadline({var});\n" + anchor, 1)
        js = deadline_js(label)
        if DL_JS_START in s:
            s = re.sub(re.escape(DL_JS_START) + r".*?" + re.escape(DL_JS_END),
                       lambda m: js.strip("\n"), s, count=1, flags=re.S)
        else:
            # 関数定義は最後の render(); 呼び出しの手前に置く
            tail = "\nrender();\n</script>"
            if s.count(tail) != 1:
                raise SystemExit(f"{path}: 末尾の render(); が {s.count(tail)} 個")
            s = s.replace(tail, js + tail, 1)

    # --- 3.55 感度レンジ（対象ページのみ） ---
    if path in SENS:
        expr, in_label = SENS[path]
        if 'id="sensOut"' not in s:
            # 導火線の目盛りの直後（意思決定期限より前）に置く
            m = re.search(r'<div class="ends">.*?</div>\n', s, re.S)
            if not m:
                raise SystemExit(f"{path}: fuse の ends が見つかりません")
            s = s[:m.end()] + SENS_HTML + "\n" + s[m.end():]
        if ".sens {" not in s:
            s = s.replace(BADGE_CSS_ANCHOR, BADGE_CSS_ANCHOR + "\n" + SENS_CSS, 1)
        if "renderSens(" not in s.split("function renderSens(")[0]:
            anchor = "  document.getElementById('fuseBig').textContent ="
            if s.count(anchor) != 1:
                raise SystemExit(f"{path}: fuseBig の行が {s.count(anchor)} 個")
            s = s.replace(anchor, f"  renderSens({expr});\n" + anchor, 1)
        js = sens_js(in_label)
        if SENS_JS_START in s:
            s = re.sub(re.escape(SENS_JS_START) + r".*?" + re.escape(SENS_JS_END),
                       lambda m: js.strip("\n"), s, count=1, flags=re.S)
        else:
            tail = "\nrender();\n"
            if tail not in s:
                raise SystemExit(f"{path}: 末尾の render(); が見つかりません")
            s = s.replace(tail, js + tail, 1)

    # --- 3.6 対話の問い＋意思決定シート（全6本） ---
    if ".talk {" not in s:
        s = s.replace(BADGE_CSS_ANCHOR, BADGE_CSS_ANCHOR + "\n" + DIALOGUE_CSS, 1)
    talk = dialogue_html(num, title, ROLE_Q[path])
    if TALK_START in s:
        s = re.sub(re.escape(TALK_START) + r".*?" + re.escape(TALK_END), lambda m: talk, s, count=1, flags=re.S)
    else:
        # 「解除の型」の散文の後、※注記の手前に置く（＝数字→解説→対話 の順）
        anchor = "<!-- CALC-COMMON START -->"
        if anchor not in s:
            raise SystemExit(f"{path}: CALC-COMMON マーカーがありません（先に共通ブロックを入れてください）")
        # ※注記セクションの開始（<section> ... CALC-COMMON）まで遡って、その手前に差す
        sec = s.rfind("<section>", 0, s.find(anchor))
        s = s[:sec] + talk + "\n\n" + s[sec:]
    if "/* TALK-JS START */" in s:
        s = re.sub(r"/\* TALK-JS START \*/.*?/\* TALK-JS END \*/",
                   lambda m: DIALOGUE_JS.strip("\n"), s, count=1, flags=re.S)
    else:
        tail = "\nrender();\n</script>"
        if s.count(tail) != 1:
            raise SystemExit(f"{path}: 末尾の render(); が {s.count(tail)} 個")
        s = s.replace(tail, "\nrender();\n" + DIALOGUE_JS + "</script>", 1)

    # --- 3.7 シリーズ6本のフッター帯 ---
    if ".series-band {" not in s:
        s = s.replace(BADGE_CSS_ANCHOR, BADGE_CSS_ANCHOR + "\n" + SERIES_CSS, 1)
    s = put_series(s, path, path)

    # --- 4. 共通ブロック（マーカーがあれば中身を差し替え＝冪等） ---
    block = build_common(num, title, source)
    if MARK_START in s:
        s = re.sub(re.escape(MARK_START) + r".*?" + re.escape(MARK_END), lambda m: block, s, count=1, flags=re.S)
    else:
        # 旧版のライセンス div を撤去してから入れ直す
        s = re.sub(r'\n    <div class="license">\n.*?\n    </div>', "", s, count=1, flags=re.S)
        anchor = "  </div>\n</section>\n\n<!-- KAIYU START -->"
        if s.count(anchor) != 1:
            raise SystemExit(f"{path}: 差し込み先が {s.count(anchor)} 個")
        s = s.replace(anchor, block + "\n" + anchor, 1)

    if s != orig:
        return s
    return None


def process_hub(check):
    """ハブページ（risk-calculators.html）にも同じ帯を出す。
    ハブは計算機ではないので PAGES のループには乗せず、帯とCSSだけ入れる。"""
    p = ROOT / HUB
    s = orig = p.read_text(encoding="utf-8")
    if ".series-band {" not in s:
        anchor = "  .note { font-size: 0.72rem; line-height: 1.95; color: var(--ink-soft); }"
        if anchor not in s:
            raise SystemExit(f"{HUB}: note の CSS が見つかりません")
        s = s.replace(anchor, anchor + "\n" + SERIES_CSS, 1)
    s = put_series(s, HUB, "hub")
    if s == orig:
        print(f"  ✅ {HUB}: 変更なし")
        return 0
    if check:
        print(f"  ⚠️  {HUB}: 差分あり（--check のため書き込みません）")
    else:
        p.write_text(s, encoding="utf-8")
        print(f"  ✏️  {HUB}: シリーズ帯を更新")
    return 1


def main():
    check = "--check" in sys.argv
    changed = 0
    for path, (num, title, source) in PAGES.items():
        out = process(path, num, title, source)
        if out is None:
            print(f"  ✅ {path}: 変更なし")
            continue
        changed += 1
        if check:
            print(f"  ⚠️  {path}: 差分あり（--check のため書き込みません）")
        else:
            (ROOT / path).write_text(out, encoding="utf-8")
            print(f"  ✏️  {path}: 共通パーツを更新（{num} {title} / ver {VERSION}）")
    changed += process_hub(check)
    print(f"完了: {changed} ページ（対象 {len(PAGES)} ページ＋ハブ / ver {VERSION}）")
    if check and changed:
        sys.exit(1)


if __name__ == "__main__":
    main()

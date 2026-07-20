#!/usr/bin/env node
/**
 * GA4 から週次・月次のレポート用データを取得し、Markdownで書き出す。
 *
 *   node scripts/ga-report.mjs            … 過去28日 vs その前の28日
 *   node scripts/ga-report.mjs --days 7   … 過去7日 vs その前の7日
 *   node scripts/ga-report.mjs --stdout   … ファイルに書かず標準出力へ
 *
 * ★ネットワーク: oauth2.googleapis.com / analyticsdata.googleapis.com は
 *   サンドボックス不許可。Claude Code から実行するときは
 *   dangerouslyDisableSandbox: true が必要。
 *
 * ★認証: サービスアカウントJSON（閲覧者権限のみ）。
 *   既定 ~/.config/kizukikumitate/ga4-service-account.json （chmod 600）
 *   リポジトリには絶対に置かない。キーの中身をコマンドラインに渡さない。
 *
 * 外部パッケージ不要（署名は node:crypto で行う）。
 */

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const CONF_DIR = path.join(process.env.HOME, '.config', 'kizukikumitate');
const CRED_FILE = process.env.GA4_CREDENTIALS || path.join(CONF_DIR, 'ga4-service-account.json');
const PROP_FILE = path.join(CONF_DIR, 'ga4-property-id');
const OUT_DIR = process.env.GA_REPORT_DIR
  || path.join(process.env.HOME, 'kizukikumitate-ops', 'analytics', 'reports');

// 有料導線。表示回数の分母として使う
const FUNNEL = {
  calculator: '/salary-negotiation-calculator.html',
  kitLp: '/salary-negotiation-kit.html',
};

// ---------------------------------------------------------------- 設定読み込み

function fail(msg, hint) {
  console.error(msg);
  if (hint) console.error('\n' + hint);
  process.exit(1);
}

function loadCredentials() {
  if (!fs.existsSync(CRED_FILE)) {
    fail(`サービスアカウントJSONが見つかりません: ${CRED_FILE}`,
      [
        'セットアップ手順:',
        '  1. console.cloud.google.com で Google Analytics Data API を有効化',
        '  2. サービスアカウント(ga4-reader)を作成し、JSONキーをダウンロード',
        '  3. GA4 → 管理 → プロパティのアクセス管理 で、そのメールアドレスに「閲覧者」を付与',
        `  4. mkdir -p "${CONF_DIR}"`,
        `     mv ~/Downloads/<ダウンロードしたファイル>.json "${CRED_FILE}"`,
        `     chmod 600 "${CRED_FILE}"`,
        `  5. GA4のプロパティID(数字)を  echo <ID> > "${PROP_FILE}"`,
      ].join('\n'));
  }
  if (fs.statSync(CRED_FILE).mode & 0o077) {
    console.error(`⚠ ${CRED_FILE} が他ユーザーから読めます。chmod 600 を推奨\n`);
  }
  const c = JSON.parse(fs.readFileSync(CRED_FILE, 'utf8'));
  if (!c.client_email || !c.private_key) fail('JSONに client_email / private_key がありません');
  return c;
}

function loadPropertyId() {
  const id = (process.env.GA4_PROPERTY_ID || '').trim()
    || (fs.existsSync(PROP_FILE) ? fs.readFileSync(PROP_FILE, 'utf8').trim() : '');
  if (!/^\d+$/.test(id)) {
    fail('GA4のプロパティID(数字)が未設定です',
      `GA4 → 管理 → プロパティの詳細 で確認し:\n  echo <ID> > "${PROP_FILE}"\n`
      + '★計測ID(G-2ECK6163X4)ではなく、9桁程度の数字の方です');
  }
  return id;
}

// ---------------------------------------------------------------- 認証

function base64url(buf) {
  return Buffer.from(buf).toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

/** サービスアカウントの秘密鍵でJWTを署名し、アクセストークンと交換する。 */
async function getAccessToken(cred) {
  const now = Math.floor(Date.now() / 1000);
  const header = base64url(JSON.stringify({ alg: 'RS256', typ: 'JWT' }));
  const claim = base64url(JSON.stringify({
    iss: cred.client_email,
    scope: 'https://www.googleapis.com/auth/analytics.readonly',
    aud: 'https://oauth2.googleapis.com/token',
    exp: now + 3600,
    iat: now,
  }));
  const signer = crypto.createSign('RSA-SHA256');
  signer.update(`${header}.${claim}`);
  const jwt = `${header}.${claim}.${base64url(signer.sign(cred.private_key))}`;

  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
      assertion: jwt,
    }),
  });
  const j = await res.json();
  if (!j.access_token) fail(`アクセストークンを取得できません: ${JSON.stringify(j).slice(0, 300)}`);
  return j.access_token;
}

// ---------------------------------------------------------------- データ取得

async function runReport(token, propertyId, body) {
  const res = await fetch(
    `https://analyticsdata.googleapis.com/v1beta/properties/${propertyId}:runReport`,
    {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    },
  );
  const j = await res.json();
  if (j.error) {
    const hint = j.error.status === 'PERMISSION_DENIED'
      ? '\nGA4 → 管理 → プロパティのアクセス管理 で、サービスアカウントに「閲覧者」を付与したか確認してください。'
      : '';
    fail(`GA4 API エラー: ${j.error.message}${hint}`);
  }
  return j;
}

/** レスポンスを [{dims:[...], mets:[数値...]}] に整形する。 */
function rows(res) {
  return (res.rows || []).map((r) => ({
    dims: (r.dimensionValues || []).map((d) => d.value),
    mets: (r.metricValues || []).map((m) => Number(m.value)),
  }));
}

function dateRanges(days) {
  return [
    { startDate: `${days}daysAgo`, endDate: 'yesterday', name: 'current' },
    { startDate: `${days * 2}daysAgo`, endDate: `${days + 1}daysAgo`, name: 'previous' },
  ];
}

// ---------------------------------------------------------------- 整形

const pct = (now, before) => {
  if (!before) return now ? '新規' : '—';
  const d = ((now - before) / before) * 100;
  return `${d >= 0 ? '+' : ''}${d.toFixed(0)}%`;
};

const rate = (num, den) => (den ? `${((num / den) * 100).toFixed(1)}%` : '—');

function splitByRange(res) {
  // dateRanges を2つ渡すと最後のディメンションに 'date_range' が入る
  const cur = new Map(); const prev = new Map();
  for (const r of rows(res)) {
    const key = r.dims.slice(0, -1).join('\t');
    const target = r.dims[r.dims.length - 1] === 'current' ? cur : prev;
    target.set(key, r.mets);
  }
  return { cur, prev };
}

// ---------------------------------------------------------------- 本体

async function main() {
  const args = process.argv.slice(2);
  const days = Number(args[args.indexOf('--days') + 1]) || 28;
  const toStdout = args.includes('--stdout');

  const cred = loadCredentials();
  const propertyId = loadPropertyId();
  const token = await getAccessToken(cred);
  const ranges = dateRanges(days);

  const [pagesRes, chanRes, evRes, totalRes] = await Promise.all([
    runReport(token, propertyId, {
      dateRanges: ranges,
      dimensions: [{ name: 'pagePath' }],
      metrics: [{ name: 'screenPageViews' }, { name: 'activeUsers' }],
      orderBys: [{ metric: { metricName: 'screenPageViews' }, desc: true }],
      limit: 200,
    }),
    runReport(token, propertyId, {
      dateRanges: ranges,
      dimensions: [{ name: 'sessionDefaultChannelGroup' }],
      metrics: [{ name: 'sessions' }],
      orderBys: [{ metric: { metricName: 'sessions' }, desc: true }],
    }),
    runReport(token, propertyId, {
      dateRanges: ranges,
      dimensions: [{ name: 'eventName' }],
      metrics: [{ name: 'eventCount' }],
      orderBys: [{ metric: { metricName: 'eventCount' }, desc: true }],
      limit: 50,
    }),
    runReport(token, propertyId, {
      dateRanges: ranges,
      metrics: [{ name: 'screenPageViews' }, { name: 'activeUsers' }, { name: 'sessions' }],
    }),
  ]);

  const pages = splitByRange(pagesRes);
  const chan = splitByRange(chanRes);
  const ev = splitByRange(evRes);
  const tot = splitByRange(totalRes);

  const t = tot.cur.get('') || [0, 0, 0];
  const tp = tot.prev.get('') || [0, 0, 0];
  const evc = (n) => (ev.cur.get(n) || [0])[0];
  const evp = (n) => (ev.prev.get(n) || [0])[0];
  const pv = (p) => (pages.cur.get(p) || [0])[0];
  const pvp = (p) => (pages.prev.get(p) || [0])[0];

  const today = new Date().toISOString().slice(0, 10);
  const L = [];
  L.push(`# アクセスレポート ${today}（過去${days}日 / 前${days}日と比較）`);
  L.push('');
  L.push('## 全体');
  L.push('');
  L.push('| 指標 | 今回 | 前回 | 変化 |');
  L.push('|---|---:|---:|---:|');
  L.push(`| 表示回数 | ${t[0]} | ${tp[0]} | ${pct(t[0], tp[0])} |`);
  L.push(`| ユーザー数 | ${t[1]} | ${tp[1]} | ${pct(t[1], tp[1])} |`);
  L.push(`| セッション | ${t[2]} | ${tp[2]} | ${pct(t[2], tp[2])} |`);
  L.push('');

  L.push('## 有料導線（昇給交渉キット）');
  L.push('');
  const calcPv = pv(FUNNEL.calculator); const kitPv = pv(FUNNEL.kitLp);
  const sel = evc('select_item'); const chk = evc('begin_checkout');
  L.push('| 段階 | 今回 | 前回 |');
  L.push('|---|---:|---:|');
  L.push(`| 計算機の表示 | ${calcPv} | ${pvp(FUNNEL.calculator)} |`);
  L.push(`| → キットLPへ送客 (select_item) | ${sel} | ${evp('select_item')} |`);
  L.push(`| キットLPの表示 | ${kitPv} | ${pvp(FUNNEL.kitLp)} |`);
  L.push(`| → 購入ボタン押下 (begin_checkout) | ${chk} | ${evp('begin_checkout')} |`);
  L.push('');
  L.push(`- 送客率（select_item ÷ 計算機の表示） = **${rate(sel, calcPv)}**`);
  L.push(`- 押下率（begin_checkout ÷ LPの表示） = **${rate(chk, kitPv)}**`);
  if (calcPv < 30 || kitPv < 30) {
    L.push('');
    L.push('> ⚠ 分母が30未満です。**この率はまだ判断に使えません**（1人の増減で大きく振れます）。');
  }
  L.push('');

  L.push('## 流入元');
  L.push('');
  L.push('| チャネル | セッション | 前回 | 変化 |');
  L.push('|---|---:|---:|---:|');
  for (const [k, v] of [...chan.cur.entries()].sort((a, b) => b[1][0] - a[1][0])) {
    const p = (chan.prev.get(k) || [0])[0];
    L.push(`| ${k} | ${v[0]} | ${p} | ${pct(v[0], p)} |`);
  }
  L.push('');

  const sorted = [...pages.cur.entries()].sort((a, b) => b[1][0] - a[1][0]);
  L.push('## よく見られたページ 上位20');
  L.push('');
  L.push('| # | ページ | 表示 | ユーザー | 前回比 |');
  L.push('|---:|---|---:|---:|---:|');
  sorted.slice(0, 20).forEach(([p, v], i) => {
    L.push(`| ${i + 1} | ${p} | ${v[0]} | ${v[1]} | ${pct(v[0], (pages.prev.get(p) || [0])[0])} |`);
  });
  L.push('');

  const zero = sorted.filter(([, v]) => v[0] <= 2);
  L.push(`## ほとんど見られていないページ（表示2回以下・${zero.length}件）`);
  L.push('');
  L.push(zero.length ? zero.map(([p]) => `- ${p}`).join('\n') : '- なし');
  L.push('');
  L.push('> 作ったのに読まれていないページ。一度告知して反応が無ければ、畳むか統合を検討する。');
  L.push('');

  L.push('## 発生したイベント');
  L.push('');
  L.push('| イベント | 回数 | 前回 |');
  L.push('|---|---:|---:|');
  for (const [k, v] of [...ev.cur.entries()].sort((a, b) => b[1][0] - a[1][0]).slice(0, 15)) {
    L.push(`| ${k} | ${v[0]} | ${(ev.prev.get(k) || [0])[0]} |`);
  }
  L.push('');

  const md = L.join('\n') + '\n';
  if (toStdout) { process.stdout.write(md); return; }

  fs.mkdirSync(OUT_DIR, { recursive: true });
  const out = path.join(OUT_DIR, `${today}-${days}days.md`);
  fs.writeFileSync(out, md);
  console.log(`書き出し: ${out}`);
  console.log(`\n全体 ${t[0]}表示 / ${t[1]}ユーザー（前期間比 ${pct(t[0], tp[0])}）`);
  console.log(`有料導線: 計算機${calcPv} → 送客${sel} / LP${kitPv} → 押下${chk}`);
}

main().catch((e) => fail(String(e && e.stack || e)));

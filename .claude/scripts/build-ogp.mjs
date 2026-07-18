// ============================================================
// build-ogp.mjs
//
// data/ogp.json（台帳）から各ページの OGP 画像を生成し、
// 各ページの og:image / twitter:image を書き換える。
// 通常は build-ogp.sh 経由で起動する。
//
//   node build-ogp.mjs              … 台帳の全ページを生成＋配線
//   node build-ogp.mjs --only foo   … img名 or page名に "foo" を含むものだけ
//   node build-ogp.mjs --check      … 生成せず、欠け（画像未生成/台帳未登録）を報告
//   node build-ogp.mjs --no-wire    … 画像生成のみ（HTMLは触らない）
//
// 依存: playwright（.claude/scripts/node_modules）, sips（あれば2x→等倍で高精細化）
// ============================================================
import { chromium } from 'playwright';
import { execFileSync, spawnSync } from 'node:child_process';
import { readFileSync, writeFileSync, existsSync, mkdtempSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';
import path from 'node:path';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(SCRIPT_DIR, '../..');
const TEMPLATE = path.join(SCRIPT_DIR, 'ogp-template.html');
const LEDGER = path.join(REPO, 'data', 'ogp.json');
const BASE = 'https://kizukikumitate.com/';

const args = process.argv.slice(2);
const CHECK = args.includes('--check');
const NOWIRE = args.includes('--no-wire');
const onlyIdx = args.indexOf('--only');
const ONLY = onlyIdx >= 0 ? args[onlyIdx + 1] : null;

const ledger = JSON.parse(readFileSync(LEDGER, 'utf8'));
let pages = ledger.pages;
if (ONLY) pages = pages.filter(p => p.img.includes(ONLY) || p.page.includes(ONLY));

const hasSips = spawnSync('sips', ['--help']).status === 0 || process.platform === 'darwin';

// ---- og:image / twitter:image をページ head に配線（冪等） ----
function wire(pg, img) {
  const f = path.join(REPO, pg);
  let h = readFileSync(f, 'utf8');
  const url = BASE + img;
  const before = h;
  if (/property="og:image"\s+content="/.test(h)) {
    h = h.replace(/(property="og:image"\s+content=")[^"]*(")/, `$1${url}$2`);
  } else {
    // 無ければ <title> の直後に一式を挿入
    const block =
      `<link rel="canonical" href="${BASE}${pg.replace(/index\.html$/, '').replace(/^/, '')}">\n` +
      `<meta property="og:type" content="website">\n` +
      `<meta property="og:image" content="${url}">\n` +
      `<meta property="og:image:width" content="1200">\n` +
      `<meta property="og:image:height" content="630">\n` +
      `<meta name="twitter:card" content="summary_large_image">\n` +
      `<meta name="twitter:image" content="${url}">\n`;
    h = h.replace(/(<title>.*?<\/title>\s*\n)/s, `$1${block}`);
  }
  h = h.replace(/(property="og:image:width"\s+content=")[^"]*(")/, '$11200$2');
  h = h.replace(/(property="og:image:height"\s+content=")[^"]*(")/, '$1630$2');
  if (/name="twitter:image"\s+content="/.test(h)) {
    h = h.replace(/(name="twitter:image"\s+content=")[^"]*(")/, `$1${url}$2`);
  }
  h = h.replace(/(name="twitter:card"\s+content=")summary(")/, '$1summary_large_image$2');
  if (h !== before) writeFileSync(f, h);
  return h !== before;
}

if (CHECK) {
  const problems = [];
  for (const p of ledger.pages) {
    if (!existsSync(path.join(REPO, p.page))) problems.push(`台帳にあるがページが無い: ${p.page}`);
    if (!existsSync(path.join(REPO, p.img))) problems.push(`画像が未生成: ${p.img}（build-ogp.sh --only ${p.img}）`);
  }
  // 台帳未登録で汎用 ogp.png のままのページを検出（_exclude は意図的な汎用のため除外）
  const listed = new Set(ledger.pages.map(p => p.page));
  const excluded = new Set(Object.keys(ledger._exclude || {}));
  const tracked = execFileSync('git', ['-C', REPO, 'ls-files', '*.html'], { encoding: 'utf8' }).split('\n').filter(Boolean);
  for (const f of tracked) {
    if (/(mockup|ogp-generator|preview-diagram|od-overflow-check|template)/.test(path.basename(f))) continue;
    if (listed.has(f) || excluded.has(f)) continue;
    const h = readFileSync(path.join(REPO, f), 'utf8');
    if (/og:image"\s+content="https:\/\/kizukikumitate\.com\/ogp\.png"/.test(h))
      problems.push(`台帳未登録（汎用ogp.pngのまま）: ${f}`);
  }
  if (problems.length) { console.log('OGP 課題:\n  ' + problems.join('\n  ')); process.exit(1); }
  console.log('✅ OGP 台帳・画像・配線に欠けなし'); process.exit(0);
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: hasSips ? 2 : 1 });
await page.goto('file://' + TEMPLATE, { waitUntil: 'networkidle' });
const tmp = mkdtempSync(path.join(tmpdir(), 'ogp-'));

let n = 0, wired = 0;
for (const p of pages) {
  await page.evaluate(o => {
    document.body.setAttribute('data-theme', o.theme || 'paper');
    document.body.setAttribute('data-template', o.template || 'standard');
    document.body.style.setProperty('--acc', o.acc);
    document.getElementById('eyebrow').textContent = o.eyebrow;
    document.getElementById('title').innerHTML = o.title;
    document.getElementById('sub').textContent = o.sub;
  }, p);
  await page.waitForTimeout(120);
  const dest = path.join(REPO, p.img);
  if (hasSips) {
    const raw = path.join(tmp, p.img);
    await page.screenshot({ path: raw, clip: { x: 0, y: 0, width: 1200, height: 630 } });
    execFileSync('sips', ['-z', '630', '1200', raw, '--out', dest], { stdio: 'ignore' });
  } else {
    await page.screenshot({ path: dest, clip: { x: 0, y: 0, width: 1200, height: 630 } });
  }
  n++;
  const changed = NOWIRE ? false : wire(p.page, p.img);
  if (changed) wired++;
  console.log(`  ✓ ${p.img}${changed ? '  (配線更新)' : ''}`);
}
await browser.close();
console.log(`完了: 画像 ${n} 枚生成${NOWIRE ? '' : ` / ${wired} ページ配線`}（対象 ${pages.length}）`);

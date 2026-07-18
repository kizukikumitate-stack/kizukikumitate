// ローカルHTML/SVGを指定ビューポートでPNGレンダリングして目視検証するヘルパー。
//
// 使い方（★必ず .claude/scripts/ にコピーして、そのディレクトリで実行する。
//   playwright は .claude/scripts/node_modules で解決されるため）:
//   node .claude/scripts/shot.mjs <file.html絶対パス> <out.png> [幅=1366] [高さ=820] [hoverセレクタ]
//
// ★この環境ではサンドボックス下でChromiumが起動できないので、Bashツールの
//   dangerouslyDisableSandbox: true を付けて実行すること（build-ogp.sh と同じ事情）。
//
// 例:
//   node .claude/scripts/shot.mjs "$PWD/rocket-map.html" out-pc.png 1366 820 "#spot-archive-w"
//   node .claude/scripts/shot.mjs "$PWD/rocket-map.html" out-mobile.png 390 1500
import { chromium } from 'playwright';

const file  = process.argv[2];
const out   = process.argv[3];
const width = parseInt(process.argv[4] || '1366', 10);
const height= parseInt(process.argv[5] || '820', 10);
const hover = process.argv[6];

if (!file || !out) {
  console.error('usage: node shot.mjs <file.html> <out.png> [width] [height] [hoverSelector]');
  process.exit(1);
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
const errors = [];
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
page.on('pageerror', e => errors.push(String(e)));

await page.goto('file://' + file, { waitUntil: 'networkidle' });
await page.waitForTimeout(500);
if (hover) { try { await page.hover(hover); await page.waitForTimeout(400); } catch (e) { console.log('hover miss:', e.message); } }

await page.screenshot({ path: out });   // ビューポート（=1画面目）。全体は fullPage:true に変える
await browser.close();
console.log('saved', out, '| JS errors:', errors.length ? errors.join(' | ') : 'none');

// ローカルHTML/SVGを指定ビューポートでPNGレンダリングして目視検証するヘルパー。
//
// 使い方（★必ず .claude/scripts/ にコピーして、そのディレクトリで実行する。
//   playwright は .claude/scripts/node_modules で解決されるため）:
//   node .claude/scripts/shot.mjs <file.html絶対パス> <out.png> [幅=1366] [高さ=900] [hoverセレクタ] [clipセレクタ] [clip高さ割合=1] [clip上端オフセット割合=0]
//
// ★この環境ではサンドボックス下でChromiumが起動できないので、Bashツールの
//   dangerouslyDisableSandbox: true を付けて実行すること（build-ogp.sh と同じ事情）。
//
// rocket-map.html はページ冒頭にカウントダウンのイントロ演出が入る。本ヘルパーは
// 読み込み後に「スキップ」ボタンを自動クリックし、#rocket-map セクションまでスクロール
// してから撮影する（どちらも best-effort。無ければ無視）。
//
// 例:
//   node .claude/scripts/shot.mjs "$PWD/rocket-map.html" out-pc.png 1366 1000            # PC全景
//   node .claude/scripts/shot.mjs "$PWD/rocket-map.html" out-mob.png 390 1500            # モバイル全景
//   node .claude/scripts/shot.mjs "$PWD/rocket-map.html" zoom.png 390 1500 "" ".sky" 0.55 0.04  # 縦SVG上部を拡大
import { chromium } from 'playwright';

const file  = process.argv[2];
const out   = process.argv[3];
const width = parseInt(process.argv[4] || '1366', 10);
const height= parseInt(process.argv[5] || '900', 10);
const hover = process.argv[6];
const clipSel = process.argv[7];                       // 指定するとその要素のbboxにクリップ（拡大検証用）
const clipFrac= parseFloat(process.argv[8] || '1');    // クリップ高さ＝bbox高さ×この割合
const clipOff = parseFloat(process.argv[9] || '0');    // クリップ上端＝bbox上端＋bbox高さ×この割合

if (!file || !out) {
  console.error('usage: node shot.mjs <file.html> <out.png> [width] [height] [hoverSelector] [clipSelector] [clipFrac] [clipOff]');
  process.exit(1);
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: clipSel ? 2 : 1 });
const errors = [];
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
page.on('pageerror', e => errors.push(String(e)));

await page.goto('file://' + file, { waitUntil: 'networkidle' });
await page.waitForTimeout(400);
try { await page.click('text=スキップ', { timeout: 1500 }); } catch (e) {}   // イントロ演出を飛ばす
await page.waitForTimeout(1500);                                             // フェード完了待ち
try { await page.locator('#rocket-map').scrollIntoViewIfNeeded(); } catch (e) {}
await page.waitForTimeout(400);
if (hover) { try { await page.hover(hover); await page.waitForTimeout(400); } catch (e) { console.log('hover miss:', e.message); } }

if (clipSel) {
  const el = await page.$(clipSel);
  await el.scrollIntoViewIfNeeded();
  const b = await el.boundingBox();
  await page.screenshot({ path: out, clip: { x: b.x, y: b.y + b.height * clipOff, width: b.width, height: b.height * clipFrac } });
} else {
  await page.screenshot({ path: out });   // ビューポート（=1画面目）。全体は fullPage:true に変える
}
await browser.close();
console.log('saved', out, '| JS errors:', errors.length ? errors.join(' | ') : 'none');

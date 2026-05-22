// ============================================================
// mobile-screenshot.mjs
//
// Playwright で iPhone 14 Pro viewport の full-page スクショを取得する。
// mobile-preflight.sh から起動される（URL / OUTPUT は env で受け取る）。
// ============================================================

import { chromium, devices } from 'playwright';

const url = process.env.URL;
const output = process.env.OUTPUT;

if (!url || !output) {
  console.error('❌ URL / OUTPUT env が必要です');
  process.exit(2);
}

// 初回起動時は browsers が無いことがあるので install を試みる
let browser;
try {
  browser = await chromium.launch();
} catch (err) {
  if (String(err).includes('Executable doesn\'t exist')) {
    console.error('🔽 Chromium が未インストール。`npx -y playwright@1 install chromium` を実行してください');
    process.exit(3);
  }
  throw err;
}

const context = await browser.newContext({
  ...devices['iPhone 14 Pro'],
});
const page = await context.newPage();

console.log(`   → ${url} を開いています`);
await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });

// 遅延読み込み画像の安定化のため少し待つ
await page.waitForTimeout(800);

await page.screenshot({
  path: output,
  fullPage: true,
});

await browser.close();

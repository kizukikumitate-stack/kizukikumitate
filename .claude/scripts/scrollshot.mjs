import { chromium } from 'playwright';
const [,, file, out, y] = process.argv;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
await page.goto('file://' + file, { waitUntil: 'networkidle' });
await page.evaluate(yy => window.scrollTo(0, +yy), y);
await page.waitForTimeout(800);
await page.screenshot({ path: out });
await browser.close();

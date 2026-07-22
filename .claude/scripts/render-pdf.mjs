// HTML → A4 PDF レンダラ（gen-jirei-pdf.py から呼ばれる）
// usage: node render-pdf.mjs <input.html> <output.pdf>
import { chromium } from 'playwright';
const [,, input, output] = process.argv;
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('file://' + input, { waitUntil: 'networkidle' });
await page.pdf({ path: output, format: 'A4', printBackground: true,
  margin: { top: '0', bottom: '0', left: '0', right: '0' } });
await browser.close();
console.log('pdf:', output);

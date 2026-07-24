import { chromium } from 'playwright';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
await page.goto('file://' + process.argv[2], { waitUntil: 'networkidle' });
const bad = await page.evaluate(() => {
  const vw = document.documentElement.clientWidth, out = [];
  document.querySelectorAll('*').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.right > vw + 2 || r.left < -2) out.push(`${el.tagName}.${[...el.classList].join('.')} L${Math.round(r.left)} R${Math.round(r.right)} W${Math.round(r.width)}`);
  });
  return out.slice(0, 20);
});
console.log(bad.join('\n'));
await browser.close();

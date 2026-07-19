import { chromium } from 'playwright';
const out = process.argv[2];
const view = process.argv[3] === 'mobile';
const b = await chromium.launch();
const p = await b.newPage({ viewport: view ? { width: 390, height: 844 } : { width: 1300, height: 900 } });
await p.goto('file:///Users/morimotoyasuhito/kizukikumitate/index.html', { waitUntil: 'networkidle' });
if (view) {
  await p.click('#hamburger');
  await p.waitForTimeout(300);
  const accs = await p.$$('.mobile-acc-toggle');
  for (const t of accs) { const tx = await t.textContent(); if (tx && tx.includes('世界の知恵')) { await t.click(); break; } }
  await p.waitForTimeout(300);
  await p.screenshot({ path: out, fullPage: true });
} else {
  const toggles = await p.$$('.nav-dropdown-toggle');
  for (const t of toggles) { const tx = await t.textContent(); if (tx && tx.includes('世界の知恵')) { await t.hover(); break; } }
  await p.waitForTimeout(500);
  await p.screenshot({ path: out, clip: { x: 470, y: 0, width: 800, height: 700 } });
}
await b.close();
console.log('shot ok');

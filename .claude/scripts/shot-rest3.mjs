import { chromium } from 'playwright';
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1280, height: 1100 } });
await p.goto('file:///Users/morimotoyasuhito/kizukikumitate/rest-productivity-zukan.html');
await p.locator('.dataroom').scrollIntoViewIfNeeded();
await p.waitForTimeout(800);
await p.locator('.dataroom').screenshot({ path: '/private/tmp/claude/rest3-dataroom.png' });
await b.close();

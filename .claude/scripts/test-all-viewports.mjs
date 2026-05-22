// 複数 viewport で行頭句読点・widow を検出
import { webkit } from 'playwright';

const url = process.env.URL || 'http://localhost:8080/democracy-fitness-camp-0811.html';
const viewports = [
  { name: 'iPhone SE (375)', width: 375, height: 667 },
  { name: 'iPhone 13 mini (375)', width: 375, height: 812 },
  { name: 'iPhone 14 Pro (393)', width: 393, height: 852 },
  { name: 'iPhone 14 Pro Max (430)', width: 430, height: 932 },
];

const browser = await webkit.launch();
for (const vp of viewports) {
  const context = await browser.newContext({
    viewport: { width: vp.width, height: vp.height },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
  });
  const page = await context.newPage();
  await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(500);

  const issues = await page.evaluate(() => {
    const FORBIDDEN = /^[、。」）】］〕｝・]/;
    const JP = /[　-〿぀-ゟ゠-ヿ㐀-䶿一-鿿豈-﫿]/;
    const cands = Array.from(document.querySelectorAll(
      'p, h1, h2, h3, h4, h5, h6, li, dt, dd, blockquote, ' +
      '[class*="-body"], [class*="-text"], [class*="-lead"], [class*="-manifesto"], ' +
      '[class*="-bridge"], [class*="-callout"], [class*="-note"], [class*="-quote"], ' +
      '[class*="-desc"], [class*="-sub"], [class*="-message"], [class*="-title"]'
    ));
    const findings = [];
    for (const el of cands) {
      const text = el.textContent || '';
      if (!JP.test(text)) continue;
      const hasDirect = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
      if (!hasDirect) continue;
      const rect = el.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) continue;

      // 各行先頭文字を取得
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      const chars = [];
      let n;
      while ((n = walker.nextNode())) for (let i = 0; i < n.textContent.length; i++) chars.push({n, i});
      if (chars.length === 0) continue;
      const tol = 3;
      let curY = null;
      const firsts = [];
      for (const c of chars) {
        const r = document.createRange();
        r.setStart(c.n, c.i); r.setEnd(c.n, c.i + 1);
        const rr = r.getBoundingClientRect();
        if (rr.width === 0) continue;
        if (curY === null || Math.abs(rr.y - curY) > tol) {
          curY = rr.y;
          firsts.push({char: c.n.textContent[c.i], y: rr.y});
        }
      }
      const bad = firsts.slice(1).filter(f => FORBIDDEN.test(f.char));
      if (bad.length > 0) {
        const sel = el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ').filter(c=>c).join('.') : '');
        const cs = getComputedStyle(el);
        findings.push({
          selector: sel.substring(0, 60),
          bad: bad.map(b => b.char).join(' / '),
          firsts: firsts.map(f => f.char).join(''),
          textWrap: cs.textWrap,
          lineBreak: cs.lineBreak,
          wordBreak: cs.wordBreak,
          textPreview: text.substring(0, 40).replace(/\s+/g, ' '),
        });
      }
    }
    return findings;
  });

  console.log(`\n══ ${vp.name} (${vp.width}px) ══`);
  if (issues.length === 0) {
    console.log('  ✅ 行頭句読点なし');
  } else {
    console.log(`  ⚠️  ${issues.length} 件`);
    for (const i of issues) {
      console.log(`    [${i.bad}] <${i.selector}>`);
      console.log(`       textWrap=${i.textWrap} lineBreak=${i.lineBreak}`);
      console.log(`       行先頭文字列: ${i.firsts}`);
      console.log(`       text: "${i.textPreview}..."`);
    }
  }
  await context.close();
}
await browser.close();

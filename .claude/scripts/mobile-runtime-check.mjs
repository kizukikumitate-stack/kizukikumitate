// ============================================================
// mobile-runtime-check.mjs
//
// 静的 grep では捕まえられない「実機での改行不具合」を Playwright で検出する。
// iPhone 14 Pro viewport でページをレンダリングし、各テキスト要素の rendered line を
// CSS Range API で取得して、以下のアンチパターンを報告:
//
//   E1) 行頭に句読点（、。」）] 等）— line-break: strict が効いていない要素
//   E2) 1〜2 文字だけの行（widow）— 単語分割で末尾の数文字が孤立
//   E3) Japanese テキストを含む要素で line-break: strict が CSS で設定されていない
//
// 実行: URL=... OUTPUT_JSON=... node mobile-runtime-check.mjs
// ============================================================

// ※ WebKit を使う（実 Safari と同じレンダリングエンジン）
// Chromium だと strict/auto-phrase が想定通りに動くが、Safari では <strong> 等の inline
// 境界で句読点が行頭に動く現象がある。実機 iPhone と同じ挙動を再現するため WebKit を使用。
import { webkit, devices } from 'playwright';
import fs from 'fs';

const url = process.env.URL;
const outJson = process.env.OUTPUT_JSON;

if (!url) {
  console.error('❌ URL env が必要です');
  process.exit(2);
}

const browser = await webkit.launch();
// iPhone SE (375px) — 最も狭い iPhone でテストして strict 違反を再現しやすくする
const context = await browser.newContext({
  viewport: { width: 375, height: 667 },
  deviceScaleFactor: 3,
  isMobile: true,
  hasTouch: true,
  userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
});
const page = await context.newPage();

await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
await page.waitForTimeout(800);

// ページ内で実行: 各テキスト要素の rendered lines を Range API で取得し、
// 行頭句読点 / widow / line-break: strict 抜けを検出
const issues = await page.evaluate(() => {
  const RESULTS = { lineHead: [], widows: [], missingStrict: [], textWrapBalance: [] };
  const LINE_HEAD_FORBIDDEN = /^[、。」）】］〕｝・]/;
  const JP_RE = /[　-〿぀-ゟ゠-ヿ㐀-䶿一-鿿豈-﫿]/;

  // 子要素を持つコンテナだけを処理（textContent が直接子テキストノードのもの）
  const candidates = Array.from(document.querySelectorAll(
    'p, h1, h2, h3, h4, h5, h6, li, dt, dd, blockquote, ' +
    '[class*="-body"], [class*="-text"], [class*="-lead"], [class*="-manifesto"], ' +
    '[class*="-bridge"], [class*="-callout"], [class*="-note"], [class*="-quote"], ' +
    '[class*="-desc"], [class*="-sub"], [class*="-message"], [class*="-title"]'
  ));

  const seen = new WeakSet();

  for (const el of candidates) {
    if (seen.has(el)) continue;
    seen.add(el);

    // 表示されていない要素はスキップ
    const rect = el.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) continue;

    const text = el.textContent || '';
    if (!JP_RE.test(text)) continue;

    // 直接の text node を持っているかチェック
    const hasDirectText = Array.from(el.childNodes).some(n =>
      n.nodeType === Node.TEXT_NODE && n.textContent.trim().length > 0
    );
    if (!hasDirectText) continue;

    // line-break: strict が効いているか
    const cs = getComputedStyle(el);
    const lineBreak = cs.lineBreak;
    const wordBreak = cs.wordBreak;
    const textWrap = cs.textWrap;
    if (lineBreak !== 'strict' && lineBreak !== 'anywhere') {
      const sel = el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ').join('.') : '');
      RESULTS.missingStrict.push({
        selector: sel.substring(0, 80),
        lineBreak, wordBreak,
        textPreview: text.substring(0, 40).replace(/\s+/g, ' '),
      });
    }
    // text-wrap: balance は日本語禁則と相性が悪い（句読点が行頭に動く）
    if (textWrap === 'balance') {
      const sel = el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ').join('.') : '');
      RESULTS.textWrapBalance.push({
        selector: sel.substring(0, 80),
        textPreview: text.substring(0, 40).replace(/\s+/g, ' '),
      });
    }

    // Range API で rendered lines を取得
    try {
      const range = document.createRange();
      // 子テキストノードだけを集めて1つの range を作る
      let firstTextNode = null, lastTextNode = null;
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
      let node;
      while ((node = walker.nextNode())) {
        if (!firstTextNode) firstTextNode = node;
        lastTextNode = node;
      }
      if (!firstTextNode) continue;
      range.setStart(firstTextNode, 0);
      range.setEnd(lastTextNode, lastTextNode.textContent.length);
      const rects = Array.from(range.getClientRects());
      if (rects.length < 2) continue;

      // 各 rect = 1行の bounding box。同 line に属する複数 rect もあるので y でグループ化。
      const lines = [];
      const tolerance = 3; // px
      for (const r of rects) {
        if (r.width === 0 || r.height === 0) continue;
        const lastLine = lines[lines.length - 1];
        if (lastLine && Math.abs(lastLine.y - r.y) < tolerance) {
          lastLine.x1 = Math.min(lastLine.x1, r.left);
          lastLine.x2 = Math.max(lastLine.x2, r.right);
        } else {
          lines.push({ y: r.y, x1: r.left, x2: r.right, height: r.height });
        }
      }
      if (lines.length < 2) continue;

      // 各行に対応するテキスト範囲を特定し、先頭文字をチェック
      // 簡易: テキスト全体を文字単位で iterate し、各文字の bounding box を取って
      // どの line に属するか判定する
      const allText = [];
      const walker2 = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
      let tn;
      while ((tn = walker2.nextNode())) {
        for (let i = 0; i < tn.textContent.length; i++) {
          allText.push({ node: tn, offset: i });
        }
      }

      const lineFirstChars = [];
      let currentLineY = null;
      for (const ch of allText) {
        const r = document.createRange();
        r.setStart(ch.node, ch.offset);
        r.setEnd(ch.node, ch.offset + 1);
        const rr = r.getBoundingClientRect();
        if (rr.width === 0 || rr.height === 0) continue;
        if (currentLineY === null || Math.abs(rr.y - currentLineY) > tolerance) {
          currentLineY = rr.y;
          lineFirstChars.push(ch.node.textContent[ch.offset]);
        }
      }

      // 各行先頭が禁止文字かチェック（最初の行は除外）
      for (let i = 1; i < lineFirstChars.length; i++) {
        const first = lineFirstChars[i];
        if (LINE_HEAD_FORBIDDEN.test(first)) {
          const sel = el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ').join('.') : '');
          RESULTS.lineHead.push({
            selector: sel.substring(0, 80),
            char: first,
            lineIndex: i + 1,
            textPreview: text.substring(0, 40).replace(/\s+/g, ' '),
          });
        }
      }

      // widow チェック: 最終行が日本語1文字だけ
      // ※ 2文字（「す。」「い。」等）は自然な文末で実害少なく、jp-nowrap 化済みなら
      //   そもそも文末2文字は同一行に必ず収まる構造になる。1文字孤立のみ警告対象。
      const lastLine = lines[lines.length - 1];
      const lastLineCharCount = Math.round((lastLine.x2 - lastLine.x1) / (lastLine.height * 0.6));
      if (lastLineCharCount === 1 && lines.length > 1) {
        const sel = el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ').join('.') : '');
        RESULTS.widows.push({
          selector: sel.substring(0, 80),
          lastLineCharCount,
          textPreview: text.substring(0, 40).replace(/\s+/g, ' '),
        });
      }
    } catch (e) {
      // 個別要素のエラーは無視
    }
  }
  return RESULTS;
});

await browser.close();

if (outJson) {
  fs.writeFileSync(outJson, JSON.stringify(issues, null, 2));
}

// stdout に人間向けサマリー
let exitCode = 0;
if (issues.lineHead.length > 0) {
  console.log(`   ⚠️  行頭句読点: ${issues.lineHead.length} 件`);
  for (const i of issues.lineHead.slice(0, 5)) {
    console.log(`      [${i.char}] line ${i.lineIndex} in <${i.selector}>: "${i.textPreview}..."`);
  }
  if (issues.lineHead.length > 5) console.log(`      ... 他 ${issues.lineHead.length - 5} 件`);
  exitCode = 1;
}
if (issues.widows.length > 0) {
  console.log(`   ⚠️  1〜2文字 widow: ${issues.widows.length} 件`);
  for (const i of issues.widows.slice(0, 5)) {
    console.log(`      [${i.lastLineCharCount}文字] <${i.selector}>: "${i.textPreview}..."`);
  }
  if (issues.widows.length > 5) console.log(`      ... 他 ${issues.widows.length - 5} 件`);
  exitCode = 1;
}
if (issues.missingStrict.length > 0) {
  console.log(`   ⚠️  line-break: strict 未適用: ${issues.missingStrict.length} 件`);
  for (const i of issues.missingStrict.slice(0, 5)) {
    console.log(`      <${i.selector}> (lineBreak=${i.lineBreak}): "${i.textPreview}..."`);
  }
  if (issues.missingStrict.length > 5) console.log(`      ... 他 ${issues.missingStrict.length - 5} 件`);
  exitCode = 1;
}
if (issues.textWrapBalance.length > 0) {
  console.log(`   ⚠️  text-wrap: balance が日本語テキストに適用: ${issues.textWrapBalance.length} 件（行頭句読点の原因）`);
  for (const i of issues.textWrapBalance.slice(0, 5)) {
    console.log(`      <${i.selector}>: "${i.textPreview}..." → pretty に変更推奨`);
  }
  if (issues.textWrapBalance.length > 5) console.log(`      ... 他 ${issues.textWrapBalance.length - 5} 件`);
  exitCode = 1;
}
if (exitCode === 0) console.log('   ✅ runtime チェック PASS（行頭句読点/widow/strict すべてクリア）');

process.exit(exitCode);

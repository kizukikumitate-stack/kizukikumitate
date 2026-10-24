#!/usr/bin/env node
/**
 * 日本語の読み物ページを「実測」するための計測器。
 *
 *   node .claude/scripts/measure-typography.mjs <file.html> [--w 390,768,1280] [--cmd font|fill|length|all]
 *
 * 目で見て直すと必ず取り残しが出る（「本文だけ直して見出しを直し忘れる」「クラスの無い
 * 段落が残る」）。数字で出してから直し、直したら同じ数字で確かめる。
 *
 *   font   … 文字サイズの分布。「何pxに何文字あるか」。読ませる文章が 14px 未満に
 *            溜まっていたらスマホで読めない。インライン style の font-size も拾う。
 *   fill   … 行の充填率。各ブロックの「最終行を除く内部行」が行幅の何%まで埋まって
 *            いるか。右端のガタつきはこれで出る。80%未満が残っていたら未処理。
 *   length … 総文字数・読了分数・章ごとの高さ（スマホ何画面分か）。どの章が重いか。
 *
 * 備考: Playwright は /opt/npm-tools に入っている（リポジトリの node_modules ではない）。
 */
import { chromium } from '/opt/npm-tools/node_modules/playwright/index.mjs';
import { resolve } from 'node:path';

const argv = process.argv.slice(2);
const file = argv.find((a) => !a.startsWith('--'));
if (!file) {
  console.error('使い方: node .claude/scripts/measure-typography.mjs <file.html> [--w 390,768] [--cmd font|fill|length|all]');
  process.exit(1);
}
const arg = (name, def) => {
  const i = argv.indexOf('--' + name);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : def;
};
const widths = arg('w', '390,1280').split(',').map(Number);
const cmd = arg('cmd', 'all');
const url = 'file://' + resolve(file);
/** 記事本体のルート。このサイトは <article class="col"> が本文、無ければ body 全体 */
const ROOT = arg('root', '.col');

const browser = await chromium.launch();

async function open(w) {
  const page = await browser.newPage({ viewport: { width: w, height: 844 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(700);
  return { page, errors };
}

// ---------------------------------------------------------------- font
async function font(w) {
  const { page } = await open(w);
  const r = await page.evaluate((ROOT) => {
    const root = document.querySelector(ROOT) || document.body;
    const dist = {};
    root.querySelectorAll('*').forEach((el) => {
      const own = [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim());
      if (!own.length) return;
      const cs = getComputedStyle(el);
      const k = parseFloat(cs.fontSize).toFixed(1);
      const chars = own.map((n) => n.textContent.trim()).join('').length;
      dist[k] = dist[k] || { n: 0, chars: 0, ex: '', op: 1 };
      dist[k].n++;
      dist[k].chars += chars;
      dist[k].op = Math.min(dist[k].op, parseFloat(cs.opacity));
      if (!dist[k].ex) dist[k].ex = el.textContent.trim().slice(0, 20);
    });
    return { dist, scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth };
  }, ROOT);
  console.log(`\n■ 文字サイズの分布  ${w}px   横はみ出し: ${r.scrollW > r.clientW ? `あり (${r.scrollW}>${r.clientW})` : 'なし'}`);
  let small = 0;
  Object.entries(r.dist)
    .sort((a, b) => +a[0] - +b[0])
    .forEach(([k, v]) => {
      if (+k < 14) small += v.chars;
      const warn = +k < 12 && v.chars > 40 ? ' ←文章なら小さすぎ' : '';
      console.log(`  ${k.padStart(6)}px  要素${String(v.n).padStart(4)}  文字${String(v.chars).padStart(5)}  最小opacity ${v.op.toFixed(2)}  例:${v.ex}${warn}`);
    });
  console.log(`  → 14px未満に ${small} 文字。ラベル・出典以外がここにあるなら上げる。`);
  await page.close();
}

// ---------------------------------------------------------------- fill
async function fill(w) {
  const { page } = await open(w);
  const rows = await page.evaluate((ROOT) => {
    const root = document.querySelector(ROOT) || document.body;
    const sel = (el) => {
      const b = [];
      for (let e = el; e && e !== document.body && b.length < 3; e = e.parentElement)
        b.unshift(e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/).join('.') : ''));
      return b.join(' > ');
    };
    const out = [];
    root.querySelectorAll('p, li, div, span, b, a').forEach((el) => {
      const own = [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim());
      if (!own.length) return;
      const txt = el.textContent.trim();
      if (txt.length < 20) return;
      const range = document.createRange();
      range.selectNodeContents(el);
      const rects = [...range.getClientRects()].filter((x) => x.width > 2 && x.height > 2);
      const lines = [];
      rects.forEach((x) => {
        const L = lines.find((l) => Math.abs(l.top - x.top) < 3);
        if (L) { L.left = Math.min(L.left, x.left); L.right = Math.max(L.right, x.right); }
        else lines.push({ top: x.top, left: x.left, right: x.right });
      });
      if (lines.length < 2) return;
      const box = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      const avail = box.width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      const fills = lines.slice(0, -1).map((l) => (l.right - l.left) / avail);
      out.push({
        sel: sel(el), wb: cs.wordBreak, ta: cs.textAlign, fs: cs.fontSize, n: lines.length,
        worst: Math.round(Math.min(...fills) * 100),
        avg: Math.round((fills.reduce((a, c) => a + c, 0) / fills.length) * 100),
        ex: txt.slice(0, 22),
      });
    });
    return out;
  }, ROOT);
  rows.sort((a, b) => a.worst - b.worst);
  const bad = rows.filter((r) => r.worst < 80);
  console.log(`\n■ 行の充填率  ${w}px   対象 ${rows.length} ブロック／80%未満 ${bad.length} ブロック`);
  rows.slice(0, 14).forEach((r) =>
    console.log(`  ${String(r.worst).padStart(3)}% avg${String(r.avg).padStart(3)}%  ${r.n}行 ${r.fs} wb=${r.wb.padEnd(8)} ta=${r.ta.padEnd(7)} ${r.sel.slice(-46).padEnd(46)} ${r.ex}`));
  if (bad.length) {
    const by = {};
    bad.forEach((r) => { const k = r.sel.split(' > ').slice(-2).join(' > '); by[k] = (by[k] || 0) + 1; });
    console.log('  内訳:');
    Object.entries(by).sort((a, b) => b[1] - a[1]).forEach(([k, v]) => console.log(`    ×${v}  ${k}`));
    console.log('  ※ chip や <br> を含むブロックは構造上短い行が出る（計測上の見かけ）。実物を見て判断する。');
  }
  await page.close();
}

// ---------------------------------------------------------------- length
async function length(w) {
  const { page } = await open(w);
  const r = await page.evaluate((ROOT) => {
    const root = document.querySelector(ROOT) || document.body;
    const H = document.documentElement.scrollHeight;
    const total = root.innerText.replace(/\s/g, '').length;
    const secs = [...root.querySelectorAll('section[id]')];
    const chaps = secs.map((s, i) => {
      const next = secs[i + 1];
      const top = s.getBoundingClientRect().top + window.scrollY;
      const bottom = next
        ? next.getBoundingClientRect().top + window.scrollY
        : root.getBoundingClientRect().bottom + window.scrollY;
      let chars = 0, n = s;
      while (n) {
        chars += (n.innerText || '').replace(/\s/g, '').length;
        n = n.nextElementSibling;
        if (!n || (n.tagName === 'SECTION' && n.id)) break;
      }
      return { id: s.id, title: (s.querySelector('h2,.st,.big,.lbl')?.innerText || '').replace(/​/g, '').slice(0, 20), chars, px: Math.round(bottom - top) };
    });
    return { H, total, chaps };
  }, ROOT);
  console.log(`\n■ 分量  ${w}px   本文 ${r.total} 字 ／ 全高 ${r.H.toLocaleString()}px（${Math.round(r.H / 844)} 画面）／ 読了およそ ${Math.round(r.total / 600)} 分（600字/分）`);
  if (r.chaps.length) {
    console.log('  章              文字   高さpx  画面');
    r.chaps.forEach((c) =>
      console.log(`  ${c.id.padEnd(5)} ${c.title.padEnd(14)} ${String(c.chars).padStart(5)} ${String(c.px).padStart(7)} ${String(Math.round(c.px / 844)).padStart(4)}`));
    console.log('  → 全体の15%を超える章は、切り出すか圧縮する候補。');
  }
  await page.close();
}

for (const w of widths) {
  if (cmd === 'font' || cmd === 'all') await font(w);
  if (cmd === 'fill' || cmd === 'all') await fill(w);
  if (cmd === 'length' || cmd === 'all') await length(w);
}
await browser.close();

#!/usr/bin/env node
/**
 * アクセス解析タグ（GA4）の網羅チェックと自動補完。
 *
 *   node .claude/scripts/analytics.mjs check   … 欠落ページを列挙して exit 1（pre-commitで使用）
 *   node .claude/scripts/analytics.mjs fix     … 欠落ページに <head> 直後へタグを挿入
 *
 * 「作ったのに計測できていないページ」を二度と作らないための番人。
 * 公開ページを新設したら、何もしなくてもここで捕まる。
 */

import { readdirSync, readFileSync, writeFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const GA_ID = 'G-2ECK6163X4';

/**
 * 計測対象外。被リンク0件かつ sitemap.xml 未掲載の内部ツール・モックアップのみ。
 * 公開ページをここに足さないこと（計測の穴はここから開く）。
 */
const EXCLUDE = new Set([
  'preview-diagram.html',
  'ogp-generator.html',
  'shimon-mockup.html',
  'structure-mockup.html',
  'themes-mockup.html',
  // ビルド用の素材・テンプレート。.nojekyll があるため配信自体はされるが、
  // 読み物として公開しているページではないので計測対象外。
  'series/_reference/BEM-diagnostic-form.html',
  'series/_pdf-build/template.html',
]);

const GA_BLOCK = `<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=${GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '${GA_ID}');
</script>`;

/**
 * 公開HTMLを集める。深さ制限は設けない。
 * .nojekyll があるため `_` 始まりのディレクトリも GitHub Pages では配信される。
 * 「深いから対象外」を作らず、除外は必ず EXCLUDE に明示させる。
 */
function collectPages(dir = '.') {
  const out = [];
  for (const name of readdirSync(dir)) {
    if (name.startsWith('.') || name === 'node_modules') continue;
    const path = dir === '.' ? name : join(dir, name);
    if (statSync(path).isDirectory()) {
      out.push(...collectPages(path));
      continue;
    }
    if (!name.endsWith('.html')) continue;
    if (EXCLUDE.has(path)) continue;
    out.push(path);
  }
  return out;
}

const hasTag = (html) => html.includes('googletagmanager.com/gtag/js');

function inject(html) {
  // <head> の直後に差し込む。既存66ページと同じ位置・同じ形に揃える。
  const m = html.match(/<head[^>]*>\n?/i);
  if (!m) return null;
  const at = m.index + m[0].length;
  return html.slice(0, at) + GA_BLOCK + '\n' + html.slice(at);
}

const mode = process.argv[2] ?? 'check';
const pages = collectPages();
const missing = pages.filter((p) => !hasTag(readFileSync(p, 'utf8')));

if (mode === 'fix') {
  const failed = [];
  for (const p of missing) {
    const next = inject(readFileSync(p, 'utf8'));
    if (next === null) { failed.push(p); continue; }
    writeFileSync(p, next);
    console.log(`  + ${p}`);
  }
  console.log(`\n解析タグを ${missing.length - failed.length} ページに追加しました（対象 ${pages.length} ページ）`);
  if (failed.length) {
    console.error(`\n<head> が見つからず手動対応が必要:\n${failed.map((p) => `  ! ${p}`).join('\n')}`);
    process.exit(1);
  }
} else {
  if (missing.length === 0) {
    console.log(`✓ 解析タグ: ${pages.length} ページすべてに設置済み`);
    process.exit(0);
  }
  console.error(`✗ アクセス解析タグが無いページが ${missing.length} 件あります:\n`);
  for (const p of missing) console.error(`  ${p}`);
  console.error(`\n修復:  node .claude/scripts/analytics.mjs fix`);
  console.error(`計測対象外にする場合は同スクリプトの EXCLUDE に追加してください。`);
  process.exit(1);
}

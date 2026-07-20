#!/usr/bin/env node
/**
 * アクセス解析タグ（GA4）の網羅チェックと自動補完。
 *
 *   node .claude/scripts/analytics.mjs check   … 欠落・IDちがいを列挙して exit 1（pre-commitで使用）
 *   node .claude/scripts/analytics.mjs fix     … 欠落ページに挿入し、古いIDは新IDへ差し替える
 *
 * 「作ったのに計測できていないページ」を二度と作らないための番人。
 * 公開ページを新設したら、何もしなくてもここで捕まる。
 *
 * 計測プロパティを引っ越すときは GA_ID を書き換えて fix を実行すれば全ページが揃う。
 * check が「IDちがい」も落とすので、差し替え漏れたページが残ることはない。
 */

import { readdirSync, readFileSync, writeFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

// 2026-07-20 引っ越し: 旧 G-2ECK6163X4（第三者アカウント TAPTEAM 内・管理権限なし）から、
// 自社所有のアカウント「きづきくみたて工房」のプロパティへ移行。
// 過去データは引き継げないが、計測の起点は元々2026-07-20なので実害は小さい。
const GA_ID = 'G-E3YZKY8DQG';

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

/** そのページに埋まっている計測IDを全部拾う（重複や旧IDの残骸を検出するため）。 */
const idsIn = (html) => [...new Set(html.match(/G-[A-Z0-9]{6,}/g) || [])];

/** GA_ID 以外のIDが混ざっていないか。引っ越し時の差し替え漏れを捕まえる。 */
const hasWrongId = (html) => hasTag(html) && idsIn(html).some((id) => id !== GA_ID);

function inject(html) {
  // <head> の直後に差し込む。既存66ページと同じ位置・同じ形に揃える。
  const m = html.match(/<head[^>]*>\n?/i);
  if (!m) return null;
  const at = m.index + m[0].length;
  return html.slice(0, at) + GA_BLOCK + '\n' + html.slice(at);
}

/** 旧IDを新IDへ差し替える。gtag/js?id= と gtag('config', …) の両方を置換。 */
function retag(html) {
  let out = html;
  for (const id of idsIn(html)) {
    if (id === GA_ID) continue;
    out = out.split(id).join(GA_ID);
  }
  return out;
}

const mode = process.argv[2] ?? 'check';
const pages = collectPages();
const read = (p) => readFileSync(p, 'utf8');
const missing = pages.filter((p) => !hasTag(read(p)));
const wrong = pages.filter((p) => hasWrongId(read(p)));

if (mode === 'fix') {
  const failed = [];
  for (const p of missing) {
    const next = inject(read(p));
    if (next === null) { failed.push(p); continue; }
    writeFileSync(p, next);
    console.log(`  + ${p}`);
  }
  for (const p of wrong) {
    writeFileSync(p, retag(read(p)));
    console.log(`  ↻ ${p}（旧ID → ${GA_ID}）`);
  }
  const added = missing.length - failed.length;
  console.log(`\n追加 ${added}ページ / 差し替え ${wrong.length}ページ（対象 ${pages.length} ページ・計測ID ${GA_ID}）`);
  if (failed.length) {
    console.error(`\n<head> が見つからず手動対応が必要:\n${failed.map((p) => `  ! ${p}`).join('\n')}`);
    process.exit(1);
  }
} else {
  if (missing.length === 0 && wrong.length === 0) {
    console.log(`✓ 解析タグ: ${pages.length} ページすべてに設置済み（計測ID ${GA_ID}）`);
    process.exit(0);
  }
  if (missing.length) {
    console.error(`✗ アクセス解析タグが無いページが ${missing.length} 件あります:\n`);
    for (const p of missing) console.error(`  ${p}`);
    console.error('');
  }
  if (wrong.length) {
    console.error(`✗ 別の計測IDが残っているページが ${wrong.length} 件あります（期待 ${GA_ID}）:\n`);
    for (const p of wrong) console.error(`  ${p}  → ${idsIn(read(p)).join(', ')}`);
    console.error('');
  }
  console.error(`修復:  node .claude/scripts/analytics.mjs fix`);
  console.error(`計測対象外にする場合は同スクリプトの EXCLUDE に追加してください。`);
  process.exit(1);
}

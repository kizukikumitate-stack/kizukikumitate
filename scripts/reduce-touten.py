#!/usr/bin/env python3
"""読点「、」を一段階減らす（機械的に安全な3パターンだけ）。

  R1 短い主語（〜は／〜が）のあとの読点
  R2 文頭の短い副詞・接続詞のあとの読点（まず、また、そして …）
  R3 短い句（〜で／〜では／〜には／〜から／〜として／〜に）のあとの読点

残すもの: 節の境目・並列・逆接の接続詞・引用（blockquote、「」の中）・
script/style・属性値・自動生成ブロック（NAV/FOOTER/KAIYU/SHELF など）。
見出し(h1〜h3)は、1文に候補が1つだけのときに限って外す。

使い方:
  python3 scripts/reduce-touten.py --report out.tsv          # 確認のみ
  python3 scripts/reduce-touten.py --write --report out.tsv  # 書き換え
  python3 scripts/reduce-touten.py --write a.html b.html     # ファイル指定
要: pip install janome
"""
import argparse
import glob
import os
import re
import sys

from janome.tokenizer import Tokenizer

TOK = Tokenizer()

SKIP_DIRS = ('_to_delete/', 'series/_reference/', 'series/_pdf-build/', '.claude/',
             'node_modules/', 'oem/', 'salary-kit-dl-92kf7m/')
SKIP_FILES = {'preview-diagram.html', 'od-overflow-check.html', 'ogp-generator.html',
              # 参加者の声＝他者の発言なので触らない
              'democracy-fitness-voices.html'}
GENERATED = ('NAV', 'FOOTER', 'KAIYU', 'SHELF', 'CALC-COMMON', 'SERIES', 'TALK', 'ZUKAI-SERIES')

INLINE = {'a', 'b', 'strong', 'em', 'i', 'span', 'mark', 'u', 'small', 'sup', 'sub', 'ruby',
          'rt', 'rp', 'rb', 'code', 'abbr', 'wbr', 'font', 'ins', 'del', 's', 'time', 'label'}
QUOTE_TAGS = {'blockquote', 'q', 'cite', 'pre', 'code', 'textarea', 'svg', 'noscript', 'template'}
HEADINGS = {'h1', 'h2', 'h3'}

R2_WORDS = {'まず', 'また', 'そして', 'さらに', '次に', 'つぎに', 'つまり', '実は', 'そこで',
            '特に', 'とくに', 'たとえば', '例えば', 'もちろん', 'ちなみに', '最後に', '同時に',
            'そのため', 'だから', 'すると', 'そのうえ', '加えて', 'まずは', '実際', '実際に'}
KEEP_HEAD = ('逆に', 'むしろ', '一方', '反対に', 'しかし', 'ただ', 'ところが', 'とはいえ', 'でも', 'けれど')
INTERROG = ('誰', '何', 'どこ', 'いつ', 'どの', 'どう', 'なぜ')
SENT_END = '。！？!?'
HIRA = re.compile(r'[ぁ-ん]')

TOKEN_RE = re.compile(
    r'<!--.*?-->|<script\b.*?</script\s*>|<style\b.*?</style\s*>|<[^>]+>|[^<]+',
    re.S | re.I)
TAG_RE = re.compile(r'<\s*(/?)\s*([a-zA-Z0-9]+)')


def last_tokens(clause):
    return [(t.surface, t.part_of_speech.split(',')) for t in TOK.tokenize(clause)]


def judge(clause, after, at_sentence_start):
    """clause=直前の区切りから読点まで / after=読点の直後。外す規則名か None を返す。"""
    c = clause.strip()
    if not c or not after:
        return None
    nxt = after[0]
    if nxt in '、。」』）)　 \n' or nxt in SENT_END:
        return None
    if c.count('「') > c.count('」') or c.count('『') > c.count('』'):
        return None
    if re.search(r'[0-9０-９]$', c):
        return None
    if at_sentence_start and c in R2_WORDS:
        return 'R2'
    if len(c) > 12 or len(c) < 2:
        return None
    if c.startswith(INTERROG) or c.startswith(KEEP_HEAD):
        return None
    toks = last_tokens(c)
    if len(toks) < 2:
        return None
    s, pos = toks[-1]
    ps, ppos = toks[-2]
    # 直後が助詞・記号で始まるなら触らない
    atoks = last_tokens(after[:6])
    if atoks and atoks[0][1][0] in ('助詞', '助動詞', '記号'):
        return None
    # ひらがなが長く続いて切れ目が見えなくなる場合は残す
    run = len(re.search(r'[ぁ-ん]*$', c).group()) + len(re.match(r'[ぁ-ん]*', after).group())
    if run >= 6:
        return None
    if pos[0] != '助詞':
        return None
    # R3: 短い句（主語を含む「AはBで、」は節の境目、直後に読点が続くものは並列なので残す）
    if (len(c) <= 10 and '、' not in after[:10] and not re.search(r'[はがも]', c[:-2])
            and c[-1] not in after[:8]):
        if s in ('で', 'から', 'に') and pos[1] == '格助詞' and ppos[0] in ('名詞', '助詞'):
            return 'R3'
        if s == 'として' or (s == 'て' and ps == 'とし'):
            return 'R3'
        if s == 'は' and ps in ('で', 'に') and ppos[0] == '助詞' and ppos[1] == '格助詞':
            return 'R3'
    # R1: 短い主語
    if s in ('は', 'が') and pos[1] in ('係助詞', '格助詞'):
        if ps in ('と', 'で', 'に', 'から', 'より', 'まで', 'へ'):
            return None          # 「〜とは、」など定義・対比の型は残す
        if s == 'が' and 'が' in after[:12]:
            return None          # 「ここが、このプログラムが…」の二重の「が」は残す
        if ppos[0] in ('名詞', '助詞') or ps in ('の', 'こと', 'もの'):
            return 'R1'
    return None


def process(src, path, report):
    out = []
    skip_gen = None
    quote_depth = 0
    heading = None
    buf = ''           # 直前の区切り（文頭・読点・ブロック境界）からの文字
    at_start = True    # buf が文頭から始まっているか
    head_edits = []    # 見出し内の候補（out の位置）
    n = 0

    def flush_heading():
        nonlocal head_edits, n
        # 見出しは候補1つのときだけ外す
        if len(head_edits) == 1:
            idx, pos_in, rule, before, after = head_edits[0]
            t = out[idx]
            out[idx] = t[:pos_in] + t[pos_in + 1:]
            report.append((path, rule + '(見出し)', before, after))
            n += 1
        head_edits = []

    for m in TOKEN_RE.finditer(src):
        tok = m.group()
        if tok.startswith('<!--'):
            mm = re.match(r'<!--\s*([A-Z][A-Z-]*)\s+(START|END)', tok)
            if mm and mm.group(1) in GENERATED:
                skip_gen = mm.group(1) if mm.group(2) == 'START' else None
            out.append(tok)
            continue
        if tok.startswith('<'):
            out.append(tok)
            tm = TAG_RE.match(tok)
            if not tm:
                continue
            closing, name = tm.group(1) == '/', tm.group(2).lower()
            if name in ('script', 'style'):
                buf, at_start = '', True
                continue
            if name in QUOTE_TAGS:
                if closing:
                    quote_depth = max(0, quote_depth - 1)
                elif not tok.rstrip().endswith('/>'):
                    quote_depth += 1
            if name in HEADINGS:
                if closing:
                    flush_heading()
                    heading = None
                else:
                    heading = name
            if name not in INLINE:
                buf, at_start = '', True
            continue
        # テキスト
        if skip_gen or quote_depth or '、' not in tok:
            if not skip_gen:
                for ch in tok:
                    if ch in SENT_END:
                        buf, at_start = '', True
                    elif not (ch.isspace() and not buf):
                        buf += ch
            out.append(tok)
            continue
        chars = list(tok)
        res = []
        i = 0
        while i < len(chars):
            ch = chars[i]
            if ch == '、':
                after = ''.join(chars[i + 1:i + 12]).lstrip('\n ')
                # テキストノード末尾の読点（直後がタグ）は触らない
                rule = judge(buf, after, at_start) if ''.join(chars[i + 1:]).strip() else None
                if rule:
                    before_s = (buf + '、' + after)[:40]
                    after_s = (buf + after)[:40]
                    if heading:
                        head_edits.append((len(out), len(res), rule, before_s, after_s))
                        res.append(ch)
                    else:
                        report.append((path, rule, before_s, after_s))
                        n += 1
                    # 外した場合は文が続く扱い（buf は読点なしでつなぐと長くなるので区切る）
                    buf, at_start = '', False
                    if heading:
                        i += 1
                        continue
                    i += 1
                    continue
                res.append(ch)
                buf, at_start = '', False
            elif ch in SENT_END:
                res.append(ch)
                buf, at_start = '', True
            else:
                res.append(ch)
                if not (ch.isspace() and not buf):
                    buf += ch
            i += 1
        out.append(''.join(res))
    flush_heading()
    return ''.join(out), n


def targets(args):
    if args.files:
        return args.files
    fs = []
    for p in sorted(glob.glob('**/*.html', recursive=True)):
        if p.startswith(SKIP_DIRS) or os.path.basename(p) in SKIP_FILES or '-mockup' in p:
            continue
        fs.append(p)
    return fs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='*')
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--report')
    args = ap.parse_args()
    report, total = [], 0
    for p in targets(args):
        src = open(p, encoding='utf-8').read()
        if '、' not in src:
            continue
        new, n = process(src, p, report)
        total += n
        if n and args.write and new != src:
            open(p, 'w', encoding='utf-8').write(new)
        if n:
            print(f'{n:5d}  {p}')
    print(f'合計 {total} 個')
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write('file\trule\tbefore\tafter\n')
            for r in report:
                f.write('\t'.join(x.replace('\n', ' ').replace('\t', ' ') for x in r) + '\n')


if __name__ == '__main__':
    sys.exit(main())

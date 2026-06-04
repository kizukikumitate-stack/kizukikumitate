#!/usr/bin/env python3
"""
grid-template-columns の裸の `fr` トラックを minmax(0, …) で囲む一括変換。

理由: `1fr` は `minmax(auto, 1fr)` の略で、auto 最小値 = コンテンツの min-content 幅。
日本語 + word-break: keep-all だと Safari で min-content が文章全体の幅になり、
track が親を超えて広がり body{overflow-x:hidden} に切られる（Chrome は overflow-wrap で縮む）。
すべての fr トラックを minmax(0, …) で囲めば全ブラウザで再発しない。

使い方:
  python3 wrap-fr-minmax.py --dry <file...>   # 変更内容を表示するだけ
  python3 wrap-fr-minmax.py <file...>         # 実際に書き換える
"""
import re
import sys

FR = re.compile(r'\d*\.?\d+fr')
MINMAX = re.compile(r'minmax\([^)]*\)')
DECL = re.compile(r'(grid-template-columns\s*:\s*)([^;{}]+)')


def wrap_value(val: str) -> str:
    # 既存の minmax(...) を退避（二重ラップ防止）
    stash = []

    def hide(m):
        stash.append(m.group(0))
        return f'\x00{len(stash) - 1}\x00'

    masked = MINMAX.sub(hide, val)
    # 裸の fr トークンを minmax(0, …) で囲む
    masked = FR.sub(lambda m: f'minmax(0, {m.group(0)})', masked)
    # 退避した minmax を戻す
    return re.sub(r'\x00(\d+)\x00', lambda m: stash[int(m.group(1))], masked)


def process(text: str):
    changes = []

    def repl(m):
        prefix, val = m.group(1), m.group(2)
        new_val = wrap_value(val)
        if new_val != val:
            changes.append((val.strip(), new_val.strip()))
        return prefix + new_val

    return DECL.sub(repl, text), changes


def main():
    args = sys.argv[1:]
    dry = '--dry' in args
    files = [a for a in args if a != '--dry']
    total = 0
    for f in files:
        with open(f, encoding='utf-8') as fh:
            text = fh.read()
        new_text, changes = process(text)
        if changes:
            total += len(changes)
            print(f'\n=== {f}  ({len(changes)} changes) ===')
            for old, new in changes:
                print(f'  - {old}')
                print(f'  + {new}')
            if not dry:
                with open(f, 'w', encoding='utf-8') as fh:
                    fh.write(new_text)
    print(f'\n{"[DRY RUN] " if dry else ""}total changes: {total}')


if __name__ == '__main__':
    main()

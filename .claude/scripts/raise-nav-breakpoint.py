#!/usr/bin/env python3
"""
グローバルナビ（8リンク）が中間幅で右に切れる問題への対策。
収まらない幅（<=1400px）ではハンバーガーメニューに切り替える。
ナビは2系統（標準 nav / .global-nav）あるので、ページごとに正しいセレクタの
override ブロックを </style> 直前に追記する。文言・フォントは変更しない。

使い方: python3 raise-nav-breakpoint.py [--dry] <file...>
"""
import sys

MARKER = 'グローバルナビ折返し対策'

STANDARD = """
  /* ===== グローバルナビ折返し対策: 収まらない幅でハンバーガーに切替（右切れ防止・必ず style 終端直前） ===== */
  @media (min-width: 1401px) {
    nav { padding-left: 1.25rem; padding-right: 1.25rem; }
    .nav-links { gap: 1rem; }
  }
  @media (max-width: 1400px) {
    .nav-links { display: none; }
    .nav-hamburger { display: flex; }
  }
"""

GLOBAL = """
  /* ===== グローバルナビ折返し対策: 収まらない幅でハンバーガーに切替（右切れ防止・必ず style 終端直前） ===== */
  @media (min-width: 1401px) {
    .global-nav { padding-left: 1.5rem; padding-right: 1.5rem; }
    .global-nav .nav-links { gap: 1rem; }
  }
  @media (max-width: 1400px) {
    .global-nav .nav-links { display: none; }
    .global-nav-hamburger { display: flex; }
  }
"""


def main():
    args = sys.argv[1:]
    dry = '--dry' in args
    files = [a for a in args if a != '--dry']
    for f in files:
        with open(f, encoding='utf-8') as fh:
            text = fh.read()
        if MARKER in text:
            print(f'SKIP (already applied): {f}')
            continue
        is_global = 'global-nav-links' in text or 'class="global-nav"' in text
        block = GLOBAL if is_global else STANDARD
        idx = text.rfind('</style>')
        if idx == -1:
            print(f'WARN (no </style>): {f}')
            continue
        new_text = text[:idx] + block + text[idx:]
        sys_name = 'global-nav' if is_global else 'standard'
        print(f'{"[DRY] " if dry else ""}{f}: appended {sys_name} nav block')
        if not dry:
            with open(f, 'w', encoding='utf-8') as fh:
                fh.write(new_text)


if __name__ == '__main__':
    main()

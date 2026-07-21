#!/usr/bin/env python3
"""
図鑑ページの OEM（ホワイトラベル）版を生成するスクリプト。

きづきくみたてサイトの図鑑ページから、サイトへの接続を全部外して
「クライアントがそのまま自分のサイトで使える単一HTMLファイル」を作る。

やること:
  - グローバルナビ / フッター / 回遊バンド（他ページへのリンク）を除去
  - GA4 計測タグを除去（クライアントのアクセスが森本さんのGAに流れないように）
  - canonical / OGP / 構造化データの kizukikumitate.com URL を中立化・除去
  - 画像を base64 data-URI で HTML に埋め込み（外部ファイル依存ゼロ＝完全ポータブル）
  - ページ最下部に小さく「Directed by Yasuhito Morimoto」のクレジットだけ足す

使い方:
  python3 scripts/build-oem-zukan.py 1on1-zukan.html oem/1on1-zukan.html

出力ファイルは単一で自己完結。クライアントは任意のドメインに置けるし、
きづきくみたてサイトからはどこからもリンクされない（nav.json の exclude に登録）。
"""

import base64
import mimetypes
import os
import re
import sys

CREDIT = "Directed by Yasuhito Morimoto"


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def cut(pattern, html, label, flags=re.S, required=True):
    """pattern に一致する部分を1回だけ削除して返す。"""
    new, n = re.subn(pattern, "", html, count=1, flags=flags)
    if n == 0 and required:
        die(f"除去対象が見つかりません: {label}")
    if n:
        print(f"  ✂  除去: {label}")
    return new


def embed_images(html, base_dir):
    """card テンプレの ./images/1on1/${imgId}.webp を data-URI に置き換える。"""
    m = re.search(r'src="\./images/([^/]+)/\$\{imgId\}\.webp"', html)
    if not m:
        die("画像srcのテンプレートが見つかりません")
    folder = m.group(1)
    img_dir = os.path.join(base_dir, "images", folder)
    if not os.path.isdir(img_dir):
        die(f"画像フォルダがありません: {img_dir}")

    imgmap = {}
    for fn in sorted(os.listdir(img_dir)):
        if not fn.lower().endswith(".webp"):
            continue
        key = os.path.splitext(fn)[0]  # 例: f-01
        with open(os.path.join(img_dir, fn), "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        imgmap[key] = f"data:image/webp;base64,{b64}"
    if not imgmap:
        die("埋め込む画像が1枚もありません")

    # JS の IMG マップを const DATA の直前に注入
    entries = ",\n".join(f'  "{k}":"{v}"' for k, v in imgmap.items())
    inject = f"const IMG = {{\n{entries}\n}};\n"
    html = html.replace("const DATA = [", inject + "const DATA = [", 1)

    # src をマップ参照に差し替え
    # 置換文字列は関数で渡す（re.sub は文字列だと \ をグループ参照として解釈するため、
    # バックスラッシュが JS テンプレートリテラルに混入して構文エラーになる）
    html = re.sub(
        r'src="\./images/[^/]+/\$\{imgId\}\.webp"',
        lambda m: "src=\"${IMG[imgId]||''}\"",
        html,
        count=1,
    )
    print(f"  🖼  画像 {len(imgmap)} 枚を data-URI で埋め込み")
    return html


def build(src_path, out_path):
    base_dir = os.path.dirname(os.path.abspath(src_path)) or "."
    with open(src_path, encoding="utf-8") as f:
        html = f.read()

    # 1) GA4 計測タグ
    html = cut(
        r"<!-- Google tag \(gtag\.js\) -->.*?gtag\('config', 'G-[^']+'\);\s*</script>",
        html, "GA4 計測タグ",
    )

    # 2) title から屋号を外す
    html = re.sub(
        r"<title>.*?</title>",
        "<title>1on1の成功と失敗の図鑑</title>",
        html, count=1, flags=re.S,
    )

    # 3) canonical / OGP / Twitter の kizukikumitate URL を中立版に差し替え
    neutral_social = (
        '<meta property="og:type" content="website">\n'
        '<meta property="og:title" content="1on1の成功と失敗の図鑑｜うちの1on1、どれ?">\n'
        '<meta property="og:description" content="職場の1on1に生息する、うまくいくパターン24種と'
        'しくじりパターン26種の観察図鑑。出没場面と対処法つき。">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="twitter:title" content="1on1の成功と失敗の図鑑｜うちの1on1、どれ?">\n'
        '<meta name="twitter:description" content="職場の1on1に生息する、うまくいくパターン24種と'
        'しくじりパターン26種の観察図鑑。出没場面と対処法つき。">'
    )
    html, n = re.subn(
        r'<link rel="canonical".*?<meta name="twitter:image"[^>]*>',
        neutral_social, html, count=1, flags=re.S,
    )
    if n == 0:
        die("OGP/canonical ブロックが見つかりません")
    print("  🔗  canonical/OGP を中立版に差し替え")

    # 4) 構造化データ（Article／kizukikumitate URL入り）を除去
    html = cut(
        r"<!-- ===== AI・検索エンジン向け構造化データ.*?</script>",
        html, "構造化データ(Article)",
    )

    # 5) グローバルナビ / フッター / 回遊バンド
    html = cut(r"<!-- NAV START -->.*?<!-- NAV END -->", html, "グローバルナビ")
    html = cut(r"<!-- KAIYU START -->.*?<!-- KAIYU END -->", html, "回遊バンド")
    html = cut(r"<!-- FOOTER START -->.*?<!-- FOOTER END -->", html, "フッター")

    # 6) ナビ用JS（ハンバーガー）を除去 — ナビ要素が無いと null 参照でエラーになる
    html = cut(
        r"<script>\s*const hamburger = document\.getElementById\('hamburger'\);.*?</script>",
        html, "ナビ用JS(ハンバーガー)",
    )

    # 7) 固定ナビが無くなったぶん、body 上部の余白を詰める
    html = html.replace("--navh:62px;", "--navh:26px;", 1)

    # 8) 画像を埋め込み
    html = embed_images(html, base_dir)

    # 9) クレジットを最下部に追加
    credit_block = (
        f'\n<div class="oem-credit">{CREDIT}</div>\n'
        "<style>.oem-credit{text-align:center;padding:2.6rem 1rem 3.2rem;"
        "font-family:'Jost',sans-serif;font-size:.72rem;letter-spacing:.2em;"
        "color:#a89e88;text-transform:uppercase;}</style>\n"
    )
    html = html.replace("</body>", credit_block + "</body>", 1)

    # 10) 念のため kizukikumitate 参照が残っていないか検査
    leftovers = re.findall(r"kizukikumitate|G-E3YZKY8DQG|きづきくみたて", html)
    if leftovers:
        die(f"接続の残骸が見つかりました: {set(leftovers)}")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    size_kb = len(html.encode("utf-8")) / 1024
    print(f"\n✅ OEM版を生成: {out_path}  ({size_kb:.0f} KB・完全自己完結)")
    print("   きづきくみたてへの接続なし／クレジットのみ／画像埋め込み済み")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使い方: python3 scripts/build-oem-zukan.py <source.html> <out.html>")
        sys.exit(1)
    build(sys.argv[1], sys.argv[2])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ホモ・サピエンスの苦手図鑑のカード画像 仕上げスクリプト。

data/nigate-images.json(台帳)を読み、export_url が入っているカードについて
  1. PNG をダウンロード
  2. 幅800px・品質82の WebP に変換して images/nigate/{no}-{slug}.webp に保存
  3. nigate-zukan.html の紋プレースホルダーを <img> に差し替え
を行う。冪等: 既に webp がある場合はDLをスキップ、既に <img> の場合は差し替えをスキップ。

使い方(Macのリポジトリルートで):
  python3 scripts/fetch-nigate-images.py

WebP変換は Pillow → cwebp の順で試す。どちらも無い場合は PNG のまま保存して警告する。
export_url の期限が切れていた場合はその旨を表示するので、Canva MCP で
design_id から export-design(png, width 800) を再実行して台帳の export_url を更新する。
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "data", "nigate-images.json")
IMGDIR = os.path.join(ROOT, "images", "nigate")
PAGE = os.path.join(ROOT, "nigate-zukan.html")
QUALITY = 82
WIDTH = 800


def to_webp(png_path, webp_path):
    """PNG→WebP。Pillow→cwebpの順で試す。成功したらTrue。"""
    try:
        from PIL import Image
        img = Image.open(png_path).convert("RGB")
        if img.width > WIDTH:
            img = img.resize((WIDTH, int(img.height * WIDTH / img.width)), Image.LANCZOS)
        img.save(webp_path, "WEBP", quality=QUALITY)
        return True
    except ImportError:
        pass
    try:
        subprocess.run(["cwebp", "-q", str(QUALITY), "-resize", str(WIDTH), "0",
                        png_path, "-o", webp_path],
                       check=True, capture_output=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def main():
    with open(MANIFEST) as f:
        manifest = json.load(f)
    os.makedirs(IMGDIR, exist_ok=True)

    with open(PAGE) as f:
        page = f.read()

    downloaded, swapped, skipped, failed = [], [], [], []

    for card in manifest["cards"]:
        no, slug, mon, alt = card["no"], card["slug"], card["mon"], card["alt"]
        webp_rel = f"images/nigate/{no}-{slug}.webp"
        webp_abs = os.path.join(ROOT, webp_rel)

        # 1. ダウンロード+変換(webp未取得かつURLありの場合)
        if not os.path.exists(webp_abs):
            url = card.get("export_url")
            if not url:
                skipped.append(f"No.{no}: export_url 未記入(未生成)")
            else:
                try:
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                        with urllib.request.urlopen(url, timeout=60) as resp:
                            tmp.write(resp.read())
                        tmp_path = tmp.name
                    if to_webp(tmp_path, webp_abs):
                        downloaded.append(f"No.{no} → {webp_rel}")
                    else:
                        png_abs = webp_abs.replace(".webp", ".png")
                        os.replace(tmp_path, png_abs)
                        failed.append(f"No.{no}: WebP変換手段なし。PNGのまま保存 {png_abs}(Pillow か cwebp を入れて再実行)")
                        continue
                    os.unlink(tmp_path)
                except Exception as e:
                    failed.append(f"No.{no}: ダウンロード失敗({e})。URL期限切れなら design_id={card.get('design_id')} から再export")
                    continue

        # 2. HTML差し替え(webpがあり、まだ紋プレースホルダーかSVG仮画像の場合)
        if os.path.exists(webp_abs):
            svg_rel = f"images/nigate/{no}-{slug}.svg"
            placeholder = f'<figure class="card-fig"><span class="mon" aria-hidden="true">{mon}</span></figure>'
            svgtag = f'<figure class="card-fig"><img src="{svg_rel}" alt="{alt}" loading="lazy"></figure>'
            imgtag = f'<figure class="card-fig"><img src="{webp_rel}" alt="{alt}" loading="lazy"></figure>'
            if placeholder in page:
                page = page.replace(placeholder, imgtag)
                swapped.append(f"No.{no}: 紋「{mon}」→ img 差し替え")
            elif svgtag in page:
                page = page.replace(svgtag, imgtag)
                swapped.append(f"No.{no}: SVG仮画像 → Canva版 webp 差し替え")
            elif webp_rel in page:
                pass  # 既に差し替え済み
            else:
                failed.append(f"No.{no}: プレースホルダーが見つからない(HTMLが変更された?)")

    with open(PAGE, "w") as f:
        f.write(page)

    print("── fetch-nigate-images 結果 ──")
    for line in downloaded: print("  ⬇️ ", line)
    for line in swapped:    print("  🔁 ", line)
    for line in skipped:    print("  ⏭️ ", line)
    for line in failed:     print("  ❌ ", line)
    if not (downloaded or swapped or failed):
        print("  変更なし(すべて処理済みか、URL未記入)")
    print("完了。差し替え後は mobile-preflight を通してからコミットしてください。")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

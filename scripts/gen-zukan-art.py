#!/usr/bin/env python3
"""
図鑑イラストを Gemini 画像API で量産する共通パイプライン。

図鑑ごとに使い捨てスクリプトを書き直していたのをやめ、
「仕様(JSON) だけ書けば絵が出来上がる」形に一本化したもの。
過去に踏んだ地雷（1:1で返ってくる／文字が焼き込まれる／顔が出る）への
対策を全部この中に入れてある。

使い方:
    # 生成 → コンタクトシート → WebP化 まで一気に
    python3 scripts/gen-zukan-art.py run data/art-specs/reflection.json

    # 個別のやり直し（外れた絵だけ指定して再生成）
    python3 scripts/gen-zukan-art.py gen data/art-specs/reflection.json --only 03-morning-pages,07-what
    python3 scripts/gen-zukan-art.py sheet data/art-specs/reflection.json
    python3 scripts/gen-zukan-art.py build data/art-specs/reflection.json

    # 枚数と概算費用だけ見る（APIを叩かない）
    python3 scripts/gen-zukan-art.py plan data/art-specs/reflection.json

★ネットワーク: generativelanguage.googleapis.com はサンドボックス不許可。
  Claude Code から実行するときは dangerouslyDisableSandbox:true が必要。

★APIキー: 環境変数 GEMINI_API_KEY、無ければ ~/Downloads/gemini-key.txt。
  aistudio.google.com/apikey で発行（Billing有効化必須）。
"""

import argparse
import base64
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

from PIL import Image, ImageDraw

MODEL_DEFAULT = "gemini-2.5-flash-image"
YEN_PER_IMAGE = 7  # 概算（1枚数円）。plan の見積り表示にだけ使う
ASPECT_TOLERANCE = 0.06  # 実出力の比率ズレの許容（4:5指定で0.78が返る程度は許す）


# ---------------------------------------------------------------- 基盤

def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_key():
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    path = os.path.expanduser("~/Downloads/gemini-key.txt")
    if os.path.exists(path):
        return open(path).read().strip()
    sys.exit(
        "APIキーが見つかりません。\n"
        "  export GEMINI_API_KEY=... か、~/Downloads/gemini-key.txt に保存してください。"
    )


def load_spec(spec_path):
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)

    for required in ("name", "out_dir", "file_pattern", "items"):
        if required not in spec:
            sys.exit(f"仕様に {required} がありません: {spec_path}")

    spec.setdefault("model", MODEL_DEFAULT)
    spec.setdefault("aspect_ratio", "16:9")
    spec.setdefault("style", "")
    spec.setdefault("anchors", [])
    spec.setdefault("webp", {})
    spec["webp"].setdefault("width", 1600)
    spec["webp"].setdefault("quality", 82)

    # 生成途中の PNG は raw_dir に貯める（WebP化前の原本を残しておくと再調整が効く）
    spec.setdefault("raw_dir", os.path.join(".art-raw", spec["name"]))

    for i, item in enumerate(spec["items"], 1):
        if "id" not in item:
            sys.exit(f"items[{i}] に id がありません")
        item.setdefault("index", i)
    return spec


def aspect_target(ratio_str):
    w, h = ratio_str.split(":")
    return float(w) / float(h)


def build_prompt(spec, item):
    """共通の画風指定 + カード個別の場面 を1本のプロンプトに合成する。"""
    parts = []
    if spec["style"]:
        parts.append(spec["style"].strip())
    parts.append(item["prompt"].strip())
    return "\n".join(parts)


def anchor_parts(spec):
    """見本画像を inline_data として渡す（画風を揃えたいときに使う）。"""
    out = []
    for path in spec["anchors"]:
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            sys.exit(f"見本画像が見つかりません: {path}")
        im = Image.open(path).convert("RGB")
        if im.width > 1024:
            im = im.resize((1024, round(im.height * 1024 / im.width)))
        buf = io.BytesIO()
        im.save(buf, "PNG")
        out.append({
            "inline_data": {
                "mime_type": "image/png",
                "data": base64.b64encode(buf.getvalue()).decode(),
            }
        })
    return out


# ---------------------------------------------------------------- 生成

def request_image(spec, key, prompt, anchors):
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{spec['model']}:generateContent?key={key}"
    )
    body = {
        "contents": [{"parts": anchors + [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            # ★これを付けないとテキストのみ生成で正方形が返ってきがち
            "imageConfig": {"aspectRatio": spec["aspect_ratio"]},
        },
    }
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=180) as res:
        payload = json.load(res)

    for part in payload["candidates"][0]["content"]["parts"]:
        blob = part.get("inlineData") or part.get("inline_data")
        if blob:
            return base64.b64decode(blob["data"])
    return None


def generate_one(spec, key, item, raw_dir, anchors, tries=3):
    """1枚生成する。比率が狂ったものは失敗扱いにして引き直す。"""
    want = aspect_target(spec["aspect_ratio"])
    dest = os.path.join(raw_dir, item["id"] + ".png")

    for attempt in range(1, tries + 1):
        try:
            raw = request_image(spec, key, build_prompt(spec, item), anchors)
            if raw is None:
                print(f"  … {item['id']} try{attempt}: 画像パートが返らなかった")
                time.sleep(2)
                continue

            im = Image.open(io.BytesIO(raw))
            got = im.width / im.height
            if abs(got - want) / want > ASPECT_TOLERANCE:
                print(
                    f"  … {item['id']} try{attempt}: 比率ちがい "
                    f"{im.width}x{im.height} (期待 {spec['aspect_ratio']}) → 引き直し"
                )
                time.sleep(2)
                continue

            with open(dest, "wb") as f:
                f.write(raw)
            print(f"  ✓ {item['id']}  {im.width}x{im.height}  {len(raw) // 1024}KB")
            return True

        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:200]
            print(f"  ✗ {item['id']} try{attempt}: HTTP {e.code} {detail}")
        except Exception as e:  # noqa: BLE001 — 生成は落ちても続行したい
            print(f"  ✗ {item['id']} try{attempt}: {e}")
        time.sleep(2)

    return False


def cmd_gen(spec, args):
    key = load_key()
    raw_dir = os.path.join(repo_root(), spec["raw_dir"])
    os.makedirs(raw_dir, exist_ok=True)
    anchors = anchor_parts(spec)

    todo = select_items(spec, args)
    if not args.force:
        before = len(todo)
        todo = [i for i in todo if not os.path.exists(os.path.join(raw_dir, i["id"] + ".png"))]
        if before != len(todo):
            print(f"生成済み {before - len(todo)} 枚はスキップ（作り直すなら --force）")

    if not todo:
        print("生成するものはありません")
        return 0

    print(f"{len(todo)}枚を生成 → {spec['raw_dir']}")
    ok = sum(1 for item in todo if generate_one(spec, key, item, raw_dir, anchors))
    print(f"\n完了: {ok}/{len(todo)}")
    if ok < len(todo):
        print("失敗分は同じコマンドを再実行すれば続きから生成されます")
        return 1
    return 0


# ---------------------------------------------------------------- 確認・組込み

def cmd_sheet(spec, args):
    """全カットを1枚に並べたコンタクトシート。外れた絵を目視で拾うため。"""
    raw_dir = os.path.join(repo_root(), spec["raw_dir"])
    items = [i for i in select_items(spec, args)
             if os.path.exists(os.path.join(raw_dir, i["id"] + ".png"))]
    if not items:
        sys.exit("生成済みの画像がありません。先に gen を実行してください。")

    cols = 4
    cell_w = 420
    ratio = aspect_target(spec["aspect_ratio"])
    cell_h = round(cell_w / ratio)
    label_h = 26
    rows = (len(items) + cols - 1) // cols

    sheet = Image.new("RGB", (cols * cell_w, rows * (cell_h + label_h)), "#ffffff")
    draw = ImageDraw.Draw(sheet)

    for n, item in enumerate(items):
        im = Image.open(os.path.join(raw_dir, item["id"] + ".png")).convert("RGB")
        im = im.resize((cell_w, cell_h))
        x = (n % cols) * cell_w
        y = (n // cols) * (cell_h + label_h)
        sheet.paste(im, (x, y))
        draw.text((x + 6, y + cell_h + 6), item["id"], fill="#333333")

    out = os.path.join(raw_dir, "_contact-sheet.png")
    sheet.save(out)
    print(f"コンタクトシート: {os.path.relpath(out, repo_root())}  ({len(items)}枚)")
    print("外れたカットは gen --only <id> で引き直してください")
    return 0


def cmd_build(spec, args):
    """原本PNG → 本番用WebP。出力名は file_pattern に従う。"""
    raw_dir = os.path.join(repo_root(), spec["raw_dir"])
    out_dir = os.path.join(repo_root(), spec["out_dir"])
    os.makedirs(out_dir, exist_ok=True)

    width = spec["webp"]["width"]
    quality = spec["webp"]["quality"]
    total = 0
    built = 0

    for item in select_items(spec, args):
        src = os.path.join(raw_dir, item["id"] + ".png")
        if not os.path.exists(src):
            print(f"  - {item['id']}: 原本が無いのでスキップ")
            continue

        im = Image.open(src).convert("RGB")
        if im.width != width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)

        name = spec["file_pattern"].format(i=item["index"], id=item["id"])
        dest = os.path.join(out_dir, name)
        im.save(dest, "WEBP", quality=quality)
        size = os.path.getsize(dest)
        total += size
        built += 1
        print(f"  ✓ {name}  {im.width}x{im.height}  {size // 1024}KB")

    print(f"\n{built}枚 → {spec['out_dir']}  合計 {total / 1024 / 1024:.1f}MB")
    if built:
        print("次: HTMLの配線を確認し、./.claude/scripts/mobile-preflight.sh full <page>.html")
    return 0


def cmd_plan(spec, args):
    items = select_items(spec, args)
    print(f"図鑑        : {spec['name']}")
    print(f"モデル      : {spec['model']}")
    print(f"比率        : {spec['aspect_ratio']}")
    print(f"枚数        : {len(items)}")
    print(f"概算費用    : ¥{len(items) * YEN_PER_IMAGE:,} 前後（1枚 約¥{YEN_PER_IMAGE}）")
    print(f"見本画像    : {len(spec['anchors'])}枚")
    print(f"原本置き場  : {spec['raw_dir']}")
    print(f"出力先      : {spec['out_dir']}/{spec['file_pattern']}")
    print(f"WebP        : 幅{spec['webp']['width']} / quality {spec['webp']['quality']}")
    if items:
        print(f"\n先頭のプロンプト（{items[0]['id']}）:\n---")
        print(build_prompt(spec, items[0]))
        print("---")
    return 0


# ---------------------------------------------------------------- CLI

def select_items(spec, args):
    if not args.only:
        return list(spec["items"])
    wanted = {s.strip() for s in args.only.split(",") if s.strip()}
    picked = [i for i in spec["items"] if i["id"] in wanted]
    missing = wanted - {i["id"] for i in picked}
    if missing:
        sys.exit(f"仕様に無いID: {', '.join(sorted(missing))}")
    return picked


def main():
    parser = argparse.ArgumentParser(description="図鑑イラストの生成パイプライン")
    parser.add_argument("command", choices=["run", "gen", "sheet", "build", "plan"])
    parser.add_argument("spec", help="仕様JSON（例: data/art-specs/reflection.json）")
    parser.add_argument("--only", help="対象IDをカンマ区切りで限定")
    parser.add_argument("--force", action="store_true", help="生成済みでも作り直す")
    args = parser.parse_args()

    spec = load_spec(args.spec)

    if args.command == "run":
        if cmd_gen(spec, args) != 0:
            print("\n生成に失敗があるため中断します。再実行するか --only で個別に引き直してください。")
            return 1
        cmd_sheet(spec, args)
        return cmd_build(spec, args)

    return {"gen": cmd_gen, "sheet": cmd_sheet, "build": cmd_build, "plan": cmd_plan}[
        args.command
    ](spec, args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""tenshoku-no-sho.html の道ゆく猫・スライムの「5段階ゴージャス化」スプライト生成。

元シート images/tenshoku/cat-run.png (2304x60, 96x60x24コマ) と
slime-hop.png (1920x60, 96x60x20コマ) を読み、段階2〜5の装飾
(リボン→王冠→宝石付き王冠＋襟巻→大王冠＋キラキラ) を各コマの
実際の輪郭位置に追従させて合成する。段階1は元ファイルのまま。

出力: images/tenshoku/{cat-run,slime-hop}-{2..5}.png （寸法は元と同一）
再実行は冪等。プレビュー用の見本シートも scratchpad ではなく
images/tenshoku/ 以外へ出したい場合は --preview DIR を使う。
"""
import argparse
import math
import os
import numpy as np
from PIL import Image, ImageDraw

SRC = os.path.join(os.path.dirname(__file__), "..", "images", "tenshoku")
SS = 4  # supersampling factor (draw at 4x then downscale)
FW, FH = 96, 60

GOLD = (255, 215, 106, 255)        # 本体と同じ金
CROWN = (255, 178, 44, 255)        # 王冠の濃い金
CROWN_HI = (255, 232, 160, 255)    # 王冠ハイライト
RED = (226, 82, 106, 255)          # リボン・襟巻
RED_DK = (188, 56, 82, 255)
RUBY = (255, 93, 115, 255)
EMERALD = (67, 214, 154, 255)
SAPPHIRE = (95, 168, 255, 255)
SPARK = (255, 247, 221, 255)


def frames(img, n):
    for i in range(n):
        yield i, img.crop((i * FW, 0, (i + 1) * FW, FH))


def mask_of(frame):
    a = np.array(frame)
    return a[:, :, 3] > 60


def bbox(m):
    ys, xs = np.where(m)
    return xs.min(), ys.min(), xs.max(), ys.max()


def cat_head_anchor(m):
    """右向き猫の耳まわり: (耳の中心x, 耳の上端y, 耳スパン幅) を返す。"""
    x0, y0, x1, y1 = bbox(m)
    w = x1 - x0
    region = m[:, int(x0 + 0.55 * w):]
    ys, xs = np.where(region)
    ear_top = ys.min()
    near = xs[ys <= ear_top + 10]
    cx = int(x0 + 0.55 * w) + int((near.min() + near.max()) / 2)
    span = near.max() - near.min()
    return cx, int(ear_top), int(span)


def slime_top_anchor(m):
    """スライムのてっぺん: (中心x, 上端y) を返す。"""
    ys, xs = np.where(m)
    top = ys.min()
    near = xs[ys <= top + 8]
    return int((near.min() + near.max()) / 2), int(top)


# ---- 装飾パーツ (すべて SS 倍座標で描く) --------------------------------

def draw_bow(d, cx, cy, s, phase=0.0):
    """ちょこんとした赤リボン。phase で羽根がわずかに揺れる。"""
    w = s * (1 + 0.06 * math.sin(phase))
    d.polygon([(cx - w, cy - s * 0.7), (cx - w, cy + s * 0.7), (cx - s * 0.15, cy)], fill=RED)
    d.polygon([(cx + w, cy - s * 0.7), (cx + w, cy + s * 0.7), (cx + s * 0.15, cy)], fill=RED)
    r = s * 0.32
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED_DK)


def draw_crown(d, cx, base_y, w, h, points=3, gems=None, band=True):
    """点数・宝石つきの王冠。base_y はバンドの下端。"""
    half = w / 2
    band_h = h * 0.34
    # ギザギザ本体
    poly = [(cx - half, base_y), (cx - half, base_y - band_h)]
    for p in range(points):
        x_a = cx - half + w * p / points
        x_m = cx - half + w * (p + 0.5) / points
        x_b = cx - half + w * (p + 1) / points
        poly += [(x_a, base_y - band_h), (x_m, base_y - h), (x_b, base_y - band_h)]
    poly += [(cx + half, base_y)]
    d.polygon(poly, fill=CROWN)
    if band:
        d.rectangle([cx - half, base_y - band_h, cx + half, base_y], fill=CROWN)
        d.line([(cx - half, base_y - band_h), (cx + half, base_y - band_h)], fill=CROWN_HI, width=SS)
    # 先端の玉
    for p in range(points):
        x_m = cx - half + w * (p + 0.5) / points
        r = h * 0.10
        d.ellipse([x_m - r, base_y - h - r, x_m + r, base_y - h + r], fill=CROWN_HI)
    # 宝石
    if gems:
        n = len(gems)
        for gi, col in enumerate(gems):
            gx = cx + (gi - (n - 1) / 2) * (w / (n + 0.6))
            r = h * 0.14
            gy = base_y - band_h / 2
            d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=col)


def draw_cape_cat(d, nx, ny, length, phase, trim=False):
    """首の付け根 (nx, ny) から後方 (左) へなびく赤マント (背面レイヤー)。"""
    flut = math.sin(phase) * 2.2 * SS
    tip_x = nx - length
    tip_hi = ny - 6 * SS + flut
    tip_lo = ny + 3 * SS + flut * 0.6
    d.polygon([(nx, ny), (nx + 2 * SS, ny + 6 * SS),
               (tip_x + 4 * SS, tip_lo), (tip_x, tip_hi)], fill=RED)
    if trim:
        d.line([(tip_x, tip_hi), (tip_x + 4 * SS, tip_lo)], fill=CROWN_HI, width=int(SS * 1.5))


def draw_pendant(d, cx, cy, s, col):
    """胸元の宝石ペンダント (スライム用)。"""
    d.line([(cx - s * 1.1, cy - s * 0.9), (cx, cy), (cx + s * 1.1, cy - s * 0.9)],
           fill=CROWN, width=SS)
    d.polygon([(cx, cy - s * 0.45), (cx + s * 0.5, cy), (cx, cy + s * 0.75),
               (cx - s * 0.5, cy)], fill=col)


def draw_sparkle(d, cx, cy, r):
    """4方向のキラキラ星。"""
    k = r * 0.28
    d.polygon([(cx, cy - r), (cx + k, cy - k), (cx + r, cy), (cx + k, cy + k),
               (cx, cy + r), (cx - k, cy + k), (cx - r, cy), (cx - k, cy - k)], fill=SPARK)


def draw_glint(d, cx, cy, r):
    """本体の照りかえし (弧状ハイライト)。"""
    d.arc([cx - r, cy - r, cx + r, cy + r], start=195, end=250,
          fill=(255, 255, 255, 150), width=int(SS * 1.8))


# ---- ステージ合成 --------------------------------------------------------

def compose(base_frame, draw_back=None, draw_front=None):
    """SS 倍で背面/前面レイヤーを描いて合成した 96x60 フレームを返す。"""
    layers = []
    for fn in (draw_back, draw_front):
        im = Image.new("RGBA", (FW * SS, FH * SS), (0, 0, 0, 0))
        if fn:
            fn(ImageDraw.Draw(im))
        layers.append(im.resize((FW, FH), Image.LANCZOS))
    out = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    out.alpha_composite(layers[0])
    out.alpha_composite(base_frame)
    out.alpha_composite(layers[1])
    return out


def sparkle_set(d, i, spots, base_r):
    """コマ番号で明滅するキラキラ群。"""
    for j, (sx, sy) in enumerate(spots):
        ph = (i // 2 + j) % 3
        if ph == 0:
            continue
        draw_sparkle(d, sx * SS, sy * SS, base_r * (1.0 if ph == 1 else 0.62))


def gen_cat(stage, src):
    n = 24
    out = Image.new("RGBA", (FW * n, FH), (0, 0, 0, 0))
    for i, f in frames(src, n):
        m = mask_of(f)
        cx, ear_top, span = cat_head_anchor(m)
        x0, y0, x1, y1 = bbox(m)
        phase = 2 * math.pi * i / n

        def back(d):
            if stage >= 4:
                draw_cape_cat(d, (cx - span * 1.1) * SS, (ear_top + 15) * SS,
                              (20 if stage == 4 else 26) * SS, phase, trim=(stage == 5))
            if stage == 3:
                draw_crown(d, cx * SS, (ear_top + 6) * SS, span * 0.95 * SS, 10 * SS, points=3)
            elif stage == 4:
                draw_crown(d, cx * SS, (ear_top + 6) * SS, span * 1.05 * SS, 12 * SS,
                           points=3, gems=[RUBY])
            elif stage == 5:
                draw_crown(d, cx * SS, (ear_top + 6) * SS, span * 1.2 * SS, 14 * SS,
                           points=5, gems=[RUBY])

        def front(d):
            if stage == 2:
                draw_bow(d, (cx - span * 0.65) * SS, (ear_top + 5) * SS, 5.2 * SS, phase)
            if stage == 5:
                spots = [(x0 + 8, ear_top), (cx + span + 3, ear_top - 4), (x0 + 28, y0 + 2)]
                sparkle_set(d, i, spots, 3.2 * SS)

        out.paste(compose(f, back, front), (i * FW, 0))
    return out


def gen_slime(stage, src):
    n = 20
    out = Image.new("RGBA", (FW * n, FH), (0, 0, 0, 0))
    for i, f in frames(src, n):
        m = mask_of(f)
        cx, top = slime_top_anchor(m)
        x0, y0, x1, y1 = bbox(m)
        phase = 2 * math.pi * i / n

        def back(d):
            pass

        def front(d):
            if stage == 2:
                draw_bow(d, (cx + 8) * SS, (top + 3) * SS, 5.2 * SS, phase)
            elif stage == 3:
                draw_crown(d, cx * SS, (top + 6) * SS, 17 * SS, 10 * SS, points=3)
            elif stage == 4:
                draw_crown(d, cx * SS, (top + 6) * SS, 20 * SS, 12 * SS,
                           points=3, gems=[RUBY])
                draw_pendant(d, cx * SS, (y1 - 10) * SS, 4.5 * SS, SAPPHIRE)
            elif stage == 5:
                draw_crown(d, cx * SS, (top + 7) * SS, 26 * SS, 15 * SS,
                           points=5, gems=[EMERALD, RUBY, SAPPHIRE])
                draw_pendant(d, cx * SS, (y1 - 10) * SS, 4.5 * SS, RUBY)
                spots = [(x0 - 2, top + 8), (x1 + 3, top + 14), (cx + 14, y1 - 4)]
                sparkle_set(d, i, spots, 3.2 * SS)
                draw_glint(d, (cx - 8) * SS, (top + 16) * SS, 11 * SS)

        out.paste(compose(f, back, front), (i * FW, 0))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", help="見本シートの出力先ディレクトリ")
    args = ap.parse_args()

    cat = Image.open(os.path.join(SRC, "cat-run.png")).convert("RGBA")
    slime = Image.open(os.path.join(SRC, "slime-hop.png")).convert("RGBA")

    for stage in (2, 3, 4, 5):
        c = gen_cat(stage, cat)
        s = gen_slime(stage, slime)
        c.save(os.path.join(SRC, f"cat-run-{stage}.png"))
        s.save(os.path.join(SRC, f"slime-hop-{stage}.png"))
        print(f"stage {stage}: cat-run-{stage}.png / slime-hop-{stage}.png")

    if args.preview:
        os.makedirs(args.preview, exist_ok=True)
        for name, src_img, nf in [("cat-run", cat, 24), ("slime-hop", slime, 20)]:
            rows = []
            for stage in (1, 2, 3, 4, 5):
                sheet = src_img if stage == 1 else Image.open(
                    os.path.join(SRC, f"{name}-{stage}.png"))
                row = Image.new("RGBA", (FW * 4, FH), (12, 13, 40, 255))
                for k in range(4):
                    fr = sheet.crop((k * (nf // 4) * FW, 0, (k * (nf // 4) + 1) * FW, FH))
                    row.alpha_composite(fr, (k * FW, 0))
                rows.append(row)
            board = Image.new("RGBA", (FW * 4, FH * 5 + 8 * 4), (12, 13, 40, 255))
            for r, row in enumerate(rows):
                board.alpha_composite(row, (0, r * (FH + 8)))
            board = board.resize((board.width * 2, board.height * 2), Image.NEAREST)
            board.save(os.path.join(args.preview, f"preview-{name}.png"))
            print("preview:", os.path.join(args.preview, f"preview-{name}.png"))


if __name__ == "__main__":
    main()

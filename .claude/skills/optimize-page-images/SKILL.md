---
name: optimize-page-images
description: |
  kizukikumitate.com の各ページの画像が重くてモバイルで読み込みが遅い問題を診断・解決するスキル。
  以下のキーワード/症状が出たら必ず参照する:
  - 「スマホでなかなかページが開かない」「読み込みが遅い」
  - 「画像が重い」「ページサイズが大きい」「LCP が悪い」
  - 「写真がカクつく」「スクロール時に画像が遅れて出る」
  新規ページ作成時、写真を多く使うページを公開する前にもこのスキルを参照する。
  画像最適化は単独タスクとして実行することもあるし、他の修正のついでに気づいたときにも実行する。
---

# ページ画像 軽量化スキル

## なぜ必要か

写真を撮ったままの状態（1600×1200、500KB-1MB/枚）を多用すると、ページ全体で10MB超になる。
モバイル4G回線では数十秒〜分単位の読み込み時間になり、ユーザーが離脱する。

過去にあった事例: 27枚の写真で 10.73 MB → 4.61 MB（57%削減）を達成。

## 診断手順

### 1. ページ内の画像とサイズを一覧する

```bash
cd /Users/morimotoyasuhito/kizukikumitate

# ページ内で参照されている画像をリストアップ
grep -oE 'src="\./[^"]+\.(jpg|jpeg|png|webp|avif)"' <ページ名>.html | sort -u

# 各画像の物理サイズ
ls -la df-*.jpg morimoto-profile.jpg logotype.png 2>/dev/null \
  | awk '{printf "%9d  %s\n", $5, $NF}' | sort -rn | head -15

# 合計
ls -la df-*.jpg *.png 2>/dev/null \
  | awk '{sum+=$5} END {printf "Total: %.2f MB across %d files\n", sum/1024/1024, NR}'
```

### 2. 各画像の実寸（ピクセル数）を確認

```bash
for f in df-tv-9.jpg df-tv-hero.jpg morimoto-profile.jpg; do
  dim=$(sips -g pixelWidth -g pixelHeight "$f" 2>/dev/null \
    | awk '/pixel/{print $2}' | paste -sd 'x' -)
  size=$(ls -la "$f" | awk '{print $5}')
  printf "%-30s %10s bytes  %s\n" "$f" "$size" "$dim"
done
```

**判断基準**:
- ページ内で **最大1200px** までしか表示しないのに **1600px超** の画像 → リサイズ対象
- **300KB超** のJPG → 再圧縮対象
- 1ページの画像合計が **5MB超** → 全体的な最適化が必要

## 修正手順

### Step 1: バックアップ

`sips` はファイルを上書きする際に挙動が不安定。安全のため必ずバックアップする:

```bash
cd /Users/morimotoyasuhito/kizukikumitate
mkdir -p _img-backup
cp df-*.jpg morimoto-profile.jpg logotype.png _img-backup/

# .gitignore に追加（既存でなければ）
grep -q "^_img-backup/" .gitignore 2>/dev/null || echo "_img-backup/" >> .gitignore
```

### Step 2: sips でリサイズ＋再圧縮（要 dangerouslyDisableSandbox: true）

**重要**: `sips` は内部的にOSの一時ディレクトリに書き込む必要があるため、
通常のサンドボックスではエラーになる。Bash 呼び出し時に `dangerouslyDisableSandbox: true` が必須。

```bash
cd /Users/morimotoyasuhito/kizukikumitate
mkdir -p _resized

# ヒーロー画像・主要フォーカス画像: 1400px / quality 75（高品質維持）
for f in df-tv-hero.jpg df-tv-fire-sub.jpg df-tv-fire-main.jpg; do
  [ -f "$f" ] || continue
  sips -Z 1400 -s formatOptions 75 "$f" --out "_resized/$f" > /dev/null 2>&1
done

# ギャラリー画像: 1000px / quality 68（小サムネ用、十分な品質）
for f in df-tv-2.jpg df-tv-3.jpg ... df-dk-*.jpg df-jp-*.jpg; do
  [ -f "$f" ] || continue
  sips -Z 1000 -s formatOptions 68 "$f" --out "_resized/$f" > /dev/null 2>&1
done

# プロフィール写真: 800px / quality 80
sips -Z 800 -s formatOptions 80 morimoto-profile.jpg \
  --out _resized/morimoto-profile.jpg > /dev/null 2>&1

# PNG ロゴ: リサイズだけ（PNG は formatOptions の効果限定的）
# 1500x450 → 400x120 など、retina @3x 表示サイズの3倍まで縮小
sips -Z 400 logotype.png --out _resized/logotype.png > /dev/null 2>&1
```

### Step 3: 確認して入れ替え

```bash
# サイズ確認
echo "Before: $(du -ch _img-backup/*.{jpg,png} 2>/dev/null | tail -1 | awk '{print $1}')"
echo "After:  $(du -ch _resized/*.{jpg,png} 2>/dev/null | tail -1 | awk '{print $1}')"

# 視覚確認も並行: 適当に1-2枚開いて画質に問題ないかチェック
open _resized/df-tv-hero.jpg
# open _img-backup/df-tv-hero.jpg  # 比較したい場合

# 問題なければ本体に入れ替え
for f in _resized/*; do
  mv "$f" "./$(basename "$f")"
done
rmdir _resized
```

## sips の品質目安（経験則）

| 用途 | 推奨最大寸法 | quality | 備考 |
|---|---|---|---|
| ヒーロー背景 | 1400-1600px | 75 | 第一印象に直結。やや高めの品質を維持 |
| ギャラリー写真 | 1000-1200px | 68-72 | リストで並ぶ。1枚250KB以下を目標 |
| プロフィール写真 | 600-800px | 78-82 | 顔写真は品質を保つ |
| アイコン/装飾画像 | 表示サイズの2-3倍 | 70-80 | 過剰品質の意味なし |
| PNG透過ロゴ | 表示サイズの3倍 | (PNG) | sips のリサイズのみで効果あり |

## HTMLの読み込み戦略

リサイズだけでなく、読み込みの優先度も整える。

### ヒーロー画像（above the fold）の preload

CSS背景画像はCSSパース後にダウンロードが始まる。`<link rel="preload">` で前倒し:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preload" as="image" href="./df-tv-hero.jpg" fetchpriority="high">
<link href="https://fonts.googleapis.com/css2?..." rel="stylesheet">
```

### ロゴ等の above-the-fold img には `fetchpriority="high"`

```html
<img src="./logotype.png" alt="ロゴ" decoding="async" fetchpriority="high">
```

### それ以外の img には `loading="lazy" decoding="async"`

```html
<img src="./photo.jpg" alt="..." loading="lazy" decoding="async">
```

### 監査ワンライナー

```bash
# img タグの数と loading="lazy" の数を比較
echo "img tags: $(grep -c '<img ' <ページ>.html)"
echo "lazy: $(grep -c 'loading=\"lazy\"' <ページ>.html)"

# lazy が付いていない img をリスト
grep -n '<img ' <ページ>.html | grep -v 'loading=' | head -10
```

above the fold（ナビロゴ、ヒーロー）以外は **すべて lazy** にする。

## デプロイ

```bash
cd /Users/morimotoyasuhito/kizukikumitate
git add <ページ>.html df-*.jpg *.png .gitignore
git commit -m "perf: <ページ名>の画像を最適化（XMB→YMB）"
git push origin main
```

数分後に本番反映。スマホで `Cmd + Shift + R` でキャッシュ破棄して確認してもらう。

## さらに高速化したい場合

今回の最適化でも十分速いはずだが、もっと攻めたい時:

1. **WebP/AVIF への変換** — JPEGよりさらに25-35%軽い。`<picture>` タグで JPEG フォールバック:
   ```html
   <picture>
     <source srcset="./photo.avif" type="image/avif">
     <source srcset="./photo.webp" type="image/webp">
     <img src="./photo.jpg" alt="..." loading="lazy">
   </picture>
   ```
2. **`srcset` でデバイス別配信** — モバイルに小さな画像を配信:
   ```html
   <img
     src="./photo-1200.jpg"
     srcset="./photo-600.jpg 600w, ./photo-1200.jpg 1200w"
     sizes="(max-width: 768px) 100vw, 50vw"
     alt="..."
     loading="lazy">
   ```
3. **Service Worker でキャッシュ** — 再訪時に即表示

これらは大規模リファクタになるため、初期最適化（sips + preload + lazy）で
ユーザー満足が得られなければ次の打ち手として提案する。

## 注意事項

- `sips` 実行時は **必ず `dangerouslyDisableSandbox: true`** で呼ぶ
  （内部の一時ファイル書き込みがサンドボックスで弾かれる）
- 同じファイル名で `--out` すると挙動が不安定。**別ディレクトリ→ mv** が確実
- リサイズ前に **必ず `_img-backup/` にコピーを取る**（.gitignore で除外）
- 画質の劣化はモニターで実機確認。特に細かい文字・線が入る画像（チラシ等）は要注意
- ページ全体の画像合計は **5MB以下** を目標

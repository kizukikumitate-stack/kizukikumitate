---
name: generate-zukan-art
description: |
  図鑑ページのカードイラストを Gemini 画像API で量産し、WebP化してHTMLに組み込むスキル。
  次のときに必ず使う:
  - 「図鑑にイラストを付けたい」「絵を生成して」「イラストを差し替えたい」
  - 新しい図鑑ページを作り、カードに絵が必要になったとき
  - 既存図鑑のイラストのタッチを変えたい・一部を引き直したいとき
  ★図鑑ごとに使い捨ての生成スクリプトを書かないこと。必ず仕様JSON + 共通スクリプトで行う。
---

# 図鑑イラスト生成スキル

2026年7月、3日間で261枚のイラストを作ったが、図鑑ごとに使い捨ての生成スクリプトを
20本書き直していた（しかも全部 `/tmp` に置いて消えた）。同じことを繰り返さないための
共通パイプライン。**新しい図鑑でも、書くのは仕様JSONだけ。**

## 使い方

```bash
cd /Users/morimotoyasuhito/kizukikumitate

# 1. 枚数と概算費用、プロンプトの仕上がりを確認（APIを叩かない）
python3 scripts/gen-zukan-art.py plan data/art-specs/<name>.json

# 2. 生成 → コンタクトシート → WebP化 まで一気に
python3 scripts/gen-zukan-art.py run data/art-specs/<name>.json

# 3. コンタクトシートを目視し、外れたカットだけ引き直す
python3 scripts/gen-zukan-art.py gen data/art-specs/<name>.json --only 07-xxx,15-yyy --force
python3 scripts/gen-zukan-art.py build data/art-specs/<name>.json
```

- **ネットワーク**: `generativelanguage.googleapis.com` はサンドボックス不許可。
  Claude Code から実行するときは `dangerouslyDisableSandbox: true` が必要。
- **APIキー**: 環境変数 `GEMINI_API_KEY`、無ければ `~/Downloads/gemini-key.txt`。
  aistudio.google.com/apikey で発行（Billing有効化必須・本人確認は不要）。
  ★森本さんはファイル保存が苦手なので「サイトでコピー → こちらが `pbpaste > ファイル`」が確実。
- **費用**: 1枚 約¥7。23枚で¥150前後。失敗して引き直した分も課金される。
- 原本PNGは `.art-raw/<name>/`（gitignore済み）。WebPだけをコミットする。

## 仕様JSONの書き方

`data/art-specs/reflection.json` が実例。

```jsonc
{
  "name": "reflection",
  "aspect_ratio": "16:9",        // 4:5 など縦も可
  "anchors": [                    // 画風の見本画像。0枚でもよい
    "~/Documents/notebookLM/Canvaイラスト/リフレクション/01 ジャーナリング（基準）.png"
  ],
  "style": "全カード共通の画風・配色・禁止事項",
  "out_dir": "images/reflection",
  "file_pattern": "{i:03d}-reflection.webp",   // {i}=通し番号 {id}=項目ID
  "webp": { "width": 1600, "quality": 82 },
  "items": [
    { "id": "01-journaling", "prompt": "【人物】…\n【場面】…" }
  ]
}
```

`items` の並び順がそのまま通し番号になる。図鑑ページ側のカード順
（例: `data/reflection-techniques.json`）と一致させること。

## 画風の2系統（どちらかを選ぶ）

| 系統 | 背景 | 使っている図鑑 |
|---|---|---|
| **クリーム地** | アイボリー〜クリームの無地 | リフレクション / 成長の法則 / 知恵 |
| **自然背景** | 森・湖・星空・雪山・野原・夕焼けを1枚ずつ変える | 苦手 / 知恵 / オルタナティブ教育 |

自然背景は「みんな同じ形に見える」対策として森本さんが希望したもの。
共通のフラットタッチは保ったまま、背景だけ変化をつける。

**共通の確定タッチ**: フラットでミニマルなベクター／限定配色（濃紺・マスタード〜金・
ティール・テラコッタ）／小さな人物と大きな余白／金色の細い糸で心の動きを象徴。

## ハマり所（全部やらかした実績あり）

**絵の中身**

- **太陽を描かない**。空の太陽・大きな金色の円は森本さんが不要と判断。
- **顔は避ける**。後ろ姿か横顔にし、真正面・カメラ目線を出さない。
  完全に消したいときは「塗りシルエット or 後ろ姿、目鼻口なし」と強く指示する
  （弱い指示だと、かわいい漫画顔が出る）。
  ★例外: オルタナティブ教育図鑑は群像シーンなので「正面顔OK」と判断された。
- **文字が焼き込まれる**。絵の説明に書いた単語が紙・看板・吹き出しに印字されてしまう。
  - `financial aid form` → 紙に印字される。「空欄の紙」と書き換える
  - 吹き出しを描かせると hex色名（`3C3489`）が漏れる。「空の吹き出し」にする
  - 金貨は「無地の円盤・記号なし・数字なし」と明示する
- **コラージュ・分割**になる。「1枚の情景・文字なし・分割禁止」を毎回入れる。
- **黒い輪郭線**を目立たせない（自然背景系のとき特に）。

**技術**

- **1:1で返ってくる**。`generationConfig.imageConfig.aspectRatio` を必ず指定する。
  スクリプトは実出力の比率も検証し、狂っていたら自動で引き直す（許容±6%。
  4:5指定で 896×1152 ≒0.78 が返るのは正常）。
- **見本画像は2枚渡す**と「人物は毎回別人でよい」が伝わりやすい。1枚だと複製されがち。
- コンタクトシートで**必ず目視**してから組み込む。数枚は必ず外れる。

## HTMLへの組み込み（図鑑ごとに構造が違う）

3パターンあるので、対象ページがどれかを先に確認すること。

1. **配線済み**（リフレクション）… `images/…/00N-….webp` を同名で差し替えるだけ。
2. **プレースホルダあり**（成長の法則）… 漢字紋 `<span class="mon">` を `<img>` に置換し、
   `.card-fig img{object-fit:cover}` を追加する。
3. **JS描画型**（オルタナティブ教育）… `const DATA=[…]` + `render()` 構造。
   カードテンプレとモーダル（`openModal`）の両方に `<img>` を足し、CSSも追加する。

**共通の注意**

- 先頭画像だけ `loading="eager" fetchpriority="high"`、以降は `loading="lazy"`。
- `aspect-ratio` は親divに付けると flex子要素で潰れる。
  **imgに直接** `width:100%; height:auto; aspect-ratio:16/9; object-fit:cover` を持たせる。
- **紋（焼印）を絵に替えたら、本文の説明と食い違わないか確認する**。
  「各カードの焼印が系統を示す」→「各カードの色（バッジ）が…」への修正が過去に必要だった。
- 確認は `./.claude/scripts/mobile-preflight.sh full <page>.html`。
  ただし **lazy画像はlocalhostのスクショに写らないことがある**ので、
  確実に見たいときは Playwright で `file://` を開く。

## 終わったら

- `python3 scripts/gen-zukan-art.py plan …` の出力（枚数・費用）を報告に含める。
- 仕様JSONは**必ずコミットする**。次に引き直すとき、これが無いと再現できない。

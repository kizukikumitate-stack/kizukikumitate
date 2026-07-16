#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
未来のリスク計算機シリーズ（6本）の共通パーツを一括で入れる／更新する。

6本は CSS も JS もコピペで共有しているため、共通の文言を1本ずつ手で直すと必ず
どれかが取り残される。このスクリプトが「共通パーツの正」を持ち、冪等に流し込む。

入れているもの:
  1. ソース冒頭のライセンスコメント（シリーズ番号つき）
  2. 大きな数字の隣の「簡易試算」バッジ  ── 数字だけスクショされたときの保険
  3. ※注記の末尾に 出典リンク＋免責  ── 出典は必ず生きているURLだけを書く
  4. ライセンス表記＋版（ver）＋ハブページへの導線

使い方:
    python3 scripts/update-calculators.py            # 反映
    python3 scripts/update-calculators.py --check    # 差分が出るかだけ確認（CI用）

版を上げるとき: VERSION と VERSION_DATE を書き換えて実行し、
risk-calculators.html の変更履歴に1項目足す。
"""
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VERSION = "1.0"
VERSION_DATE = "2026-07-15"
VERSION_DATE_JA = "2026年7月15日"
HUB = "risk-calculators.html"

# 出典はすべて到達確認済みのURLのみ。リンク切れを載せるのは本末転倒なので、
# 追加するときは必ず curl で 200 を確認してから書くこと。
IPSS = '<a href="https://www.ipss.go.jp/pp-zenkoku/j/zenkoku2023/pp_zenkoku2023.asp" target="_blank" rel="noopener">日本の将来推計人口（2023年推計・出生中位）</a>'
MHLW_VITAL = '<a href="https://www.mhlw.go.jp/toukei/list/81-1a.html" target="_blank" rel="noopener">人口動態統計</a>'
MHLW_LIFE = '<a href="https://www.mhlw.go.jp/toukei/saikin/hw/life/life24/index.html" target="_blank" rel="noopener">簡易生命表</a>'
MHLW_KAIGO = '<a href="https://www.mhlw.go.jp/topics/kaigo/toukei/joukyou.html" target="_blank" rel="noopener">介護保険事業状況報告</a>'
EGOV_SCHOOL = '<a href="https://laws.e-gov.go.jp/law/333AC0000000116" target="_blank" rel="noopener">義務教育標準法</a>'

# path -> (シリーズ番号, タイトル, 出典の一文)
PAGES = {
    "customer-age-timebomb.html": (
        "01", "顧客の平均年齢時限爆弾",
        f"出典：年齢帯別の死亡率は厚生労働省「{MHLW_LIFE}」の近似値。",
    ),
    "recruitment-extinction.html": (
        "02", "採用市場消滅計算機",
        f"出典：出生数は厚生労働省「{MHLW_VITAL}」の実績値。",
    ),
    "tax-revenue-countdown.html": (
        "03", "税収カウントダウン",
        # 人口は利用者入力。IPSS の推計値は使っていない（使っているのは生命表近似の死亡率だけ）
        f"出典：人口・財政の数値は利用者が入力したもので、外部の統計データは使っていません。"
        f"加齢にともなう年齢帯別の死亡率のみ、厚生労働省「{MHLW_LIFE}」の近似値を使っています。",
    ),
    "skill-succession-timebomb.html": (
        "04", "技能承継時限爆弾",
        "出典：外部の統計データは使っていません（入力された数字だけで計算しています）。",
    ),
    "school-consolidation-countdown.html": (
        "05", "学校統廃合カウントダウン",
        # 出生数は利用者入力のみ。人口動態統計の実績値は読み込んでいない
        f"出典：出生数は利用者が入力したもので、外部の統計データは使っていません。"
        f"学級編制の考え方は{EGOV_SCHOOL}を参照していますが、"
        "本ページの目安（48人・24人）は簡略化したもので、実際の基準は各自治体の方針で異なります。",
    ),
    "caregiving-capacity-calculator.html": (
        "06", "介護の支え手計算機",
        f"出典：人口は国立社会保障・人口問題研究所「{IPSS}」の近似値、"
        f"要介護認定率・介護職員数は厚生労働省「{MHLW_KAIGO}」の概数。",
    ),
}

DISCLAIMER = (
    "本計算機の結果は簡易な試算であり、将来を保証するものではありません。"
    "これに基づく判断・意思決定の結果について当工房は責任を負いかねます。"
)

MARK_START = "<!-- CALC-COMMON START -->"
MARK_END = "<!-- CALC-COMMON END -->"

BADGE_CSS_ANCHOR = "  .note { font-size: 0.72rem; line-height: 1.95; color: var(--ink-soft); }"
BADGE_CSS = """  /* 「簡易試算」バッジ。大きな数字と但し書きは画面にして数スクロール離れているため、
     数字だけスクショされると前提が一切伝わらない。数字の隣に置いて一緒に写るようにする */
  .approx { display: inline-block; font-family: 'Jost', 'Noto Serif JP', sans-serif; font-size: 0.62rem; letter-spacing: 0.12em; padding: 0.15em 0.7em; border-radius: 999px; border: 1px solid rgba(250,248,242,0.45); color: rgba(250,248,242,0.8); white-space: nowrap; align-self: center; }
  /* ライセンス表記。サイト共通フッターとは別物なので footer 要素ではなく div で作る
     （footer 要素にすると scripts/update-nav.py の locate_footer がこちらを先に掴み、
     マーカー破損時に誤置換される。同じ理由でこのコメントにもタグ名を書かない） */
  .license { margin-top: 1.8rem; padding-top: 1rem; border-top: 1px solid var(--line); font-size: 0.7rem; line-height: 1.85; color: var(--ink-soft); }
  .license a { color: var(--teal); }
  .license .ver { font-family: 'Jost', sans-serif; letter-spacing: 0.06em; color: var(--ink); font-weight: 600; }"""

BADGE_HTML = '<span class="approx">簡易試算</span>'


def build_common(num, title, source):
    """※注記の下に入る共通ブロック（出典・免責・ライセンス・版）。

    ★ <p> は必ず1行で書く。句読点の後で改行すると mobile-preflight の
      Pattern A（句読点孤立・widow の原因）に引っかかる。
    """
    note = (f'{source}<br>{DISCLAIMER}'
            f'前提・出典の詳細と変更履歴は <a href="./{HUB}" style="color:var(--teal)">未来のリスク計算機について</a> にまとめています。')
    return f"""{MARK_START}
    <p class="note" style="margin-top:0.8rem">{note}</p>
    <div class="license">
      &copy; 2026 きづきくみたて工房（<a href="./index.html">kizukikumitate.com</a>）　<span class="ver">ver {VERSION}</span>（{VERSION_DATE_JA}）<br>
      この計算機は、いただくご意見を反映しながら育てています。前提や数字におかしな点があれば <a href="mailto:y.morimoto@kizukikumitate.com?subject=%E6%9C%AA%E6%9D%A5%E3%81%AE%E3%83%AA%E3%82%B9%E3%82%AF%E8%A8%88%E7%AE%97%E6%A9%9F%E3%81%B8%E3%81%AE%E3%81%94%E6%84%8F%E8%A6%8B%EF%BC%88{urllib.parse.quote(title)}%20ver%20{VERSION}%EF%BC%89">ご意見</a> をお寄せください。<br>
      本計算機は <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ja" rel="license noopener" target="_blank">CC BY-NC-SA 4.0</a> で公開しています。非営利での利用・改変・再配布は、クレジット表記と同条件での公開を条件に自由です。改変した場合はその旨を明記し、当工房の試算としては示さないでください。商用利用をご希望の場合は <a href="./index.html#contact">お問い合わせ</a> ください。
    </div>
{MARK_END}"""


def header_comment(num, title):
    return (
        "<!DOCTYPE html>\n"
        "<!--\n"
        f"  未来リスク計算機シリーズ {num} {title}\n"
        "  (c) 2026 きづきくみたて工房 森本康仁 (kizukikumitate.com)\n"
        f"  version: {VERSION} ({VERSION_DATE})\n"
        "  License: CC BY-NC-SA 4.0\n"
        "  https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ja\n"
        "  非営利利用: クレジット表記＋同ライセンス継承で自由\n"
        "  商用利用: 要事前許諾 → kizukikumitate.com へご相談ください\n"
        "-->"
    )


def process(path, num, title, source):
    p = ROOT / path
    s = orig = p.read_text(encoding="utf-8")

    # --- 1. 冒頭コメント（版つきに置き換え。既存の版なしコメントも拾う） ---
    s = re.sub(r"^<!DOCTYPE html>\n<!--\n  未来リスク計算機シリーズ.*?-->",
               lambda m: header_comment(num, title), s, count=1, flags=re.S)
    if not s.startswith("<!DOCTYPE html>\n<!--"):
        s = s.replace("<!DOCTYPE html>", header_comment(num, title), 1)

    # --- 2. CSS ---
    if ".approx {" not in s:
        if BADGE_CSS_ANCHOR not in s:
            raise SystemExit(f"{path}: note の CSS が見つかりません")
        s = s.replace(BADGE_CSS_ANCHOR, BADGE_CSS_ANCHOR + "\n" + BADGE_CSS, 1)
    # 旧版（ライセンス追加時）の .license CSS が残っていれば重複するので消す
    s = re.sub(
        r"\n  /\* ライセンス表記（CC BY-NC-SA 4\.0）。.*?\n  \.license a \{ color: var\(--teal\); \}",
        "", s, count=1, flags=re.S)

    # --- 3. バッジを大きな数字の隣に ---
    if BADGE_HTML not in s:
        m = re.search(r'(<span class="fuse-big" id="fuseBig">.*?</span>)', s)
        if not m:
            raise SystemExit(f"{path}: fuse-big が見つかりません")
        s = s.replace(m.group(1), m.group(1) + "\n        " + BADGE_HTML, 1)

    # --- 4. 共通ブロック（マーカーがあれば中身を差し替え＝冪等） ---
    block = build_common(num, title, source)
    if MARK_START in s:
        s = re.sub(re.escape(MARK_START) + r".*?" + re.escape(MARK_END), lambda m: block, s, count=1, flags=re.S)
    else:
        # 旧版のライセンス div を撤去してから入れ直す
        s = re.sub(r'\n    <div class="license">\n.*?\n    </div>', "", s, count=1, flags=re.S)
        anchor = "  </div>\n</section>\n\n<!-- KAIYU START -->"
        if s.count(anchor) != 1:
            raise SystemExit(f"{path}: 差し込み先が {s.count(anchor)} 個")
        s = s.replace(anchor, block + "\n" + anchor, 1)

    if s != orig:
        return s
    return None


def main():
    check = "--check" in sys.argv
    changed = 0
    for path, (num, title, source) in PAGES.items():
        out = process(path, num, title, source)
        if out is None:
            print(f"  ✅ {path}: 変更なし")
            continue
        changed += 1
        if check:
            print(f"  ⚠️  {path}: 差分あり（--check のため書き込みません）")
        else:
            (ROOT / path).write_text(out, encoding="utf-8")
            print(f"  ✏️  {path}: 共通パーツを更新（{num} {title} / ver {VERSION}）")
    print(f"完了: {changed} ページ（対象 {len(PAGES)} ページ / ver {VERSION}）")
    if check and changed:
        sys.exit(1)


if __name__ == "__main__":
    main()

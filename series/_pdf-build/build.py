#!/usr/bin/env python3
"""BEM 診断結果 PDF を生成する。

使い方:
    python3 build.py            # 全タイプ生成
    python3 build.py A          # Type A のみ生成

生成された PDF は ../assets/pdf/type-{a-e}.pdf に出力される。
HTML テンプレート: template.html
タイプ別データ: 本ファイル内の TYPES 辞書
ロゴ: ../../logo.png
"""
from __future__ import annotations
import base64
import html
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent.parent  # kizukikumitate/
TEMPLATE = ROOT / "template.html"
LOGO = PROJECT_ROOT / "logo.png"
OUTPUT_DIR = PROJECT_ROOT / "series" / "assets" / "pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# タイプカラー (diagnostic.html と同じ)
COLORS = {
    "A": ("#2563eb", "#eff6ff"),
    "B": ("#0891b2", "#ecfeff"),
    "C": ("#d97706", "#fffbeb"),
    "D": ("#475569", "#f8fafc"),
    "E": ("#059669", "#ecfdf5"),
}

# ============================================================
# タイプ別データ
# ============================================================
TYPES = {
    "A": {
        "name": "情報・フィードバック構造型",
        "subtitle": "E1 優位",
        "headline": "あなたの組織は「期待水準とフィードバックの設計」にボトルネックがあります。",
        "scores": {"E1": (8, 8), "E2": (4, 8), "E3": (5, 12), "I1": (2, 4)},
        "dominant": ["E1"],
        "diagnosis": "Gilbert (1978) の BEM では、組織のパフォーマンスを左右する6つの構造のうち、E1 (情報・フィードバック・期待水準) が最初の介入対象とされています。あなたの組織はこの E1 領域に最も大きなギャップがあると診断されました。これは、研修によるスキル付与では解決しません。情報設計とフィードバック構造の再設計が必要です。",
        "symptoms": [
            "1on1を導入しても雑談化する",
            "評価制度が処遇配分の道具になっている",
            "「察してくれ」型の暗黙知文化が根強い",
            "目標管理が形式化している",
            "期待水準が明示されず、各自の解釈で動いている",
        ],
        "articles": [
            ("④", "1on1が雑談で終わる構造", "上司にスキルもインセンティブもない仕組みの中で、1on1だけ導入される問題"),
            ("⑧", "エンゲージメントサーベイ依存症", "測ることが構造改革の代替になっている問題"),
            ("⑨", "評価制度の処遇配分ツール化", "本来のフィードバック機能が失われている問題"),
            ("⑫", "対話がフォーマットになるとき", "対話・心理的安全性の概念が形骸化する構造"),
        ],
        "actions": [
            ("関連記事を読み、自社の症状を言語化する", "上記4記事から、最も近い症状を特定"),
            ("30分相談で E1 構造を一緒に整理する", "期待水準・フィードバック構造の現状診断"),
            ("メルマガで継続的なアップデートを受け取る", "新着記事・実務テンプレートの優先案内"),
        ],
    },
    "B": {
        "name": "資源・時間構造型",
        "subtitle": "E2 優位",
        "headline": "あなたの組織は「業務量とプロセスの設計」にボトルネックがあります。",
        "scores": {"E1": (4, 8), "E2": (8, 8), "E3": (5, 12), "I1": (2, 4)},
        "dominant": ["E2"],
        "diagnosis": "Gilbert の BEM における E2 (資源・ツール・時間・プロセス) は、「人がやろうとしてもできない」状態を生み出す構造領域です。あなたの組織は、能力の問題ではなく、資源と時間の構造に最大のボトルネックがあります。これは「タイムマネジメント研修」では解決しません。業務量・工数・プロセス設計そのものの再構築が必要です。",
        "symptoms": [
            "マネジャーのプレイングマネジャー化が進行している",
            "部下育成の時間が物理的に確保できない",
            "ツール・システムが業務を妨げている",
            "部門間プロセスの分断が深刻",
            "兼務だらけで、本業に集中する時間がない",
        ],
        "articles": [
            ("③", "マネジャーに育成の時間はあるか", "プレイングマネジャー化の構造とコーチング研修の限界"),
            ("⑥", "時間管理研修という延命装置", "業務量問題を個人スキルで補わせる延命策の限界"),
            ("⑬", "キャリア自律の押し付け", "選択肢が整備されていないなかで自律を求める構造"),
            ("⑮", "メンタル問題の個人化", "業務量の構造問題を個人のストレス管理に押し付ける問題"),
        ],
        "actions": [
            ("関連記事で「時間と資源の構造」を診断するレンズを獲得", "上記4記事から、最も近い症状を特定"),
            ("30分相談で「育成時間の捻出」を構造から考える", "プロセス再設計のヒントを共有"),
            ("メルマガで継続的なアップデートを受け取る", "新着記事・実務テンプレートの優先案内"),
        ],
    },
    "C": {
        "name": "インセンティブ構造型",
        "subtitle": "E3 優位",
        "headline": "あなたの組織は「評価と望ましい行動の不整合」にボトルネックがあります。",
        "scores": {"E1": (4, 8), "E2": (4, 8), "E3": (11, 12), "I1": (2, 4)},
        "dominant": ["E3"],
        "diagnosis": "Gilbert の BEM における E3 (インセンティブ・帰結) は、「人がやらない理由」を生み出す構造領域です。あなたの組織は、能力ではなく、望ましい行動が報われない構造に最大のボトルネックがあります。これはリーダー研修やバリュー策定では解決しません。評価制度・処遇・承認構造そのものの再設計が必要です。BEM の中でも E3 は最も診断されにくく、しかし最も介入効果が大きい領域です。",
        "symptoms": [
            "リーダーシップ研修を打ってもリーダーが育たない",
            "バリューが掲示物で終わっている",
            "育成行動が報われない構造",
            "数字成果の偏重 / 減点主義",
            "言うことと評価されることが分離している",
        ],
        "articles": [
            ("②", "リーダー研修で育たないリーダー", "E3 が逆向きに働く構造のなかでリーダー研修を打つ違和感"),
            ("⑦", "バリューが掲示物で終わる", "評価制度に組み込まれず、日々の判断基準として機能しない"),
            ("⑩", "ハラスメント研修の年次行事化", "帰結のない儀式と組織風土問題のすれ違い"),
            ("⑪", "心理的安全性の希釈", "発言が報われない構造で「心理的安全性」を導入する問題"),
            ("⑰", "シニアにモチベ研修を打つ前に", "役割再構築の構造問題を個人の心持ちにしてしまう問題"),
        ],
        "actions": [
            ("関連記事で「インセンティブが逆向きに働く構造」を特定する", "上記5記事から、最も近い症状を特定"),
            ("30分相談で評価制度と望ましい行動のギャップを構造化する", "E3 構造の現状診断"),
            ("メルマガで継続的なアップデートを受け取る", "新着記事・実務テンプレートの優先案内"),
        ],
    },
    "D": {
        "name": "構造複合型",
        "subtitle": "E1 + E2 + E3 すべて高",
        "headline": "あなたの組織は複数の構造領域に同時に課題を抱えています。",
        "scores": {"E1": (7, 8), "E2": (7, 8), "E3": (11, 12), "I1": (2, 4)},
        "dominant": ["E1", "E2", "E3"],
        "diagnosis": "BEM の3つの環境セル (E1・E2・E3) すべてに高いスコアが出ているのは、問題が複合化している組織の典型的なパターンです。この場合、単発の介入では効果が薄く、構造的な順序立てが必要です。推奨される介入順序は E3 → E1 → E2 です。インセンティブ構造を再設計しないと、情報設計や資源配分を変えても元に戻る力が働くためです。30分相談を優先的に検討することを推奨します。",
        "symptoms": [
            "改革を打っても局所最適化に終わる",
            "全方位的な機能不全に陥っている",
            "「何から手をつけていいか分からない」状態",
            "経営と現場の景色のズレが大きい",
            "問題が連鎖していて、単発の打ち手では効かない",
        ],
        "articles": [
            ("①", "研修で解けない問題を、研修で解こうとする", "シリーズの入口・BEM全体像"),
            ("⑤", "「研修やったのに変わらない」はなぜか", "Kirkpatrick L3-L4 不在の構造問題"),
            ("⑭", "人的資本経営という空語", "IR文脈と現場の断絶という複合問題"),
            ("⑯", "早期離職フォロー研修症候群", "配属・労働条件・キャリア設計の構造問題"),
            ("⑱", "女性活躍の構造盲点", "数値目標と研修だけで構造に触れない問題"),
        ],
        "actions": [
            ("30分相談を優先的に検討する", "複合型は単発記事だけでは構造化が難しいため最優先"),
            ("シリーズ全体を順番に読む", "Phase 1 から順に読み進めることで構造化が進む"),
            ("メルマガで継続的なアップデートを受け取る", "新着記事・実務テンプレートの優先案内"),
        ],
    },
    "E": {
        "name": "スキル特化型",
        "subtitle": "I1 優位 (まれなケース)",
        "headline": "あなたの組織は「環境構造は機能している、純粋なスキル課題」に直面しています。",
        "scores": {"E1": (3, 8), "E2": (3, 8), "E3": (4, 12), "I1": (4, 4)},
        "dominant": ["I1"],
        "diagnosis": "BEM 観点で I1 (個人の知識・スキル) のみが顕著で、E1〜E3 が機能している組織は、実は組織開発の現場でも稀なケースです。Gilbert の研究では、組織のパフォーマンス問題の約75-85%は環境要因に起因するとされており、純粋に I1 が原因となるのは少数派です。そのため、HPI の観点で「真にスキル不足か」を再検証することを推奨します。再検証の結果、本当に I1 が中心の課題であれば、研修・OJT・経験学習設計が主軸の打ち手になります。",
        "symptoms": [
            "期待・フィードバック・インセンティブはおおむね機能している",
            "業務量・ツールも妥当な範囲",
            "真に知識・スキルの不足が中心の課題",
            "BEM 観点では研修 (I1 介入) が主たる打ち手として正当化される",
            "ただし HPI 観点での再検証が望ましい",
        ],
        "articles": [
            ("①", "研修で解けない問題を、研修で解こうとする", "BEM 全体像と HPI 再検証の起点"),
            ("⑤", "「研修やったのに変わらない」はなぜか", "L3-L4 で測ったときに見えてくる構造"),
        ],
        "actions": [
            ("関連記事で BEM の他のセルを再点検", "本当に E1〜E3 が機能しているか確認"),
            ("必要に応じて30分相談", "HPI 観点での再診断をサポート"),
            ("メルマガで研修設計の補足情報を継続的に受け取る", "新着記事・実務テンプレートの優先案内"),
        ],
    },
}

# BEM セル名 (共通)
CELL_LABELS = {
    "E1": ("情報・フィードバック", "期待水準・データ・気づきの設計"),
    "E2": ("資源・時間", "ツール・プロセス・工数の設計"),
    "E3": ("インセンティブ・帰結", "評価・承認・処遇の設計"),
    "I1": ("個人能力", "知識・スキル"),
}


def encode_logo() -> str:
    """ロゴを base64 data URL にエンコード（Chrome headless でローカル画像を確実に読むため）"""
    with open(LOGO, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{encoded}"


def render_bem_cells(data: dict) -> str:
    cells = []
    for cell in ["E1", "E2", "E3", "I1"]:
        cell_name, cell_desc = CELL_LABELS[cell]
        is_dominant = cell in data["dominant"]
        dom_class = " dominant" if is_dominant else ""
        marker = '<span class="bem-cell-marker">★</span>' if is_dominant else ""
        cells.append(f"""<div class="bem-cell{dom_class}">
  {marker}
  <span class="bem-cell-pill">{cell}</span>
  <p class="bem-cell-name">{html.escape(cell_name)}</p>
  <p class="bem-cell-desc">{html.escape(cell_desc)}</p>
</div>""")
    return "\n".join(cells)


def render_score_rows(data: dict) -> str:
    rows = []
    for cell in ["E1", "E2", "E3", "I1"]:
        score, max_score = data["scores"][cell]
        cell_name, cell_desc = CELL_LABELS[cell]
        is_dominant = cell in data["dominant"]
        dom_class = " dominant" if is_dominant else ""
        rows.append(f"""<tr class="score-row">
  <td style="width:60px;"><span class="score-cell-pill{dom_class}">{cell}</span></td>
  <td>
    <div class="score-cell-name">{html.escape(cell_name)}</div>
    <div class="score-cell-desc">{html.escape(cell_desc)}</div>
  </td>
  <td class="score-num{dom_class}">{score} / {max_score}</td>
</tr>""")
    return "\n".join(rows)


def render_symptoms(items: list[str]) -> str:
    return "\n".join(f"<li>{html.escape(item)}</li>" for item in items)


def render_articles(items: list[tuple[str, str, str]]) -> str:
    out = []
    for num, title, desc in items:
        out.append(f"""<div class="article-item">
  <div class="article-num">{html.escape(num)}</div>
  <div class="article-content">
    <p class="article-title">{html.escape(title)}</p>
    <p class="article-desc">{html.escape(desc)}</p>
  </div>
</div>""")
    return "\n".join(out)


def render_actions(items: list[tuple[str, str]]) -> str:
    out = []
    for i, (title, desc) in enumerate(items, 1):
        out.append(f"""<div class="action-item">
  <div class="action-num">{i}</div>
  <div class="action-content">
    <p class="action-title">{html.escape(title)}</p>
    <p class="action-desc">{html.escape(desc)}</p>
  </div>
</div>""")
    return "\n".join(out)


def build_html(type_letter: str, logo_data_url: str) -> str:
    data = TYPES[type_letter]
    accent, accent_light = COLORS[type_letter]
    template = TEMPLATE.read_text(encoding="utf-8")

    replacements = {
        "{{TYPE_LETTER}}": type_letter,
        "{{TYPE_NAME}}": data["name"],
        "{{TYPE_SUBTITLE}}": data["subtitle"],
        "{{TYPE_HEADLINE}}": html.escape(data["headline"]),
        "{{ACCENT_COLOR}}": accent,
        "{{ACCENT_LIGHT}}": accent_light,
        "{{LOGO_DATA_URL}}": logo_data_url,
        "{{BEM_CELLS}}": render_bem_cells(data),
        "{{SCORE_ROWS}}": render_score_rows(data),
        "{{DIAGNOSIS_BODY}}": html.escape(data["diagnosis"]),
        "{{SYMPTOM_ITEMS}}": render_symptoms(data["symptoms"]),
        "{{ARTICLE_ITEMS}}": render_articles(data["articles"]),
        "{{ACTION_ITEMS}}": render_actions(data["actions"]),
    }
    out = template
    for key, value in replacements.items():
        out = out.replace(key, value)
    return out


def generate_pdf(type_letter: str, logo_data_url: str) -> Path:
    """1タイプぶんのHTMLを Chrome headless でPDFに変換する"""
    html_content = build_html(type_letter, logo_data_url)
    out_path = OUTPUT_DIR / f"type-{type_letter.lower()}.pdf"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(html_content)
        tmp_path = tmp.name

    chrome_profile = tempfile.mkdtemp(prefix="chrome-pdf-")
    if out_path.exists():
        out_path.unlink()
    try:
        cmd = [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            f"--user-data-dir={chrome_profile}",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",
            f"--print-to-pdf={out_path}",
            f"file://{tmp_path}",
        ]
        # Chrome sometimes hangs after writing PDF; wait for file to appear, then kill.
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import time
        deadline = time.time() + 45
        while time.time() < deadline:
            if out_path.exists() and out_path.stat().st_size > 1024:
                # Wait briefly for write to finish
                time.sleep(0.5)
                last_size = out_path.stat().st_size
                time.sleep(0.5)
                if out_path.stat().st_size == last_size:
                    break
            if proc.poll() is not None:
                break
            time.sleep(0.2)
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        if not out_path.exists():
            print(f"[ERROR] Type {type_letter}: PDF not created", file=sys.stderr)
            sys.exit(1)
        size_kb = out_path.stat().st_size // 1024
        print(f"[OK]  Type {type_letter}: {out_path.name} ({size_kb} KB)")
    finally:
        Path(tmp_path).unlink(missing_ok=True)
        import shutil
        shutil.rmtree(chrome_profile, ignore_errors=True)

    return out_path


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(TYPES.keys())
    targets = [t.upper() for t in targets]
    logo_data_url = encode_logo()
    for t in targets:
        if t not in TYPES:
            print(f"[SKIP] Unknown type: {t}", file=sys.stderr)
            continue
        generate_pdf(t, logo_data_url)


if __name__ == "__main__":
    main()

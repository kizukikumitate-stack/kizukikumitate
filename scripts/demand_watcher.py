#!/usr/bin/env python3
"""
demand_watcher.py — 検索ワードから新サービス候補を起案する週次ウォッチャー

流れ:
  1. seed_keywords ごとに Googleサジェスト（無料・認証不要）を収集
     （五十音・アルファベット掛け合わせで各シードあたり最大80件程度）
  2. 意図語（失敗/意味ない/定着しない…）で需要スコアを付与
  3. assets.yaml の既存資産とマッチング
     - マッチあり → 「既存資産の強化提案」（該当ページにセクション追加等）
     - マッチなし & スコア閾値以上 → 「新サービス候補」
  4. Gemini API で新サービス候補ごとに一枚企画（想定顧客/提供形態/価格帯/流用資産）を生成
  5. Markdownレポートを reports/ に出力し、GitHub Issue として起票

必要な環境変数:
  GEMINI_API_KEY   (任意。無ければ起案文はテンプレのみ)
  GSC_CREDENTIALS  (任意。Search Console のサービスアカウントJSON。あれば自サイト実クエリも取得)
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = yaml.safe_load((ROOT / "config" / "assets.yaml").read_text(encoding="utf-8"))
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

SUGGEST_URL = "https://suggestqueries.google.com/complete/search?client=firefox&hl=ja&q={q}"

# 掛け合わせ文字（多すぎるとリクエスト過多になるので厳選）
EXPANSIONS = ["", " "] + [f" {c}" for c in "あかさたなはまやらわ"] + [" 失敗", " 意味", " 効果", " やり方", " 事例", " 比較"]


def fetch_suggest(query: str) -> list[str]:
    url = SUGGEST_URL.format(q=urllib.parse.quote(query))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8", errors="ignore"))
            return data[1] if len(data) > 1 else []
    except Exception as e:
        print(f"  [warn] suggest failed for '{query}': {e}", file=sys.stderr)
        return []


def collect_keywords(seed_limit: int = 0) -> dict[str, int]:
    """サジェストを収集し、出現回数（=複数経路で出てくるほど需要が太い）を数える"""
    counts: dict[str, int] = defaultdict(int)
    seeds = CONFIG["seed_keywords"]
    if seed_limit:
        seeds = seeds[:seed_limit]
    for seed in seeds:
        for exp in EXPANSIONS:
            for s in fetch_suggest(seed + exp):
                s = s.strip()
                if s and s != seed:
                    counts[s] += 1
            time.sleep(0.4)  # 行儀よく
    return dict(counts)


def fetch_gsc_queries() -> dict[str, int]:
    """Search Console から自サイトの実クエリを取得（任意）"""
    creds_json = os.environ.get("GSC_CREDENTIALS")
    if not creds_json:
        return {}
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        creds = service_account.Credentials.from_service_account_info(
            json.loads(creds_json),
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )
        svc = build("searchconsole", "v1", credentials=creds)
        body = {
            "startDate": "2026-01-01",
            "endDate": str(date.today()),
            "dimensions": ["query"],
            "rowLimit": 500,
        }
        resp = svc.searchanalytics().query(
            siteUrl="sc-domain:kizukikumitate.com", body=body
        ).execute()
        return {r["keys"][0]: int(r.get("impressions", 0)) for r in resp.get("rows", [])}
    except Exception as e:
        print(f"[warn] GSC取得スキップ: {e}", file=sys.stderr)
        return {}


def is_noise(kw: str) -> bool:
    """業種違いの同名ワードを落とす（例: ゲームの「1on1」＝1対1の対戦）"""
    words = CONFIG["scoring"].get("noise_words") or []
    low = kw.lower()
    return any(w.lower() in low for w in words)


def intent_weight(kw: str) -> int:
    sc = CONFIG["scoring"]["intent_words"]
    if any(w in kw for w in sc["high"]):
        return 3
    if any(w in kw for w in sc["mid"]):
        return 2
    return 1


def match_assets(kw: str) -> list[dict]:
    hits = []
    for asset in CONFIG["assets"]:
        if any(tag in kw for tag in asset["tags"]):
            hits.append(asset)
    return hits


def gemini_propose(keyword_cluster: list[str]) -> str:
    """新サービス候補のクラスタから一枚企画を生成"""
    api_key = os.environ.get("GEMINI_API_KEY")
    prompt = f"""あなたは組織開発コンサルタント「きづきくみたて工房」の企画参謀です。
以下の検索キーワード群は、現在需要が伸びているが当工房に受け皿となる資産がないものです。

キーワード: {", ".join(keyword_cluster[:15])}

工房の強み: BEM/HPIによる行動定着の診断、Kirkpatrick評価、対話ファシリテーション、
デモクラシーフィットネス、図鑑シリーズ（成功と失敗の併記フォーマット）、1on1・フィードバック研修資産。

このキーワード需要に応える新サービスを1つ起案してください。以下の形式で300字以内:
【サービス名案】【想定顧客】【提供形態】【価格帯目安】【流用できる既存資産】【最初の一歩（今週作れる最小ページ）】"""

    if not api_key:
        return "（GEMINI_API_KEY未設定のため自動起案スキップ。上記キーワードを元に手動検討）"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"（Gemini起案失敗: {e}）"


def cluster_orphans(orphans: list[tuple[str, int]]) -> dict[str, list[str]]:
    """資産マッチなしワードを先頭語でざっくりクラスタリング"""
    clusters: dict[str, list[str]] = defaultdict(list)
    for kw, _ in orphans:
        head = kw.split()[0] if " " in kw else kw[:6]
        clusters[head].append(kw)
    return {k: v for k, v in clusters.items() if len(v) >= 2}


def main():
    # --seeds N で種ワードを先頭N件に絞る（ローカル動作確認用）
    seed_limit = 0
    if "--seeds" in sys.argv:
        seed_limit = int(sys.argv[sys.argv.index("--seeds") + 1])

    today = str(date.today())
    print("1/4 サジェスト収集中...")
    counts = collect_keywords(seed_limit)
    print(f"  {len(counts)} 語収集")

    print("2/4 Search Console 取得（任意）...")
    gsc = fetch_gsc_queries()
    for q, imp in gsc.items():
        counts[q] = counts.get(q, 0) + min(imp // 10, 5)  # 表示回数もスコアに加算

    print("3/4 スコアリングと資産マッチ...")
    scored = sorted(
        ((kw, c * intent_weight(kw)) for kw, c in counts.items() if not is_noise(kw)),
        key=lambda x: -x[1],
    )

    strengthen: list[str] = []   # 既存資産の強化提案
    orphans: list[tuple[str, int]] = []  # 新サービス候補の種
    threshold = CONFIG["scoring"]["new_service_threshold"]

    for kw, score in scored[:200]:
        hits = match_assets(kw)
        if hits:
            names = " / ".join(
                f"[{a['name']}](https://kizukikumitate.com{a['url']})" if a.get("url") else a["name"]
                for a in hits[:2]
            )
            strengthen.append(f"| `{kw}` | {score} | {names} |")
        elif score >= threshold:
            orphans.append((kw, score))

    print("4/4 新サービス起案...")
    clusters = cluster_orphans(orphans)
    proposals = []
    for head, kws in list(clusters.items())[:3]:  # 週3案まで
        proposals.append((head, kws, gemini_propose(kws)))

    # レポート生成
    lines = [
        f"# 需要ウォッチャーレポート {today}",
        "",
        "## 📈 需要上位ワード（既存資産で受けられるもの）",
        "",
        "→ 該当ページに悩み別セクション・FAQを追記するとSEOが伸びる候補",
        "",
        "| キーワード | スコア | 受け皿資産 |",
        "|---|---|---|",
        *strengthen[:30],
        "",
        "## 🌱 新サービス候補（受け皿なし & 高スコア）",
        "",
    ]
    if not proposals:
        lines.append("今週は閾値超えの新規クラスタなし。")
    for head, kws, plan in proposals:
        lines += [
            f"### クラスタ「{head}」",
            f"検索ワード: {', '.join(kws[:10])}",
            "",
            plan,
            "",
        ]

    report = "\n".join(lines)
    out = REPORT_DIR / f"demand-{today}.md"
    out.write_text(report, encoding="utf-8")
    print(f"レポート出力: {out}")

    # GitHub Actions から Issue 本文として使えるよう stdout にも出す
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"report_path={out}\n")


if __name__ == "__main__":
    main()

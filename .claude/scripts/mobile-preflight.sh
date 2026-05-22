#!/bin/bash
# ============================================================
# mobile-preflight.sh
#
# kizukikumitate.com の HTML 編集後、コミット前の最終チェックを行う。
#
# 使い方:
#   ./.claude/scripts/mobile-preflight.sh check <file.html>
#   ./.claude/scripts/mobile-preflight.sh shoot <file.html>
#   ./.claude/scripts/mobile-preflight.sh full  <file.html>
#
# - check: 静的 grep チェックのみ（数秒）
# - shoot: iPhone viewport でスクショ取得（Playwright）
# - full : 上記両方
#
# 検出するアンチパターン:
#   A) Multi-line <p> ブロック（句読点孤立の原因）
#   B) 番号+ASCII半角スペース+名称（「筋肉① 好奇心筋」の分断の原因）
#   C) flex-direction: column ブロックで align-items: stretch が抜けている
#   D) モバイル typography ブロックに hanging-punctuation: allow-end が無い
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCREENSHOT_DIR="$REPO_DIR/.claude/screenshots"
PORT=8080

mode="${1:-}"
target="${2:-}"

if [ -z "$mode" ] || [ -z "$target" ]; then
  echo "usage: $0 {check|shoot|full} <file.html>"
  exit 2
fi

if [ ! -f "$REPO_DIR/$target" ]; then
  echo "❌ ファイルが見つかりません: $REPO_DIR/$target"
  exit 2
fi

FILE="$REPO_DIR/$target"

# ============================================================
# 静的 grep チェック
# ============================================================
run_check() {
  echo "🔍 静的チェック: $target"
  echo ""

  local issues=0

  # --- Pattern A: 中文区切り（、）後に改行がある <p> ブロック ---
  # 警告の対象を絞る: 「、」が行末にあり、次行も同じ段落内テキストが続くケース。
  # これが「、孤立」「文中での不自然な改行」を引き起こす実害パターン。
  echo "▶ A. 中文（、）の後に HTML 改行がある <p>（句読点孤立の原因）"
  local pattern_a
  pattern_a=$(perl -0777 -ne '
    my $found = 0;
    while (/<p\b[^>]*>([\s\S]*?)<\/p>/g) {
      my $content = $1;
      my $start = $-[0];
      # 段落内で「、」の直後（任意空白を挟んで）に改行＋次のインデント文字が来るケース
      if ($content =~ /、\s*\n\s+\S/s) {
        my $line = (substr($_, 0, $start) =~ tr/\n//) + 1;
        my $preview = $content;
        $preview =~ s/\s+/ /gs;
        $preview = substr($preview, 0, 80);
        print "   L$line: $preview...\n";
        $found++;
      }
    }
    exit($found > 0 ? 1 : 0);
  ' "$FILE") || true

  if [ -n "$pattern_a" ]; then
    echo "$pattern_a"
    echo "   ⚠️  → <p>...</p> を1行に書き直してください（改行・インデント除去）"
    issues=$((issues + 1))
  else
    echo "   ✅ クリア"
  fi
  echo ""

  # --- Pattern B: 番号+ASCII半角スペース+漢字 ---
  echo "▶ B. 番号+半角スペース+名称（分断の原因）"
  # 丸数字（①〜⑳ U+2460-U+2473 等）の後に ASCII space が続くケース
  # &nbsp; は HTML エンティティなので問題なし
  local pattern_b
  pattern_b=$(grep -nP '[\x{2460}-\x{24FF}\x{3251}-\x{32BF}] [^&<\s]' "$FILE" 2>/dev/null || true)
  if [ -n "$pattern_b" ]; then
    echo "$pattern_b" | sed 's/^/   /'
    echo "   ⚠️  → 番号と名称の間の半角スペースを &nbsp; に置換してください"
    issues=$((issues + 1))
  else
    echo "   ✅ クリア"
  fi
  echo ""

  # --- Pattern C: align-items: flex-start を持つ flex container が ---
  # ---            モバイル column 化された際に align-items override 漏れ ---
  # 今回の実害パターン: PC で `display: flex; align-items: flex-start;` の親が、
  # モバイルで `flex-direction: column` になると、子要素が intrinsic 幅に縮んで本文がはみ出す。
  # 検出方法:
  #   1. 各 selector について全ブロックを走査し、align-items: flex-start を持つか記録
  #   2. その selector の他ブロックで flex-direction: column があるか
  #   3. その column ブロック内で align-items: stretch|center の override があるか
  #   3 が無ければ警告
  echo "▶ C. align-items: flex-start の flex container が mobile column で stretch override 漏れ"
  local pattern_c
  pattern_c=$(perl -0777 -ne '
    my $src = $_;
    # ブロック抽出: selector { body } を非ネスト前提で（@media 内の rule は ok）
    # 各 rule の selector と body をペアで集める
    my @rules;
    while ($src =~ /([\.\#\w][^{}\n]*?)\s*\{([^{}]*)\}/g) {
      my $sel = $1; my $body = $2;
      $sel =~ s/^\s+|\s+$//g;
      next if $sel =~ /^@/;
      my $pos = $-[0];
      my $line = (substr($src, 0, $pos) =~ tr/\n//) + 1;
      push @rules, { sel => $sel, body => $body, line => $line };
    }
    # selector -> 各ブロックの集計
    my %risky;
    for my $r (@rules) {
      if ($r->{body} =~ /align-items:\s*flex-start/ && $r->{body} =~ /display:\s*flex/) {
        $risky{$r->{sel}} = 1;
      }
    }
    my $found = 0;
    for my $r (@rules) {
      next unless $r->{body} =~ /flex-direction:\s*column/;
      next unless $risky{$r->{sel}};
      next if $r->{body} =~ /align-items:\s*(stretch|center)/;
      print "   L$r->{line}: $r->{sel}（PC 側で align-items: flex-start のため override 必要）\n";
      $found++;
    }
    exit($found > 0 ? 1 : 0);
  ' "$FILE") || true

  if [ -n "$pattern_c" ]; then
    echo "$pattern_c"
    echo "   ⚠️  → 同一ブロックに align-items: stretch を追加してください"
    echo "       （アイコンを中央寄せしたい子要素には align-self: center を別途指定）"
    issues=$((issues + 1))
  else
    echo "   ✅ クリア"
  fi
  echo ""

  # --- Pattern D: モバイル typography に hanging-punctuation 抜け ---
  echo "▶ D. モバイル typography ブロックに hanging-punctuation: allow-end 漏れ"
  local has_autophrase has_hanging
  has_autophrase=$(grep -c 'word-break:\s*auto-phrase' "$FILE" || true)
  has_hanging=$(grep -c 'hanging-punctuation:\s*allow-end' "$FILE" || true)
  if [ "$has_autophrase" -gt 0 ] && [ "$has_hanging" -eq 0 ]; then
    echo "   ⚠️  word-break: auto-phrase は設定されているが hanging-punctuation: allow-end が無い"
    echo "   → モバイル typography ブロックに hanging-punctuation: allow-end を追加してください"
    issues=$((issues + 1))
  else
    echo "   ✅ クリア"
  fi
  echo ""

  echo "────────────────────────────────────────"
  if [ "$issues" -eq 0 ]; then
    echo "✅ 静的チェック PASS（4項目すべてクリア）"
    return 0
  else
    echo "❌ $issues 件の改善ポイントが見つかりました"
    return 1
  fi
}

# ============================================================
# ローカル HTTP サーバー起動
# ============================================================
ensure_server() {
  local existing
  existing=$(lsof -ti tcp:$PORT 2>/dev/null || true)
  if [ -n "$existing" ]; then
    echo "🌐 ポート $PORT のサーバーは既に動作中（PID: $existing）"
    return 0
  fi
  echo "🌐 ローカル HTTP サーバーを起動中... (ポート $PORT)"
  (cd "$REPO_DIR" && python3 -m http.server $PORT > /tmp/mobile-preflight-server.log 2>&1 &)
  sleep 1
  STARTED_SERVER=1
}

stop_server() {
  if [ "${STARTED_SERVER:-0}" -eq 1 ]; then
    local pid
    pid=$(lsof -ti tcp:$PORT 2>/dev/null || true)
    if [ -n "$pid" ]; then
      kill -9 "$pid" 2>/dev/null || true
      echo "🛑 サーバー停止 (PID: $pid)"
    fi
  fi
}

# ============================================================
# Playwright で iPhone viewport のスクショ取得
# ============================================================
run_shoot() {
  ensure_server
  trap stop_server EXIT

  # nvm の Node を確実に PATH へ
  export NVM_DIR="$HOME/.nvm"
  if [ -s "$NVM_DIR/nvm.sh" ]; then
    . "$NVM_DIR/nvm.sh"
  fi
  if ! command -v npx >/dev/null 2>&1; then
    for node_dir in "$HOME/.nvm/versions/node"/*/bin; do
      if [ -d "$node_dir" ]; then
        export PATH="$node_dir:$PATH"
        break
      fi
    done
  fi
  if ! command -v npx >/dev/null 2>&1; then
    echo "❌ npx が見つかりません。Node.js（nvm経由）が必要です"
    return 2
  fi

  mkdir -p "$SCREENSHOT_DIR"
  local timestamp
  timestamp=$(date +%Y%m%d_%H%M%S)
  local safe_name
  safe_name=$(echo "$target" | sed 's|[/.]|_|g')
  local out="$SCREENSHOT_DIR/mobile_${safe_name}_${timestamp}.png"

  echo "📸 iPhone viewport でスクショ取得中: $target"
  echo "   出力先: $out"
  echo "   ※初回は Playwright のブラウザ DL に1-2分かかります"
  echo ""

  # Playwright をローカル node_modules に入れる（未インストールなら）
  if [ ! -d "$SCRIPT_DIR/node_modules/playwright" ]; then
    echo "🔽 Playwright をインストール中（初回のみ、数十秒）..."
    (cd "$SCRIPT_DIR" && npm install --no-audit --no-fund --silent)
  fi
  # Chromium ブラウザバイナリを確認・DL
  if ! (cd "$SCRIPT_DIR" && npx playwright install chromium --dry-run 2>&1 | grep -q "is already installed"); then
    echo "🔽 Chromium をインストール中（初回のみ、1-2分）..."
    (cd "$SCRIPT_DIR" && npx playwright install chromium 2>&1 | tail -3)
  fi

  URL="http://localhost:$PORT/$target" OUTPUT="$out" \
    node "$SCRIPT_DIR/mobile-screenshot.mjs"

  echo ""
  echo "✅ スクショ保存完了: $out"
  echo "   Claude/エディタで Read して目視確認してください"
}

# ============================================================
# main
# ============================================================
case "$mode" in
  check)
    run_check
    ;;
  shoot)
    run_shoot
    ;;
  full)
    if run_check; then
      echo ""
      run_shoot
    else
      echo ""
      echo "⚠️  静的チェックで指摘あり。修正後に再実行してください。"
      echo "    スクショだけ撮りたい場合は: $0 shoot $target"
      exit 1
    fi
    ;;
  *)
    echo "usage: $0 {check|shoot|full} <file.html>"
    exit 2
    ;;
esac

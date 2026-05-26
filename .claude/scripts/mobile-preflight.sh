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
  echo "usage: $0 {check|runtime|shoot|full} <file.html>"
  echo "  check   : 静的 grep 検査（Pattern A〜D）"
  echo "  runtime : Playwright で実機 iPhone レンダリング検査（行頭句読点/widow/strict 未適用）"
  echo "  shoot   : iPhone viewport スクショ取得"
  echo "  full    : check → runtime → shoot を順に実行"
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

  # --- Pattern A: 句読点（、。）後に HTML 改行がある葉ノード段落 ---
  # 対象タグ（葉ノード）: <p>, <h1>〜<h6>, <li>, <dt>, <dd>, <blockquote>,
  #                       および見出し的な div: *-bridge / *-heading / *-quote / *-title / *-callout-title
  # ※ 一般 div は内部に複数の <p> を持つため対象外。葉ノードのみチェックする。
  # 「、」「。」の後の HTML 改行 + 「実テキスト続行」が実害（句読点孤立 / widow）の原因
  echo "▶ A. 句読点（、。）の後に HTML 改行があるテキストブロック（句読点孤立・widow の原因）"
  local pattern_a
  pattern_a=$(perl -0777 -ne '
    my $found = 0;
    my @patterns = (
      qr/<(p|h[1-6]|li|dt|dd|blockquote)\b[^>]*>([\s\S]*?)<\/\1>/,
      # heading 的な div（複数の <p> を含まないことを期待）
      qr/<(div)\b[^>]*\bclass\s*=\s*"[^"]*\b(?:bridge|heading|quote|callout-title|visual-quote|visual-sub|hero-title|hero-subtitle|hero-label|manifesto)[\w-]*"[^>]*>([\s\S]*?)<\/\1>/,
    );
    for my $pat (@patterns) {
      while (/$pat/g) {
        my $tag = $1;
        my $content = $2;
        my $start = $-[0];
        # 入れ子の <p> を含む div は除外（その場合は内側の <p> 単体で検査される）
        next if $tag eq "div" && $content =~ /<p\b/;
        # 「、」「。」直後に改行+インデント+実テキスト（閉じタグ / 純空白以外）が続くケースを警告
        if ($content =~ /[、。][ \t]*\n[ \t]+(?=\S)(?!<\/)/s) {
          my $line = (substr($_, 0, $start) =~ tr/\n//) + 1;
          my $preview = $content;
          $preview =~ s/\s+/ /gs;
          $preview = substr($preview, 0, 80);
          print "   L$line: $preview...\n";
          $found++;
        }
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
  # モバイルの @media 内で `flex-direction: column` になると、子要素が intrinsic 幅に
  # 縮んで本文がはみ出す。
  # ※ ベース CSS で最初から column の場合（hero 等）は意図的なので対象外
  # 検出方法（awk による O(n) スキャン）:
  #   1. 各 CSS ブロック { ... } を line-by-line で抽出（@media 内かどうかも記録）
  #   2. selector ごとに「align-items: flex-start + display: flex」を持つかを記録（risky 集合）
  #   3. **@media 内で** flex-direction: column を含むブロックで risky の selector 該当 かつ
  #      同ブロック内に align-items: stretch|center が無いものを警告
  echo "▶ C. align-items: flex-start の flex container が mobile column で stretch override 漏れ"
  local pattern_c
  pattern_c=$(awk '
    function trim(s) { sub(/^[[:space:]]+/, "", s); sub(/[[:space:]]+$/, "", s); return s }
    {
      lines[NR] = $0
      # 行内の { と } の数を集計（ネスト深さ用）
      n_open  = gsub(/\{/, "{")
      n_close = gsub(/\}/, "}")
      opens[NR] = n_open
      closes[NR] = n_close
    }
    END {
      # フェーズ1: すべての非@media rule ブロックを抽出
      # ブロック開始 = 行内に { が現れた地点
      # スタックで管理し、各ブロックの selector / start_line / end_line / 親が@mediaか を保存
      stack_n = 0
      block_n = 0
      for (i = 1; i <= NR; i++) {
        for (k = 0; k < opens[i]; k++) {
          # 新しいブロック開始
          stack_n++
          # selector を取得（{ より前のテキスト + 1つ前の非空行を結合）
          sel = lines[i]
          sub(/\{.*/, "", sel)
          sel = trim(sel)
          if (sel == "") {
            for (j = i - 1; j >= i - 4 && j >= 1; j--) {
              if (lines[j] !~ /^[[:space:]]*$/) {
                sel = lines[j]
                break
              }
            }
            sel = trim(sel)
          }
          stack_sel[stack_n] = sel
          stack_start[stack_n] = i
          # 親スタックに @media があるか判定
          in_media = 0
          for (s = 1; s < stack_n; s++) {
            if (stack_sel[s] ~ /^@media/) { in_media = 1; break }
          }
          stack_in_media[stack_n] = in_media
        }
        for (k = 0; k < closes[i]; k++) {
          # ブロック終了
          if (stack_n <= 0) continue
          sel = stack_sel[stack_n]
          start = stack_start[stack_n]
          in_media = stack_in_media[stack_n]
          stack_n--
          # @media や @keyframes 等の selector 自体は skip
          if (sel ~ /^@/) continue
          block_n++
          block_sel[block_n] = sel
          block_start[block_n] = start
          block_end[block_n] = i
          block_in_media[block_n] = in_media
        }
      }
      # フェーズ2: 各ブロックの body をスキャンして特性を集める
      for (b = 1; b <= block_n; b++) {
        has_flex = 0; has_flexstart = 0; has_column = 0; has_stretch = 0
        for (L = block_start[b]; L <= block_end[b]; L++) {
          if (lines[L] ~ /display:[[:space:]]*flex/) has_flex = 1
          if (lines[L] ~ /align-items:[[:space:]]*flex-start/) has_flexstart = 1
          if (lines[L] ~ /flex-direction:[[:space:]]*column/) has_column = 1
          if (lines[L] ~ /align-items:[[:space:]]*(stretch|center)/) has_stretch = 1
        }
        block_flex[b] = has_flex
        block_flexstart[b] = has_flexstart
        block_column[b] = has_column
        block_stretch[b] = has_stretch
      }
      # フェーズ3: selector ごとに「risky = どこかで display:flex + flex-start」を集計
      for (b = 1; b <= block_n; b++) {
        if (block_flex[b] && block_flexstart[b]) {
          risky[block_sel[b]] = 1
        }
      }
      # フェーズ4: 警告対象 = @media 内で flex-direction: column を持ち、
      #            risky selector で、stretch なし
      # ※ ベース CSS で column の場合は意図的なので対象外
      found = 0
      for (b = 1; b <= block_n; b++) {
        if (block_column[b] && block_in_media[b] && risky[block_sel[b]] && !block_stretch[b]) {
          printf "   L%d: %s（PC 側で align-items: flex-start のため override 必要）\n", block_start[b], block_sel[b]
          found = 1
        }
      }
      if (found) exit 1
    }
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

  # --- Pattern H: OGP / Twitter Card の必須タグ漏れ ---
  # SNS シェア時のカード表示に必要な以下が揃っているかチェック
  echo "▶ H. OGP / Twitter Card の必須タグ確認"
  local pattern_h=""
  local required_og="og:title og:description og:image og:url og:type"
  local required_tw="twitter:card twitter:title twitter:description twitter:image"
  for tag in $required_og; do
    if ! grep -q "property=\"$tag\"" "$FILE"; then
      pattern_h="${pattern_h}   ⚠️ <meta property=\"$tag\"> が見つかりません\n"
    fi
  done
  for tag in $required_tw; do
    if ! grep -q "name=\"$tag\"" "$FILE"; then
      pattern_h="${pattern_h}   ⚠️ <meta name=\"$tag\"> が見つかりません\n"
    fi
  done
  # canonical URL チェック
  if ! grep -q 'rel="canonical"' "$FILE"; then
    pattern_h="${pattern_h}   ⚠️ <link rel=\"canonical\"> が見つかりません\n"
  fi
  # og:url が canonical と一致しているかも確認
  local og_url canonical_url
  og_url=$(grep -oE 'property="og:url"[^>]*content="[^"]*"' "$FILE" | head -1 | sed -E 's/.*content="([^"]*)".*/\1/')
  canonical_url=$(grep -oE 'rel="canonical"[^>]*href="[^"]*"' "$FILE" | head -1 | sed -E 's/.*href="([^"]*)".*/\1/')
  if [ -n "$og_url" ] && [ -n "$canonical_url" ] && [ "$og_url" != "$canonical_url" ]; then
    pattern_h="${pattern_h}   ⚠️ og:url ($og_url) と canonical ($canonical_url) が不一致\n"
  fi
  if [ -n "$pattern_h" ]; then
    printf '%b' "$pattern_h"
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
# Playwright + iPhone viewport で runtime CSS チェック
# ============================================================
run_runtime() {
  ensure_server
  trap stop_server EXIT

  # Node / Playwright のセットアップ（run_shoot と同じ）
  export NVM_DIR="$HOME/.nvm"
  if [ -s "$NVM_DIR/nvm.sh" ]; then . "$NVM_DIR/nvm.sh"; fi
  if ! command -v npx >/dev/null 2>&1; then
    for node_dir in "$HOME/.nvm/versions/node"/*/bin; do
      if [ -d "$node_dir" ]; then export PATH="$node_dir:$PATH"; break; fi
    done
  fi
  if [ ! -d "$SCRIPT_DIR/node_modules/playwright" ]; then
    echo "🔽 Playwright をインストール中（初回のみ）..."
    (cd "$SCRIPT_DIR" && npm install --no-audit --no-fund --silent)
  fi
  # WebKit (Safari エンジン) を使う — Chromium と挙動が違うので必須
  if ! (cd "$SCRIPT_DIR" && npx playwright install webkit --dry-run 2>&1 | grep -q "is already installed"); then
    echo "🔽 WebKit をインストール中（初回のみ）..."
    (cd "$SCRIPT_DIR" && npx playwright install webkit 2>&1 | tail -3)
  fi

  echo "🔬 runtime チェック実行中: $target（WebKit + iPhone SE 375px viewport — 実 Safari と同等）"
  URL="http://localhost:$PORT/$target" \
    node "$SCRIPT_DIR/mobile-runtime-check.mjs"
}

# ============================================================
# main
# ============================================================
case "$mode" in
  check)
    run_check
    ;;
  runtime)
    run_runtime
    ;;
  shoot)
    run_shoot
    ;;
  full)
    if run_check; then
      echo ""
      run_runtime || true   # runtime は警告どまり（exit はしない）
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
    echo "usage: $0 {check|runtime|shoot|full} <file.html>"
    exit 2
    ;;
esac

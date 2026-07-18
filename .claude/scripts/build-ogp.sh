#!/usr/bin/env bash
# ============================================================
# build-ogp.sh
#   data/ogp.json（台帳）から OGP 画像を生成し、各ページに配線する。
#
#   ./.claude/scripts/build-ogp.sh                # 台帳の全ページ
#   ./.claude/scripts/build-ogp.sh --only foo     # img/page 名に foo を含むものだけ
#   ./.claude/scripts/build-ogp.sh --check        # 生成せず欠けを報告（CI/確認用）
#   ./.claude/scripts/build-ogp.sh --no-wire      # 画像生成のみ（HTML不変更）
#
# 新規ページの追加手順:
#   1) data/ogp.json の pages に1エントリ追加（page/img/template/theme/acc/eyebrow/title/sub）
#   2) ./.claude/scripts/build-ogp.sh --only <img>
#   3) 生成された <img> と該当HTMLを commit
# ============================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Node（nvm経由）を PATH に
if ! command -v node >/dev/null 2>&1; then
  for d in "$HOME/.nvm/versions/node"/*/bin; do [ -d "$d" ] && export PATH="$d:$PATH" && break; done
fi
if ! command -v node >/dev/null 2>&1; then
  echo "❌ node が見つかりません（nvm 経由の Node.js が必要）"; exit 1
fi

# playwright（ローカル node_modules）と chromium を用意
if [ ! -d "$SCRIPT_DIR/node_modules/playwright" ]; then
  echo "🔽 playwright を導入中..."; (cd "$SCRIPT_DIR" && npm install playwright@1 >/dev/null 2>&1)
fi
if ! (cd "$SCRIPT_DIR" && npx playwright install chromium --dry-run 2>&1 | grep -q "is already installed"); then
  echo "🔽 Chromium を導入中（初回のみ）..."; (cd "$SCRIPT_DIR" && npx playwright install chromium 2>&1 | tail -2)
fi

node "$SCRIPT_DIR/build-ogp.mjs" "$@"

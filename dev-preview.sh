#!/bin/bash
# ============================================================
# モバイル即時プレビューサーバー起動スクリプト
#
# 使い方:
#   ./dev-preview.sh
#
# 起動すると公開URL（例: https://xxxx.loca.lt）が表示されるので、
# それをスマホのSafariで開く。
# 開発者がローカルでファイルを編集→保存→スマホでリロード
# で即座に確認できる（デプロイ不要）。
# ============================================================

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8080

echo "📂 リポジトリ: $REPO_DIR"
echo ""

# 既存の python サーバーがいたら止める
existing_pid=$(lsof -ti tcp:$PORT 2>/dev/null || true)
if [ -n "$existing_pid" ]; then
  echo "🛑 ポート $PORT で動いている既存サーバーを停止します (PID: $existing_pid)"
  kill -9 $existing_pid 2>/dev/null || true
  sleep 1
fi

# ローカル HTTP サーバーをバックグラウンド起動
echo "🌐 ローカル HTTP サーバーを起動中... (ポート $PORT)"
python3 -m http.server $PORT --directory "$REPO_DIR" > /tmp/dev-preview-server.log 2>&1 &
SERVER_PID=$!
echo "   PID: $SERVER_PID"
echo ""

# 終了時に必ずサーバーも止める
trap "echo ''; echo '🛑 サーバー停止中...'; kill $SERVER_PID 2>/dev/null || true; exit 0" INT TERM EXIT

sleep 1

# トンネル起動（npx localtunnel: インストール不要、無料、サインアップ不要）
echo "🚀 公開トンネルを起動します..."
echo "   ※ 初回は npx が localtunnel をダウンロードするため少し時間がかかります"
echo ""
echo "----------------------------------------------------------"
echo "📱 表示される 'your url is: https://xxxxx.loca.lt' を"
echo "   スマホのSafariで開いてください。"
echo ""
echo "   ⚠️ 初回アクセス時に「Click to Continue」画面が出ますが、"
echo "      パスワードを入力（公開IP のラスト1桁等）して進めてOK"
echo "      ※詳細は loca.lt のページ案内の通り"
echo ""
echo "   停止するには Ctrl+C"
echo "----------------------------------------------------------"
echo ""

# サブドメイン名を kizuki にして毎回同じURLになるよう試みる
# （他の人に取られていなければ https://kizuki-preview.loca.lt が固定で使える）
npx --yes localtunnel --port $PORT --subdomain kizuki-preview 2>&1 || \
npx --yes localtunnel --port $PORT

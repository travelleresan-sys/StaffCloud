#!/bin/bash

# --- 設定 ---
# 仮想環境のディレクトリ名
VENV_DIR="venv"
DEFAULT_PORT=5000

# --- 処理開始 ---
echo "開発環境のセットアップとアプリケーションの起動を開始します..."

# 既存のFlaskプロセスをチェック・終了
echo "Checking for existing Flask processes..."
if pgrep -f "flask run" >/dev/null; then
    echo "Existing Flask processes found. Terminating..."
    pkill -f "flask run"
    sleep 3
    pkill -9 -f "flask run" 2>/dev/null
    sleep 2
fi

# 1. 仮想環境の存在を確認し、なければ作成する
if [ ! -d "$VENV_DIR" ]; then
    echo "仮想環境が見つかりません。新しい仮想環境を作成します: $VENV_DIR"
    python3 -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "仮想環境の作成に失敗しました。処理を中断します。"
        exit 1
    fi
else
    echo "既存の仮想環境が見つかりました: $VENV_DIR"
fi

# 2. 仮想環境を有効化する
source $VENV_DIR/bin/activate

# 3. requirements.txt を使って必要なパッケージをインストールする
echo "requirements.txt から必要なパッケージをインストールします..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "パッケージのインストールに失敗しました。処理を中断します。"
    exit 1
fi

# 4. 利用可能なポートを検索
echo "Checking available port..."
PORT=$DEFAULT_PORT
while lsof -i :$PORT >/dev/null 2>&1; do
    echo "Port $PORT is in use, trying port $((PORT + 1))"
    PORT=$((PORT + 1))
done

# 5. Flaskアプリケーションを起動する
echo "パッケージのインストールが完了しました。"
echo "Flaskアプリケーションを起動します..."
echo ""
echo "================================="
echo "🚀 StaffCloud Starting..."
echo "Port: $PORT"
echo "🌐 Access URLs:"
echo "   - Local:   http://127.0.0.1:$PORT/"
echo "   - Network: http://$(hostname -I | awk '{print $1}'):$PORT/"
echo "================================="
echo ""
flask run --host=0.0.0.0 --port=$PORT

# スクリプトが終了したら、仮想環境は自動的に無効になります
#!/bin/bash

# --- 設定 ---
VENV_DIR="venv"
DEFAULT_PORT=5000
APP_NAME="StaffCloud"

# --- 関数定義 ---
find_free_port() {
    local port=$1
    while lsof -i :$port >/dev/null 2>&1; do
        echo "Port $port is in use, trying port $((port + 1))"
        port=$((port + 1))
    done
    echo $port
}

kill_existing_flask() {
    echo "Checking for existing Flask processes..."
    local pids=$(pgrep -f "flask run")
    if [ ! -z "$pids" ]; then
        echo "Found existing Flask processes: $pids"
        echo "Terminating existing processes..."
        pkill -f "flask run"
        sleep 3
        # 強制終了が必要な場合
        pkill -9 -f "flask run" 2>/dev/null
        sleep 2
        echo "Existing Flask processes terminated."
    else
        echo "No existing Flask processes found."
    fi
}

# --- 処理開始 ---
echo "==========================="
echo "$APP_NAME 起動スクリプト"
echo "==========================="

# 1. 既存のFlaskプロセスを終了
kill_existing_flask

# 2. 仮想環境の確認・作成
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment: $VENV_DIR"
    python3 -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Exiting."
        exit 1
    fi
else
    echo "Using existing virtual environment: $VENV_DIR"
fi

# 3. 仮想環境を有効化
source $VENV_DIR/bin/activate
echo "Virtual environment activated."

# 4. 依存関係をインストール
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt --quiet
    if [ $? -ne 0 ]; then
        echo "Failed to install requirements. Exiting."
        exit 1
    fi
else
    echo "No requirements.txt found, skipping dependency installation."
fi

# 5. 利用可能なポートを検索
AVAILABLE_PORT=$(find_free_port $DEFAULT_PORT)

# 6. Flask環境変数を設定
export FLASK_APP=app.py
export FLASK_ENV=development

# 7. アプリケーションを起動
echo ""
echo "=================================="
echo "🚀 $APP_NAME Starting..."
echo "Port: $AVAILABLE_PORT"
echo "🌐 Access URLs:"
echo "   - Local:   http://127.0.0.1:$AVAILABLE_PORT/"
echo "   - Network: http://$(hostname -I | awk '{print $1}'):$AVAILABLE_PORT/"
echo "=================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

flask run --host=0.0.0.0 --port=$AVAILABLE_PORT
#!/bin/bash

# === StaffCloud スマート起動スクリプト ===
# ポート競合を根本的に解決する統合管理システム

# 設定
VENV_DIR="venv"
APP_NAME="StaffCloud"

echo "=================================================="
echo "🚀 $APP_NAME Smart Launch System"
echo "ポート競合を根本解決する統合管理システム"
echo "=================================================="

# 1. 仮想環境の確認・作成
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment: $VENV_DIR"
    python3 -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
else
    echo "📦 Using existing virtual environment: $VENV_DIR"
fi

# 2. 仮想環境を有効化
source $VENV_DIR/bin/activate
echo "✅ Virtual environment activated"

# 3. 依存関係のインストール
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# 4. Flask Manager を使用して起動
echo ""
echo "🔧 Using advanced Flask process management..."
python flask_manager.py start
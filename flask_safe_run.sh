#!/bin/bash
# 
# Flask Safe Run - ポート競合を自動回避してFlaskを起動
#
# 使用法: ./flask_safe_run.sh [port]
# ポート指定なしの場合は5000番ポートを使用
#

set -e  # エラー時に終了

PORT=${1:-5000}
VENV_PATH="venv/bin/activate"

echo "🚀 Flask Safe Run - ポート競合自動回避システム"
echo "================================================"
echo "対象ポート: ${PORT}"

# 仮想環境の確認
if [[ ! -f "$VENV_PATH" ]]; then
    echo "❌ 仮想環境が見つかりません: $VENV_PATH"
    exit 1
fi

# 既存のFlaskプロセスを確認・停止
echo "📋 既存のFlaskプロセスを確認中..."

# ポートを使用中のプロセスを確認
PORT_PID=$(lsof -ti:${PORT} 2>/dev/null || echo "")

if [[ -n "$PORT_PID" ]]; then
    echo "⚠️  ポート${PORT}が使用中です (PID: ${PORT_PID})"
    
    # Flaskプロセスかどうか確認
    if ps -p ${PORT_PID} -o cmd= | grep -q "flask\|python.*app.py"; then
        echo "🔄 既存のFlaskプロセスを停止中..."
        kill ${PORT_PID} 2>/dev/null || true
        
        # プロセスが完全に終了するまで待機
        for i in {1..10}; do
            if ! kill -0 ${PORT_PID} 2>/dev/null; then
                break
            fi
            echo "   待機中... (${i}/10)"
            sleep 1
        done
        
        # 強制終了が必要な場合
        if kill -0 ${PORT_PID} 2>/dev/null; then
            echo "🔨 強制終了中..."
            kill -9 ${PORT_PID} 2>/dev/null || true
            sleep 2
        fi
        
        echo "✅ 既存プロセスを停止しました"
    else
        echo "❌ ポート${PORT}が他のプロセスに使用されています"
        echo "プロセス詳細:"
        ps -p ${PORT_PID} -o pid,ppid,cmd= || true
        exit 1
    fi
else
    echo "✅ ポート${PORT}は使用可能です"
fi

# 残存するflask runプロセスをクリーンアップ
echo "🧹 残存プロセスのクリーンアップ中..."
pkill -f "flask run" 2>/dev/null && echo "   flask runプロセスを停止" || true
pkill -f "python.*app.py" 2>/dev/null && echo "   Python app.pyプロセスを停止" || true

# 最終確認
sleep 2
FINAL_CHECK=$(lsof -ti:${PORT} 2>/dev/null || echo "")
if [[ -n "$FINAL_CHECK" ]]; then
    echo "❌ ポート${PORT}がまだ使用中です"
    lsof -i:${PORT}
    exit 1
fi

echo "✅ ポート競合回避完了"
echo ""

# Flask起動
echo "🎯 Flaskアプリケーション起動中..."
echo "アクセス先: http://127.0.0.1:${PORT}"
echo "停止方法: Ctrl+C"
echo ""

# 仮想環境をアクティベートしてFlask起動
source "$VENV_PATH"

if [[ "$PORT" == "5000" ]]; then
    # デフォルトポート5000の場合
    flask run
else
    # 指定ポートの場合
    flask run --port=${PORT}
fi
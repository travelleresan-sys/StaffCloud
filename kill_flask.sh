#!/bin/bash
# Flask プロセス強制終了スクリプト - 再発防止用

echo "=== Flask Process Killer ==="
echo "Checking for Flask processes using port 5000..."

# ポート5000を使用中のプロセスを特定
FLASK_PIDS=$(lsof -t -i:5000 2>/dev/null)

if [ -z "$FLASK_PIDS" ]; then
    echo "✅ Port 5000 is free. No Flask processes found."
else
    echo "🔍 Found Flask processes using port 5000:"
    lsof -i:5000 2>/dev/null
    
    echo ""
    echo "🛑 Stopping Flask processes..."
    
    # プロセスを段階的に停止
    for pid in $FLASK_PIDS; do
        echo "Stopping PID: $pid"
        kill -TERM $pid 2>/dev/null
        sleep 1
        
        # まだ存在する場合は強制終了
        if kill -0 $pid 2>/dev/null; then
            echo "Force killing PID: $pid"
            kill -9 $pid 2>/dev/null
        fi
    done
    
    # 追加でflaskコマンド関連プロセスも確認
    echo "🧹 Cleaning up any remaining flask processes..."
    pkill -f "flask run" 2>/dev/null || true
    pkill -f "python.*flask" 2>/dev/null || true
    
    sleep 2
    
    # 最終確認
    REMAINING=$(lsof -t -i:5000 2>/dev/null)
    if [ -z "$REMAINING" ]; then
        echo "✅ All Flask processes stopped successfully."
        echo "✅ Port 5000 is now free."
    else
        echo "⚠️  Some processes may still be running:"
        lsof -i:5000 2>/dev/null
    fi
fi

echo ""
echo "=== Summary ==="
echo "You can now run 'flask run' safely."
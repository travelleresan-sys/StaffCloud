#!/bin/bash
# 
# Flask Ultra Safe Run - 最強のポート競合回避システム
#
# 使用法: ./flask_ultra_safe_run.sh [port]
# ポート指定なしの場合は5000番ポートを使用
#

set -e  # エラー時に終了

PORT=${1:-5000}
BACKUP_PORTS=(5001 5002 5003 5004 5005)
VENV_PATH="venv/bin/activate"
MAX_RETRY=3

echo "🚀 Flask Ultra Safe Run - 最強ポート競合回避システム"
echo "======================================================"
echo "対象ポート: ${PORT}"

# 仮想環境の確認
if [[ ! -f "$VENV_PATH" ]]; then
    echo "❌ 仮想環境が見つかりません: $VENV_PATH"
    exit 1
fi

# 関数: ポートが使用可能かチェック
check_port_available() {
    local port=$1
    local pid=$(lsof -ti:${port} 2>/dev/null || echo "")
    [[ -z "$pid" ]]
}

# 関数: Flaskプロセスを完全停止
kill_flask_processes() {
    local port=$1
    echo "🧹 ポート${port}のプロセス完全停止..."
    
    # ポート使用プロセス停止
    local port_pid=$(lsof -ti:${port} 2>/dev/null || echo "")
    if [[ -n "$port_pid" ]]; then
        echo "   ポート${port}使用プロセス(PID: ${port_pid})を停止"
        kill ${port_pid} 2>/dev/null || true
        
        # 終了待機
        for i in {1..10}; do
            if ! kill -0 ${port_pid} 2>/dev/null; then
                break
            fi
            sleep 1
        done
        
        # 強制終了
        if kill -0 ${port_pid} 2>/dev/null; then
            echo "   強制終了実行"
            kill -9 ${port_pid} 2>/dev/null || true
            sleep 2
        fi
    fi
    
    # 全てのFlask関連プロセス停止
    echo "   全Flask関連プロセス停止中..."
    pkill -f "flask run" 2>/dev/null || true
    pkill -f "python.*app.py" 2>/dev/null || true
    pkill -f "Flask" 2>/dev/null || true
    
    # Pythonプロセスからapp.pyを実行中のものを停止
    for pid in $(ps aux | grep "python.*app\.py" | grep -v grep | awk '{print $2}'); do
        echo "   Python app.pyプロセス(PID: ${pid})を停止"
        kill ${pid} 2>/dev/null || true
    done
    
    sleep 3  # 確実な停止を待つ
}

# 関数: 利用可能なポートを見つける
find_available_port() {
    local target_port=$1
    
    # まず指定ポートを試行
    if check_port_available ${target_port}; then
        echo ${target_port}
        return 0
    fi
    
    # 指定ポートが使用中の場合、バックアップポートを試行
    echo "⚠️  ポート${target_port}が使用中のため、代替ポートを検索中..."
    for backup_port in "${BACKUP_PORTS[@]}"; do
        if check_port_available ${backup_port}; then
            echo "🔄 代替ポート${backup_port}を使用します"
            echo ${backup_port}
            return 0
        fi
    done
    
    echo "❌ 利用可能なポートが見つかりません"
    return 1
}

# メイン処理
echo "📋 既存プロセス確認・停止..."

# 徹底的にFlaskプロセスを停止
kill_flask_processes ${PORT}

# 利用可能なポートを確保
ACTUAL_PORT=$(find_available_port ${PORT})
if [[ $? -ne 0 ]]; then
    echo "❌ ポート確保に失敗しました"
    exit 1
fi

# 最終確認
echo "🔍 最終ポート確認..."
if ! check_port_available ${ACTUAL_PORT}; then
    echo "❌ ポート${ACTUAL_PORT}の確保に失敗"
    lsof -i:${ACTUAL_PORT} 2>/dev/null || true
    exit 1
fi

echo "✅ ポート${ACTUAL_PORT}を確保しました"
echo ""

# Flask起動
echo "🎯 Flaskアプリケーション起動..."
echo "アクセス先: http://127.0.0.1:${ACTUAL_PORT}"
echo "停止方法: Ctrl+C"
echo ""

# 環境変数設定
export FLASK_APP=app.py
export FLASK_ENV=development

# 仮想環境をアクティベート
source "$VENV_PATH"

# リトライロジック付きでFlask起動
for attempt in $(seq 1 ${MAX_RETRY}); do
    echo "起動試行 ${attempt}/${MAX_RETRY}..."
    
    if [[ "$ACTUAL_PORT" == "5000" ]]; then
        # デフォルトポート5000の場合
        flask run --debug 2>&1 || {
            echo "⚠️  起動失敗 (試行${attempt})"
            if [[ ${attempt} -lt ${MAX_RETRY} ]]; then
                echo "2秒後に再試行..."
                sleep 2
                kill_flask_processes ${ACTUAL_PORT}
                continue
            else
                echo "❌ Flask起動に失敗しました"
                exit 1
            fi
        }
    else
        # 指定ポートの場合
        flask run --port=${ACTUAL_PORT} --debug 2>&1 || {
            echo "⚠️  起動失敗 (試行${attempt})"
            if [[ ${attempt} -lt ${MAX_RETRY} ]]; then
                echo "2秒後に再試行..."
                sleep 2
                kill_flask_processes ${ACTUAL_PORT}
                continue
            else
                echo "❌ Flask起動に失敗しました"
                exit 1
            fi
        }
    fi
    
    break  # 成功した場合はループを抜ける
done
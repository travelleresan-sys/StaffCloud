#!/bin/bash
#
# 簡単Flask起動スクリプト
# 使用法: ./start_flask.sh
#

echo "🚀 Employee DB Flask Application"
echo "================================="

# プロジェクトディレクトリに移動
cd "$(dirname "$0")"

# Ultra Safe Runを実行
./flask_ultra_safe_run.sh

echo ""
echo "✅ Flaskアプリケーションが終了しました"
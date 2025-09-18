#!/bin/bash

# ポート管理ユーティリティ

case "$1" in
    "check")
        PORT=${2:-5000}
        if lsof -i :$PORT >/dev/null 2>&1; then
            echo "Port $PORT is in use by:"
            lsof -i :$PORT
            exit 1
        else
            echo "Port $PORT is available"
            exit 0
        fi
        ;;
    "kill")
        PORT=${2:-5000}
        echo "Killing processes using port $PORT..."
        lsof -ti :$PORT | xargs kill -9 2>/dev/null
        sleep 2
        if lsof -i :$PORT >/dev/null 2>&1; then
            echo "Failed to free port $PORT"
            exit 1
        else
            echo "Port $PORT is now free"
            exit 0
        fi
        ;;
    "kill-flask")
        echo "Killing all Flask processes..."
        pkill -f "flask run"
        sleep 2
        pkill -9 -f "flask run" 2>/dev/null
        echo "All Flask processes terminated"
        ;;
    "find")
        START_PORT=${2:-5000}
        PORT=$START_PORT
        while lsof -i :$PORT >/dev/null 2>&1; do
            PORT=$((PORT + 1))
        done
        echo $PORT
        ;;
    *)
        echo "Usage: $0 {check|kill|kill-flask|find} [port]"
        echo ""
        echo "Commands:"
        echo "  check [port]    - Check if port is available (default: 5000)"
        echo "  kill [port]     - Kill processes using port (default: 5000)"
        echo "  kill-flask      - Kill all Flask processes"
        echo "  find [port]     - Find first available port starting from port (default: 5000)"
        echo ""
        echo "Examples:"
        echo "  $0 check 5000"
        echo "  $0 kill 5000"
        echo "  $0 kill-flask"
        echo "  $0 find 5000"
        exit 1
        ;;
esac
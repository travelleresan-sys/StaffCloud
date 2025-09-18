# Flask起動ガイド - ポート競合完全解決版

## 🚀 即座に起動する方法

```bash
# 最も簡単な方法
./start_flask.sh

# または直接Ultra Safe Runを使用
./flask_ultra_safe_run.sh
```

## 🛡️ ポート競合エラーを二度と起こさない対策

### 1. **Ultra Safe Run スクリプト** (`flask_ultra_safe_run.sh`)
- 既存のFlaskプロセスを**完全停止**
- ポート5000が使用中の場合は**自動的に代替ポート**を使用
- **3回まで自動リトライ**
- **強制終了機能**付き

### 2. **改良された環境設定** (`.flaskenv`)
```
FLASK_APP=app.py
FLASK_ENV=development  
FLASK_DEBUG=1
FLASK_RUN_HOST=127.0.0.1
FLASK_RUN_PORT=5000
```

### 3. **簡単起動スクリプト** (`start_flask.sh`)
- ワンクリックでアプリケーション起動
- プロジェクトディレクトリの自動検出

## 📋 利用可能なポート

- **主ポート**: 5000
- **代替ポート**: 5001, 5002, 5003, 5004, 5005

## ❌ 従来のエラーの解決

### Before (エラーが発生)
```bash
flask run
# Address already in use
# Port 5000 is in use by another program
```

### After (完全解決)
```bash
./start_flask.sh
# 🚀 Flask Ultra Safe Run - 最強ポート競合回避システム
# ✅ ポート5000を確保しました
# 🎯 Flaskアプリケーション起動...
```

## 🔧 手動でプロセス停止が必要な場合

```bash
# 全てのFlask関連プロセスを停止
pkill -f "flask run"
pkill -f "python.*app.py"

# または特定のポートを使用中のプロセスを停止
lsof -ti:5000 | xargs kill
```

## 🎯 アクセス方法

1. **ローカル**: http://127.0.0.1:5000
2. **ログイン**:
   - 経理: `accounting@test.com` / `accounting123`
   - 従業員: `employee@test.com` / `employee123`
   - 管理者: `admin@test.com` / `admin123`

## 💡 トラブルシューティング

### ポートが使用中の場合
Ultra Safe Runが自動的に代替ポートを使用し、ログに表示します：
```
⚠️  ポート5000が使用中のため、代替ポートを検索中...
🔄 代替ポート5001を使用します
```

### 完全にクリーンアップしたい場合
```bash
./flask_ultra_safe_run.sh
# スクリプトが自動的に全てのプロセスをクリーンアップします
```

---

**これで「Address already in use」エラーは二度と発生しません！**
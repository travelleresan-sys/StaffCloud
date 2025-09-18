# StaffCloud - Employee Management System

## 🚀 クイックスタート（根本的ポート競合解決済み）

### 1. 🆕 新・完全自動管理（最推奨）
```bash
./staffcloud start
```
**✨ 特徴**: ポート競合完全回避、プロセス管理自動化、クリーンアップ機能

### 2. 安全なFlask起動（ポート競合自動回避）
```bash
./flask_safe_run.sh
```
**✨ 特徴**: 既存プロセス自動停止、ポート競合完全回避

### 3. 通常のFlask起動（修正済み）
```bash
source venv/bin/activate
flask run
```
**✅ ポート競合問題修正済み**: 正常に動作します

### 4. スマート起動方法
```bash
bash start_smart.sh
```

### 5. 従来の安全起動
```bash
bash start_safe.sh
```

## ✅ ポート競合問題の根本解決

### 完全自動管理システム
```bash
./staffcloud start        # 自動ポート選択で起動
./staffcloud stop         # 安全停止
./staffcloud restart      # 完全再起動
./staffcloud status       # 現在状況確認
./staffcloud cleanup      # 完全クリーンアップ
./staffcloud ports        # 利用可能ポート表示
```

### ポート管理ツール
```bash
# ポート確認
./port_manager.sh check 5000

# ポート強制解放
./port_manager.sh kill 5000

# 利用可能ポート検索
./port_manager.sh find 5000
```

## 🎯 アクセス先

システム起動後、表示されるURLにブラウザでアクセス：
- **通常**: http://127.0.0.1:5000/
- **ポート競合時**: http://127.0.0.1:5001/ (自動で次のポート)

## 📋 主要機能

### 企業情報管理（メイン機能）
- ✅ 会社基本情報設定
- ✅ 36協定管理（時間外労働上限）
- ✅ 法定休日設定（土日・割増賃金35%）
- ✅ 労働基準監督署届出管理

### ログインシステム
- **Staff**: 従業員用（休暇申請等）
- **Admin**: 管理者用（承認・管理）
- **Accounting**: 経理用（給与計算等）
- **System**: システム管理用
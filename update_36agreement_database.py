#!/usr/bin/env python3
"""
36協定管理機能のデータベーススキーマ更新スクリプト
新しいAgreement36テーブルとCompanySettingsの拡張フィールドを追加します。
"""

from flask import Flask
from models import db, Agreement36, CompanySettings
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# データベース初期化
db.init_app(app)

def update_database():
    """データベーススキーマを更新"""
    with app.app_context():
        try:
            print("36協定管理機能のデータベーススキーマを更新中...")
            
            # 新しいテーブルを作成
            db.create_all()
            
            print("✅ データベーススキーマの更新が完了しました。")
            print("📋 追加された機能:")
            print("  - Agreement36テーブル（詳細な36協定管理）")
            print("  - CompanySettingsテーブルの拡張（郵便番号、代表者役職、事業内容詳細）")
            print("  - 労働者代表・使用者の従業員情報との連携")
            print("  - 時間外労働・休日労働の詳細設定")
            
        except Exception as e:
            print(f"❌ データベース更新中にエラーが発生しました: {e}")
            return False
    
    return True

if __name__ == '__main__':
    success = update_database()
    if success:
        print("\n🎉 36協定管理機能の導入が完了しました！")
        print("💡 使用方法:")
        print("  1. 管理者または総務事務担当者でログイン")
        print("  2. /create_36agreement にアクセスして新規36協定を作成")
        print("  3. /list_36agreements で36協定一覧を確認")
        print("  4. /general_affairs_36agreement で既存の36協定管理も利用可能")
    else:
        print("\n💔 データベース更新に失敗しました。")
        exit(1)
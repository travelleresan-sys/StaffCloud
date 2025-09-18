#!/usr/bin/env python3
"""
ユーザーロールを新しい分類に更新するスクリプト
総務事務(general_affairs)と人事事務(hr_affairs)ロールを作成
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash

def update_roles():
    with app.app_context():
        print("🔧 ユーザーロールの更新を開始...")
        
        # 新しいロールのユーザーを作成
        users_to_create = [
            {
                'email': 'general_affairs@example.com',
                'password': 'generalaffairs123',
                'role': 'general_affairs'
            },
            {
                'email': 'hr_affairs@example.com', 
                'password': 'hraffairs123',
                'role': 'hr_affairs'
            }
        ]
        
        for user_data in users_to_create:
            # 既存ユーザーをチェック
            existing_user = User.query.filter_by(email=user_data['email']).first()
            
            if existing_user:
                # 既存ユーザーのロールを更新
                existing_user.role = user_data['role']
                print(f"✅ 既存ユーザー {user_data['email']} のロールを {user_data['role']} に更新")
            else:
                # 新しいユーザーを作成
                new_user = User(
                    email=user_data['email'],
                    password=generate_password_hash(user_data['password']),
                    role=user_data['role']
                )
                db.session.add(new_user)
                print(f"✅ 新しいユーザー {user_data['email']} を作成 (ロール: {user_data['role']})")
        
        # データベースに保存
        try:
            db.session.commit()
            print("💾 データベースの更新が完了しました")
        except Exception as e:
            db.session.rollback()
            print(f"❌ エラー: {e}")
            return False
        
        # 結果を表示
        print("\n📋 現在のユーザー一覧:")
        users = User.query.all()
        for user in users:
            print(f"   - {user.email}: {user.role}")
        
        print("\n🎯 ログイン情報:")
        print("   - 総務事務: general_affairs@example.com / generalaffairs123")
        print("   - 人事事務: hr_affairs@example.com / hraffairs123")
        print("   - 経理事務: accounting@example.com / accounting123")
        print("   - システム管理: system@example.com / systemadmin123")
        
        return True

if __name__ == '__main__':
    if update_roles():
        print("✨ ロール更新が正常に完了しました！")
    else:
        print("❌ ロール更新に失敗しました")
        sys.exit(1)
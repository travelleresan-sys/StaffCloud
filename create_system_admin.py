#!/usr/bin/env python3
"""
システム管理者アカウント作成スクリプト
"""
from app import app, db, User
from werkzeug.security import generate_password_hash

def create_system_admin():
    with app.app_context():
        # 既存のシステム管理者をチェック
        existing_admin = User.query.filter_by(role='system_admin').first()
        if existing_admin:
            print(f"システム管理者は既に存在します: {existing_admin.email}")
            return
        
        # システム管理者アカウントを作成
        system_admin = User(
            email='system@staffcloud.local',
            password=generate_password_hash('SystemAdmin2025!'),
            role='system_admin'
        )
        
        db.session.add(system_admin)
        db.session.commit()
        
        print("✅ システム管理者アカウントが作成されました:")
        print(f"   Email: system@staffcloud.local")
        print(f"   Password: SystemAdmin2025!")
        print(f"   ログインURL: http://localhost:5001/system_admin_login")

if __name__ == '__main__':
    create_system_admin()
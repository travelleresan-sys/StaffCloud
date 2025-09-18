#!/usr/bin/env python3
"""
経理ユーザーを作成
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_accounting_user():
    """経理ユーザーを作成"""
    with app.app_context():
        # 既存の経理ユーザーを確認
        accounting = User.query.filter_by(email='accounting@test.com').first()
        if accounting:
            print("経理ユーザーが既に存在します")
            return
        
        # 経理ユーザーを作成
        accounting = User(
            email='accounting@test.com',
            password=generate_password_hash('accounting123'),
            role='accounting'
        )
        db.session.add(accounting)
        db.session.commit()
        
        print("経理ユーザーを作成しました")
        print("メール: accounting@test.com")
        print("パスワード: accounting123")
        print("ロール: accounting")

if __name__ == "__main__":
    create_accounting_user()
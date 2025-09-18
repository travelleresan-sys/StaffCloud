#!/usr/bin/env python3
"""
Flask-Loginの動作をテストするスクリプト
"""

from app import app
from models import User, db
from werkzeug.security import generate_password_hash

def test_flask_login():
    with app.app_context():
        try:
            print("=== Flask-Login 動作テスト ===")
            
            # テストユーザーを作成
            test_user = User.query.filter_by(email='test@example.com').first()
            if not test_user:
                test_user = User(
                    email='test@example.com',
                    password=generate_password_hash('testpassword'),
                    role='admin'
                )
                db.session.add(test_user)
                db.session.commit()
                print("テストユーザーを作成しました")
            
            with app.test_client() as client:
                # ログインページにアクセス
                response = client.get('/login')
                print(f"ログインページアクセス: {response.status_code}")
                
                # ログイン試行
                login_data = {
                    'email': 'test@example.com',
                    'password': 'testpassword'
                }
                response = client.post('/login', data=login_data, follow_redirects=False)
                print(f"ログイン試行: {response.status_code}")
                
                if response.status_code == 302:
                    print("ログイン成功（リダイレクト）")
                    
                    # ダッシュボードにアクセス（ログイン必須）
                    response = client.get('/dashboard', follow_redirects=False)
                    print(f"ダッシュボードアクセス: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("✓ Flask-Loginは正常に動作しています")
                    else:
                        print("✗ ダッシュボードアクセスに失敗")
                else:
                    print("✗ ログインに失敗")
                    print(f"レスポンス内容: {response.data.decode()[:200]}...")
                    
        except Exception as e:
            print(f"エラー: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_flask_login()
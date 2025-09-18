#!/usr/bin/env python3
"""
Web経由で自動付与機能をテストするスクリプト
"""

from app import app
from models import User, db
from werkzeug.security import generate_password_hash

def test_web_auto_grant():
    with app.app_context():
        try:
            # Adminユーザーを作成
            admin_user = User.query.filter_by(email='admin@test.com').first()
            if not admin_user:
                admin_user = User(
                    email='admin@test.com',
                    password=generate_password_hash('password'),
                    role='admin'
                )
                db.session.add(admin_user)
                db.session.commit()
            
            with app.test_client() as client:
                # ログイン
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(admin_user.id)
                    sess['_fresh'] = True
                
                print("自動付与機能をWebインターフェース経由でテスト...")
                
                # 自動付与を実行
                response = client.post('/auto_grant_annual_leave')
                print(f"HTTPステータス: {response.status_code}")
                
                if response.status_code == 302:  # リダイレクト
                    print("自動付与処理が完了しました（リダイレクト）")
                    
                    # リダイレクト先を確認
                    location = response.headers.get('Location', '')
                    if 'leave_management' in location:
                        print("年休管理画面にリダイレクトされました")
                else:
                    print(f"想定外のレスポンス: {response.data.decode()}")
                    
        except Exception as e:
            print(f"エラー: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_web_auto_grant()
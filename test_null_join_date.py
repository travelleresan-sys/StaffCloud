#!/usr/bin/env python3
"""
入社日がNullの従業員で年休管理画面をテストするスクリプト
"""

from app import app, db
from models import Employee
from datetime import date

def test_null_join_date():
    with app.app_context():
        try:
            # 入社日がNullの従業員を作成
            test_employee = Employee.query.filter_by(name='入社日Null従業員').first()
            if not test_employee:
                test_employee = Employee(
                    name='入社日Null従業員',
                    join_date=None,  # 意図的にNullにする
                    status='在籍中'
                )
                db.session.add(test_employee)
                db.session.commit()
                print(f"入社日Null従業員を作成しました: ID={test_employee.id}")
            
            # leave_management関数のロジックをテスト
            from app import leave_management
            
            # 実際にビューをテストする
            with app.test_client() as client:
                # ダミーのログインを行う（adminユーザーを作成）
                from models import User
                from werkzeug.security import generate_password_hash
                
                admin_user = User.query.filter_by(email='admin@test.com').first()
                if not admin_user:
                    admin_user = User(
                        email='admin@test.com',
                        password=generate_password_hash('password'),
                        role='admin'
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                
                # ログイン
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(admin_user.id)
                    sess['_fresh'] = True
                
                # 年休管理画面にアクセス
                response = client.get('/leave_management')
                print(f"HTTPステータス: {response.status_code}")
                
                if response.status_code == 200:
                    print("年休管理画面は正常にロードされました")
                else:
                    print(f"エラーが発生しました: {response.data.decode()}")
                    
        except Exception as e:
            print(f"エラー: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_null_join_date()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, create_working_conditions_change
from models import CompanySettings, Employee, User
from flask import request
import io
import sys

def test_web_working_conditions_change():
    """Web経由での労働条件変更通知書作成テスト"""
    with app.app_context():
        with app.test_client() as client:
            try:
                print("🔧 Web経由労働条件変更通知書作成テスト開始")
                
                # 会社設定の確認/作成
                company = CompanySettings.query.first()
                if not company:
                    print("📝 会社設定を作成します...")
                    from datetime import datetime
                    company = CompanySettings(
                        company_name="テスト株式会社",
                        representative_name="山田 太郎",
                        company_address="東京都渋谷区テスト町1-2-3",
                        company_phone="03-1234-5678",
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    db.session.add(company)
                    db.session.commit()
                    print("✅ 会社設定を作成しました")
                
                # テストユーザーの確認/作成
                test_user = User.query.filter_by(email='admin@test.com').first()
                if not test_user:
                    print("📝 テストユーザーを作成します...")
                    from werkzeug.security import generate_password_hash
                    test_user = User(
                        email='admin@test.com',
                        password=generate_password_hash('password'),
                        role='admin'
                    )
                    db.session.add(test_user)
                    db.session.commit()
                    print("✅ テストユーザーを作成しました")
                
                # フォームデータのシミュレート
                form_data = {
                    'employee_name': '佐藤 花子',
                    'change_date': '2024-04-01',
                    'change_reason': '昇進・昇格による労働条件の変更',
                    'old_position': '営業職',
                    'new_position': '営業主任',
                    'old_department': '営業部', 
                    'new_department': '営業1部',
                    'old_salary': '250000',
                    'new_salary': '300000'
                }
                
                # ログイン状態をシミュレート
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(test_user.id)
                    sess['_fresh'] = True
                
                print("📄 Web経由でPDF作成をテスト中...")
                
                # create_working_conditions_change関数を直接テスト
                with app.test_request_context('/create_working_conditions_change', 
                                            method='POST', 
                                            data=form_data):
                    # current_userを設定
                    from flask_login import login_user
                    login_user(test_user)
                    
                    # PDF生成処理を実行
                    response = create_working_conditions_change()
                    
                    if response.status_code == 200:
                        print("✅ PDF生成成功")
                        print(f"📊 Content-Type: {response.headers.get('Content-Type')}")
                        print(f"📊 Content-Length: {len(response.data)} bytes")
                        
                        # PDFファイルとして保存
                        with open('test_web_working_conditions_change.pdf', 'wb') as f:
                            f.write(response.data)
                        print("✅ PDFファイル保存完了: test_web_working_conditions_change.pdf")
                        
                        return True
                    else:
                        print(f"❌ PDF生成失敗: Status {response.status_code}")
                        print(f"Response: {response.data.decode('utf-8') if response.data else 'No data'}")
                        return False
                        
            except Exception as e:
                print(f"❌ エラー発生: {str(e)}")
                import traceback
                traceback.print_exc()
                return False

if __name__ == '__main__':
    success = test_web_working_conditions_change()
    exit(0 if success else 1)
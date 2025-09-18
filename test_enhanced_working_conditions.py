#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, create_working_conditions_change
from models import CompanySettings, Employee, User
from flask import request
import io
import sys

def test_enhanced_working_conditions_change():
    """拡張版労働条件変更通知書作成テスト"""
    with app.app_context():
        with app.test_client() as client:
            try:
                print("🔧 拡張版労働条件変更通知書作成テスト開始")
                
                # 会社設定とテストユーザーの確認/作成
                company = CompanySettings.query.first()
                if not company:
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
                
                test_user = User.query.filter_by(email='admin@test.com').first()
                if not test_user:
                    from werkzeug.security import generate_password_hash
                    test_user = User(
                        email='admin@test.com',
                        password=generate_password_hash('password'),
                        role='admin'
                    )
                    db.session.add(test_user)
                    db.session.commit()
                
                # 拡張フォームデータ（変更あり・変更なしの混合パターン）
                form_data = {
                    'employee_name': '佐藤 花子',
                    'change_date': '2024-04-01',
                    'change_reason': '昇進・昇格及び組織改編による労働条件の変更',
                    
                    # 変更ありの項目
                    'change_type_position': 'change',
                    'old_position': '営業職',
                    'new_position': '営業主任',
                    
                    'change_type_department': 'change',
                    'old_department': '営業部',
                    'new_department': '営業1部',
                    
                    'change_type_base_salary': 'change',
                    'old_base_salary': '250000',
                    'new_base_salary': '300000',
                    
                    # 変更なしの項目
                    'change_type_contract_period': 'no_change',
                    'current_contract_period': '期間の定めなし',
                    
                    'change_type_work_hours': 'no_change',
                    'current_work_hours': '09:00-18:00（休憩60分）',
                    
                    'change_type_workplace': 'no_change',
                    'current_workplace': '東京都渋谷区テスト町1-2-3',
                    
                    'change_type_overtime': 'no_change',
                    'current_overtime': 'あり（36協定の範囲内）',
                    
                    'change_type_social_insurance': 'no_change',
                    'current_social_insurance': '健康保険、厚生年金保険、雇用保険、労災保険'
                }
                
                # ログイン状態をシミュレート
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(test_user.id)
                    sess['_fresh'] = True
                
                print("📄 拡張版PDF作成をテスト中...")
                
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
                        print("✅ 拡張版PDF生成成功")
                        print(f"📊 Content-Type: {response.headers.get('Content-Type')}")
                        print(f"📊 Content-Length: {len(response.data)} bytes")
                        
                        # PDFファイルとして保存
                        with open('test_enhanced_working_conditions_change.pdf', 'wb') as f:
                            f.write(response.data)
                        print("✅ PDFファイル保存完了: test_enhanced_working_conditions_change.pdf")
                        
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
    success = test_enhanced_working_conditions_change()
    exit(0 if success else 1)
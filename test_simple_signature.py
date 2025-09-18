#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, create_working_conditions_change
from models import CompanySettings, Employee, User
from flask import request
import io
import sys

def test_simple_signature_working_conditions():
    """シンプル署名欄調整版労働条件変更通知書作成テスト"""
    with app.app_context():
        with app.test_client() as client:
            try:
                print("🔧 シンプル署名欄調整版労働条件変更通知書作成テスト開始")
                
                # 会社設定とテストユーザーの確認/作成
                company = CompanySettings.query.first()
                if not company:
                    from datetime import datetime
                    company = CompanySettings(
                        company_name="株式会社テストコーポレーション",
                        representative_name="代表取締役 山田 太郎",
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
                
                # 最小限必要なフィールドを含む完全なフォームデータ
                form_data = {
                    'employee_name': '鈴木 花子',
                    'change_date': '2024-08-15',
                    'change_reason': '署名欄レイアウト調整のテスト',
                    
                    # すべてのフィールドを変更なしで設定（必要最小限）
                    'change_type_contract_period': 'no_change',
                    'current_contract_period_type': '期間の定めなし',
                    
                    'change_type_contract_renewal': 'no_change',
                    'current_contract_renewal': '該当なし',
                    
                    'change_type_workplace': 'no_change',
                    'current_workplace': '東京都渋谷区テスト町1-2-3',
                    
                    'change_type_job_duties': 'no_change',
                    'current_job_duties': '一般事務',
                    
                    'change_type_work_hours': 'no_change',
                    'current_work_hours': '09:00-18:00',
                    
                    'change_type_break_time': 'no_change',
                    'current_break_time': '12:00-13:00（60分）',
                    
                    'change_type_overtime': 'no_change',
                    'current_overtime': '有（36協定の範囲内）',
                    
                    'change_type_holidays': 'no_change',
                    'current_holidays': '土日祝日',
                    
                    'change_type_vacation': 'no_change',
                    'current_vacation': '年次有給休暇',
                    
                    'change_type_base_salary': 'change',
                    'old_base_salary': '250000',
                    'new_base_salary': '300000',
                    
                    'change_type_allowances': 'no_change',
                    'current_allowances': '通勤手当',
                    
                    'change_type_payment_terms': 'no_change',
                    'current_payment_terms': '月末締翌月25日払',
                    
                    'change_type_payment_method': 'no_change',
                    'current_payment_method': '銀行振込',
                    
                    'change_type_retirement': 'no_change',
                    'current_retirement': '定年60歳',
                    
                    'change_type_dismissal': 'no_change',
                    'current_dismissal': '就業規則に準ずる',
                    
                    'change_type_social_insurance': 'no_change',
                    'current_social_insurance': '厚生年金、健康保険等',
                    
                    'change_type_employment_insurance': 'no_change',
                    'current_employment_insurance': '適用あり'
                }
                
                # ログイン状態をシミュレート
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(test_user.id)
                    sess['_fresh'] = True
                
                print("📄 シンプル署名欄調整版PDF作成をテスト中...")
                
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
                        print("✅ シンプル署名欄調整版PDF生成成功")
                        print(f"📊 Content-Type: {response.headers.get('Content-Type')}")
                        print(f"📊 Content-Length: {len(response.data)} bytes")
                        
                        # PDFファイルとして保存
                        with open('test_simple_signature_working_conditions.pdf', 'wb') as f:
                            f.write(response.data)
                        print("✅ PDFファイル保存完了: test_simple_signature_working_conditions.pdf")
                        
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
    success = test_simple_signature_working_conditions()
    exit(0 if success else 1)
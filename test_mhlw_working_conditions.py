#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, create_working_conditions_change
from models import CompanySettings, Employee, User
from flask import request
import io
import sys

def test_mhlw_working_conditions_change():
    """MHLW完全準拠労働条件変更通知書作成テスト"""
    with app.app_context():
        with app.test_client() as client:
            try:
                print("🔧 MHLW完全準拠労働条件変更通知書作成テスト開始")
                
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
                
                # MHLW完全準拠フォームデータ
                form_data = {
                    'employee_name': '佐藤 花子',
                    'change_date': '2024-04-01',
                    'change_reason': '昇進に伴う労働条件の変更（契約期間の変更および勤務地の変更）',
                    
                    # 1. 労働契約の期間（期間の定めありから期間の定めなしへ変更）
                    'change_type_contract_period': 'change',
                    'old_contract_period_type': '期間の定めあり',
                    'old_contract_start_date': '2023-04-01',
                    'old_contract_end_date': '2024-03-31',
                    'new_contract_period_type': '期間の定めなし',
                    
                    # 1-1. 契約の更新の有無（変更なし）
                    'change_type_contract_renewal': 'no_change',
                    'current_contract_renewal': '自動的に更新する',
                    
                    # 2. 就業の場所（変更あり）
                    'change_type_workplace': 'change',
                    'old_workplace': '東京都渋谷区テスト町1-2-3\n（本社ビル3階）',
                    'new_workplace': '大阪府大阪市北区テスト町2-3-4\n（関西支社ビル5階）',
                    
                    # その他の項目（変更なし）
                    'change_type_position': 'no_change',
                    'current_position': '営業職',
                    
                    'change_type_department': 'no_change',
                    'current_department': '営業部',
                    
                    'change_type_base_salary': 'no_change',
                    'current_base_salary': '300000',
                    
                    'change_type_work_hours': 'no_change',
                    'current_work_hours': '9:00-18:00（休憩60分）',
                    
                    'change_type_social_insurance': 'no_change',
                    'current_social_insurance': '健康保険、厚生年金保険、雇用保険、労災保険'
                }
                
                # ログイン状態をシミュレート
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(test_user.id)
                    sess['_fresh'] = True
                
                print("📄 MHLW完全準拠PDF作成をテスト中...")
                
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
                        print("✅ MHLW完全準拠PDF生成成功")
                        print(f"📊 Content-Type: {response.headers.get('Content-Type')}")
                        print(f"📊 Content-Length: {len(response.data)} bytes")
                        
                        # PDFファイルとして保存
                        with open('test_mhlw_working_conditions_change.pdf', 'wb') as f:
                            f.write(response.data)
                        print("✅ PDFファイル保存完了: test_mhlw_working_conditions_change.pdf")
                        
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
    success = test_mhlw_working_conditions_change()
    exit(0 if success else 1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, create_working_conditions_change
from models import CompanySettings, Employee, User
from flask import request
import io
import sys

def test_enlarged_signature_working_conditions():
    """文字サイズ拡大・印位置調整版労働条件変更通知書作成テスト"""
    with app.app_context():
        with app.test_client() as client:
            try:
                print("🔧 文字サイズ拡大・印位置調整版労働条件変更通知書作成テスト開始")
                
                # 会社設定とテストユーザーの確認/作成
                company = CompanySettings.query.first()
                if not company:
                    from datetime import datetime
                    company = CompanySettings(
                        company_name="株式会社グローバルテクノロジー",
                        representative_name="代表取締役社長 佐藤 一郎",
                        company_address="東京都港区テクノロジータワー1-1-1",
                        company_phone="03-9999-8888",
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
                
                # 署名欄調整テスト用フォームデータ
                form_data = {
                    'employee_name': '渡辺 美佳',
                    'change_date': '2024-10-01',
                    'change_reason': '昇進及び職務変更による労働条件の改定',
                    
                    # 複数項目を変更して署名欄の重要性をテスト
                    'change_type_workplace': 'change',
                    'old_workplace': '東京都港区テクノロジータワー1-1-1（5階開発部）',
                    'new_workplace': '東京都港区テクノロジータワー1-1-1（12階管理部）',
                    
                    'change_type_job_duties': 'change',
                    'old_job_duties': 'システム開発エンジニア\\n・Webアプリケーション開発\\n・データベース設計',
                    'new_job_duties': '開発チームリーダー\\n・開発チームの統括管理\\n・プロジェクト進行管理\\n・技術指導及び人材育成',
                    
                    'change_type_base_salary': 'change',
                    'old_base_salary': '420000',
                    'new_base_salary': '500000',
                    
                    'change_type_allowances': 'change',
                    'old_allowances': '通勤手当、技術手当（月額15,000円）',
                    'new_allowances': '通勤手当、技術手当（月額20,000円）、管理職手当（月額40,000円）',
                    
                    # 変更なしの項目
                    'change_type_contract_period': 'no_change',
                    'current_contract_period_type': '期間の定めなし',
                    
                    'change_type_work_hours': 'no_change',
                    'current_work_hours': '10:00-19:00（フレックスタイム制）',
                    
                    'change_type_break_time': 'no_change',
                    'current_break_time': '12:00-13:00（60分）',
                    
                    'change_type_overtime': 'no_change',
                    'current_overtime': '有（36協定の範囲内）',
                    
                    'change_type_holidays': 'no_change',
                    'current_holidays': '完全週休2日制、国民の祝日、夏季・年末年始休暇',
                    
                    'change_type_vacation': 'no_change',
                    'current_vacation': '年次有給休暇（法定通り）、特別休暇制度',
                    
                    'change_type_payment_terms': 'no_change',
                    'current_payment_terms': '毎月末日締切、翌月25日支払',
                    
                    'change_type_payment_method': 'no_change',
                    'current_payment_method': '銀行振込',
                    
                    'change_type_retirement': 'no_change',
                    'current_retirement': '定年65歳、継続雇用制度あり',
                    
                    'change_type_dismissal': 'no_change',
                    'current_dismissal': '労働基準法及び就業規則に準ずる',
                    
                    'change_type_social_insurance': 'no_change',
                    'current_social_insurance': '健康保険、厚生年金保険、雇用保険、労災保険',
                    
                    'change_type_employment_insurance': 'no_change',
                    'current_employment_insurance': '適用あり'
                }
                
                # ログイン状態をシミュレート
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(test_user.id)
                    sess['_fresh'] = True
                
                print("📄 文字サイズ拡大・印位置調整版PDF作成をテスト中...")
                
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
                        print("✅ 文字サイズ拡大・印位置調整版PDF生成成功")
                        print(f"📊 Content-Type: {response.headers.get('Content-Type')}")
                        print(f"📊 Content-Length: {len(response.data)} bytes")
                        
                        # PDFファイルとして保存
                        with open('test_enlarged_signature_working_conditions.pdf', 'wb') as f:
                            f.write(response.data)
                        print("✅ PDFファイル保存完了: test_enlarged_signature_working_conditions.pdf")
                        
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
    success = test_enlarged_signature_working_conditions()
    exit(0 if success else 1)
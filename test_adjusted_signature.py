#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, create_working_conditions_change
from models import CompanySettings, Employee, User
from flask import request
import io
import sys

def test_adjusted_signature_working_conditions():
    """署名欄レイアウト調整版労働条件変更通知書作成テスト"""
    with app.app_context():
        with app.test_client() as client:
            try:
                print("🔧 署名欄レイアウト調整版労働条件変更通知書作成テスト開始")
                
                # 会社設定とテストユーザーの確認/作成
                company = CompanySettings.query.first()
                if not company:
                    from datetime import datetime
                    company = CompanySettings(
                        company_name="株式会社テストエンタープライズ",
                        representative_name="代表取締役社長 田中 健太郎",
                        company_address="東京都新宿区テストタワー1-1-1",
                        company_phone="03-9876-5432",
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
                    'employee_name': '佐々木 美智子',
                    'change_date': '2024-08-01',
                    'change_reason': '部門再編及び職責変更による労働条件の全面的見直し',
                    
                    # 複数項目で変更テスト
                    # 2. 就業の場所（変更あり）
                    'change_type_workplace': 'change',
                    'old_workplace': '東京都新宿区テストタワー1-1-1（10階マーケティング部）',
                    'new_workplace': '神奈川県横浜市みなとみらい新ビル3-4-5（7階戦略企画部）',
                    
                    # 3. 従事すべき業務（変更あり）
                    'change_type_job_duties': 'change',
                    'old_job_duties': 'マーケティング部スペシャリスト\\n・市場調査・分析\\n・広告企画・制作\\n・イベント企画・運営',
                    'new_job_duties': '戦略企画部マネージャー\\n・中長期戦略の立案・推進\\n・新規事業開発\\n・M&A案件の検討・推進\\n・部門横断プロジェクトの統括',
                    
                    # 4. 始業、終業時間（変更あり）
                    'change_type_work_hours': 'change',
                    'old_work_hours': '09:30-18:30',
                    'new_work_hours': '09:00-18:00（フレックスタイム制導入）',
                    
                    # 9. 賃金（変更あり）
                    'change_type_base_salary': 'change',
                    'old_base_salary': '380000',
                    'new_base_salary': '450000',
                    
                    # 10. 諸手当（変更あり）
                    'change_type_allowances': 'change',
                    'old_allowances': '通勤手当（15,000円）、残業手当',
                    'new_allowances': '通勤手当（18,000円）、管理職手当（50,000円）、企画手当（30,000円）',
                    
                    # 12. 賃金支払方法（変更あり）
                    'change_type_payment_method': 'change',
                    'old_payment_method': '銀行振込',
                    'new_payment_method': '銀行振込',  # 実質変更なしだが、テストのため
                    
                    # 変更なしの項目
                    'change_type_contract_period': 'no_change',
                    'current_contract_period_type': '期間の定めなし',
                    
                    'change_type_break_time': 'no_change',
                    'current_break_time': '12:00-13:00（60分）',
                    
                    'change_type_overtime': 'no_change',
                    'current_overtime': '有（36協定の範囲内）',
                    
                    'change_type_holidays': 'no_change',
                    'current_holidays': '完全週休2日制（土日）、国民の祝日、年末年始、夏季休暇',
                    
                    'change_type_vacation': 'no_change',
                    'current_vacation': '年次有給休暇（法定どおり付与）、特別休暇制度あり',
                    
                    'change_type_payment_terms': 'no_change',
                    'current_payment_terms': '毎月末日締切、翌月25日支払',
                    
                    'change_type_retirement': 'no_change',
                    'current_retirement': '定年制65歳、継続雇用制度あり（70歳まで）',
                    
                    'change_type_dismissal': 'no_change',
                    'current_dismissal': '労働基準法及び就業規則の定めによる',
                    
                    'change_type_social_insurance': 'no_change',
                    'current_social_insurance': '健康保険、厚生年金保険、雇用保険、労災保険',
                    
                    'change_type_employment_insurance': 'no_change',
                    'current_employment_insurance': '適用あり'
                }
                
                # ログイン状態をシミュレート
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(test_user.id)
                    sess['_fresh'] = True
                
                print("📄 署名欄レイアウト調整版PDF作成をテスト中...")
                
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
                        print("✅ 署名欄レイアウト調整版PDF生成成功")
                        print(f"📊 Content-Type: {response.headers.get('Content-Type')}")
                        print(f"📊 Content-Length: {len(response.data)} bytes")
                        
                        # PDFファイルとして保存
                        with open('test_adjusted_signature_working_conditions.pdf', 'wb') as f:
                            f.write(response.data)
                        print("✅ PDFファイル保存完了: test_adjusted_signature_working_conditions.pdf")
                        
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
    success = test_adjusted_signature_working_conditions()
    exit(0 if success else 1)
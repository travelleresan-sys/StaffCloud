#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, create_working_conditions_change
from models import CompanySettings, Employee, User
from flask import request
import io
import sys

def test_updated_16_items_working_conditions():
    """更新された16項目労働条件変更通知書作成テスト（賃金支払方法分離版）"""
    with app.app_context():
        with app.test_client() as client:
            try:
                print("🔧 更新された16項目労働条件変更通知書作成テスト開始")
                
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
                
                # 全16項目のフォームデータ（賃金支払条件と支払方法を分離）
                form_data = {
                    'employee_name': '田中 一郎',
                    'change_date': '2024-05-01',
                    'change_reason': '職位変更及び勤務地変更による労働条件の一括変更',
                    
                    # 1. 契約期間（変更なし）
                    'change_type_contract_period': 'no_change',
                    'current_contract_period_type': '期間の定めなし',
                    
                    # 1-1. 契約の更新の有無（変更なし）
                    'change_type_contract_renewal': 'no_change',
                    'current_contract_renewal': '該当なし',
                    
                    # 2. 就業の場所（変更あり）
                    'change_type_workplace': 'change',
                    'old_workplace': '東京都渋谷区テスト町1-2-3（本社ビル2階）',
                    'new_workplace': '神奈川県横浜市テスト区1-1-1（横浜支店ビル4階）',
                    
                    # 3. 従事すべき業務（変更あり）
                    'change_type_job_duties': 'change',
                    'old_job_duties': '総務部一般事務\\n・書類作成\\n・電話対応\\n・来客対応',
                    'new_job_duties': '総務部主任\\n・部門業務の統括・管理\\n・新入社員の指導\\n・業務効率化の企画',
                    
                    # 4. 始業、終業時間（変更あり）
                    'change_type_work_hours': 'change',
                    'old_work_hours': '09:00-18:00',
                    'new_work_hours': '08:30-17:30',
                    
                    # 5. 休憩時間（変更なし）
                    'change_type_break_time': 'no_change',
                    'current_break_time': '12:00-13:00（60分）',
                    
                    # 6. 所定時間外労働の有無（変更なし）
                    'change_type_overtime': 'no_change',
                    'current_overtime': '有（36協定の範囲内）',
                    
                    # 7. 休日（変更なし）
                    'change_type_holidays': 'no_change',
                    'current_holidays': '毎週土・日曜日、祝祭日、GW、夏季休暇、年末年始',
                    
                    # 8. 休暇（変更なし）
                    'change_type_vacation': 'no_change',
                    'current_vacation': '年次有給休暇（入社6カ月後から付与）',
                    
                    # 9. 賃金（変更あり）
                    'change_type_base_salary': 'change',
                    'old_base_salary': '220000',
                    'new_base_salary': '280000',
                    
                    # 10. 諸手当（変更あり）
                    'change_type_allowances': 'change',
                    'old_allowances': '通勤手当のみ',
                    'new_allowances': '通勤手当、職務手当（20,000円）、地域手当（10,000円）',
                    
                    # 11. 賃金締切日、支払日（変更なし）
                    'change_type_payment_terms': 'no_change',
                    'current_payment_terms': '毎月末日締切、翌月25日支払',
                    
                    # 12. 賃金支払方法（変更あり）
                    'change_type_payment_method': 'change',
                    'old_payment_method': '現金支給',
                    'new_payment_method': '銀行振込',
                    
                    # 13. 退職に関する事項（変更なし）
                    'change_type_retirement': 'no_change',
                    'current_retirement': '定年60歳、継続雇用制度有、自己都合退職は30日前に届出',
                    
                    # 14. 解雇の事由及び手続（変更なし）
                    'change_type_dismissal': 'no_change',
                    'current_dismissal': '就業規則違反など、就業規則に準ずる',
                    
                    # 15. 社会保険加入状況（変更なし）
                    'change_type_social_insurance': 'no_change',
                    'current_social_insurance': '厚生年金、健康保険、その他',
                    
                    # 16. 雇用保険の適用（変更なし）
                    'change_type_employment_insurance': 'no_change',
                    'current_employment_insurance': '適用あり'
                }
                
                # ログイン状態をシミュレート
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(test_user.id)
                    sess['_fresh'] = True
                
                print("📄 更新された16項目PDF作成をテスト中...")
                
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
                        print("✅ 更新された16項目PDF生成成功")
                        print(f"📊 Content-Type: {response.headers.get('Content-Type')}")
                        print(f"📊 Content-Length: {len(response.data)} bytes")
                        
                        # PDFファイルとして保存
                        with open('test_updated_16_items_working_conditions.pdf', 'wb') as f:
                            f.write(response.data)
                        print("✅ PDFファイル保存完了: test_updated_16_items_working_conditions.pdf")
                        
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
    success = test_updated_16_items_working_conditions()
    exit(0 if success else 1)
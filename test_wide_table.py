#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, create_working_conditions_change
from models import CompanySettings, Employee, User
from flask import request
import io
import sys

def test_wide_table_working_conditions():
    """テーブル幅拡張版労働条件変更通知書作成テスト"""
    with app.app_context():
        with app.test_client() as client:
            try:
                print("🔧 テーブル幅拡張版労働条件変更通知書作成テスト開始")
                
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
                
                # 幅拡張テスト用フォームデータ（長い文章で幅の効果を確認）
                form_data = {
                    'employee_name': '高橋 美咲',
                    'change_date': '2024-06-01',
                    'change_reason': '組織再編による部門統合及び新規事業立ち上げに伴う職務変更のため、労働条件を下記のとおり変更いたします。',
                    
                    # 2. 就業の場所（変更あり）
                    'change_type_workplace': 'change',
                    'old_workplace': '東京都渋谷区テスト町1-2-3（本社ビル2階・総務部）従来のオープンスペースでの勤務',
                    'new_workplace': '東京都新宿区新規事業町4-5-6（新規事業拠点ビル10階・新事業開発部）個室での専門業務',
                    
                    # 3. 従事すべき業務（変更あり）
                    'change_type_job_duties': 'change',
                    'old_job_duties': '総務部における一般事務業務\\n・社内文書の作成、管理、保管業務\\n・社内会議の準備、調整、記録作成\\n・来客対応、電話応対、郵便物管理\\n・備品管理、発注業務\\n・その他総務部長が指示する業務',
                    'new_job_duties': '新事業開発部における企画管理業務\\n・新規事業の市場調査、競合分析、事業計画策定\\n・プロジェクトマネジメント、進捗管理、品質管理\\n・社外パートナーとの折衝、契約業務、関係構築\\n・事業収支の分析、予算管理、投資判断支援\\n・チームメンバーの業務指導、人材育成\\n・その他新事業開発部長が指示する専門業務',
                    
                    # 9. 賃金（変更あり）
                    'change_type_base_salary': 'change',
                    'old_base_salary': '280000',
                    'new_base_salary': '350000',
                    
                    # 10. 諸手当（変更あり）
                    'change_type_allowances': 'change',
                    'old_allowances': '通勤手当（月額15,000円）、住宅手当（月額20,000円）、食事手当（月額5,000円）',
                    'new_allowances': '通勤手当（月額18,000円）、住宅手当（月額25,000円）、食事手当（月額8,000円）、専門職手当（月額30,000円）、プロジェクト手当（月額20,000円）',
                    
                    # 12. 賃金支払方法（変更あり）
                    'change_type_payment_method': 'change',
                    'old_payment_method': '現金支給',
                    'new_payment_method': '銀行振込',
                    
                    # 変更なしの項目
                    'change_type_contract_period': 'no_change',
                    'current_contract_period_type': '期間の定めなし',
                    
                    'change_type_work_hours': 'no_change',
                    'current_work_hours': '09:00-18:00（休憩60分）',
                    
                    'change_type_break_time': 'no_change',
                    'current_break_time': '12:00-13:00（60分）',
                    
                    'change_type_overtime': 'no_change',
                    'current_overtime': '有（36協定の範囲内）',
                    
                    'change_type_holidays': 'no_change',
                    'current_holidays': '毎週土・日曜日、国民の祝日、GW（4月29日～5月5日）、夏季休暇（8月13日～16日）、年末年始（12月29日～1月3日）',
                    
                    'change_type_vacation': 'no_change',
                    'current_vacation': '年次有給休暇（入社6カ月後10日付与、以降勤続年数により最大20日）、慶弔休暇、産前産後休暇、育児休業、介護休業',
                    
                    'change_type_payment_terms': 'no_change',
                    'current_payment_terms': '毎月末日締切、翌月25日支払（休日の場合は前営業日）',
                    
                    'change_type_retirement': 'no_change',
                    'current_retirement': '定年60歳、継続雇用制度有（65歳まで）、自己都合退職は30日前に書面にて届出',
                    
                    'change_type_dismissal': 'no_change',
                    'current_dismissal': '就業規則違反、経営上の事由、能力不足等、詳細は就業規則第○条に準ずる',
                    
                    'change_type_social_insurance': 'no_change',
                    'current_social_insurance': '厚生年金保険、健康保険、介護保険（40歳以上）、その他法定社会保険',
                    
                    'change_type_employment_insurance': 'no_change',
                    'current_employment_insurance': '適用あり'
                }
                
                # ログイン状態をシミュレート
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(test_user.id)
                    sess['_fresh'] = True
                
                print("📄 テーブル幅拡張版PDF作成をテスト中...")
                
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
                        print("✅ テーブル幅拡張版PDF生成成功")
                        print(f"📊 Content-Type: {response.headers.get('Content-Type')}")
                        print(f"📊 Content-Length: {len(response.data)} bytes")
                        
                        # PDFファイルとして保存
                        with open('test_wide_table_working_conditions.pdf', 'wb') as f:
                            f.write(response.data)
                        print("✅ PDFファイル保存完了: test_wide_table_working_conditions.pdf")
                        
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
    success = test_wide_table_working_conditions()
    exit(0 if success else 1)
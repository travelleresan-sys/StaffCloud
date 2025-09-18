#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, generate_employment_contract_pdf
from models import CompanySettings, Employee, User
from datetime import date

def test_employment_contract_pdf():
    """雇用契約書PDF作成のテスト"""
    with app.app_context():
        try:
            print("🔧 雇用契約書PDF生成テスト開始")
            
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
            
            # テスト用契約データ
            contract_data = {
                'employee': None,  # 新規雇用の場合
                'employee_name': '佐藤 花子',
                'employee_birth_date': '1990-05-15',
                'employee_address': '東京都新宿区テスト1-1-1',
                'employee_phone': '080-1234-5678',
                'company': company,
                'contract_type': '正社員',
                'contract_period_type': '無期契約',
                'start_date': '2024-04-01',
                'end_date': '',
                'contract_renewal': '',
                'renewal_criteria': '',
                'work_location': '東京都渋谷区テスト町1-2-3',
                'work_location_change': 'なし',
                'position': '営業職',
                'department': '営業部',
                'job_description': '法人営業、新規開拓、既存顧客管理業務',
                'work_start_time': '09:00',
                'work_end_time': '18:00',
                'break_time': '60',
                'scheduled_working_hours': '週40時間',
                'shift_work': 'なし',
                'work_days': ['月', '火', '水', '木', '金'],
                'holidays': '土日祝日、年末年始、夏季休暇、その他会社が指定する日',
                'overtime_work': 'あり（36協定の範囲内）',
                'salary_type': '月給',
                'base_salary': '250000',
                'wage_calculation_method': '基本給＋諸手当（通勤手当実費支給、時間外手当は労働基準法に定める率で支給）',
                'salary_closing_date': '月末',
                'payment_date': '翌月25日',
                'payment_method': '銀行振込',
                'allowances': '通勤手当（賃金規定に準ずる）',
                'bonus_payment': 'あり',
                'bonus_details': '年2回（夏季・冬季）基本給の2ヶ月分',
                'trial_period': '3ヶ月',
                'social_insurance': ['健康保険', '厚生年金保険', '雇用保険', '労災保険'],
                'retirement_allowance': 'あり（退職金規程に定めるところによる）',
                'retirement_age': '満65歳',
                'termination_conditions': '''1. 従業員が退職を希望する場合は、30日前までに書面により申し出ること
2. 会社が従業員を解雇する場合は、30日前に予告するか、30日分以上の平均賃金を支払う
3. 定年により退職する場合は、定年に達した日の属する月の末日をもって退職とする
4. その他、労働基準法及び就業規則に定めるところによる''',
                'dismissal_reasons': '''1. 勤務成績が著しく不良で、業務に支障を及ぼす場合
2. 正当な理由なく無断欠勤が継続し、出勤の督促に応じない場合
3. 重要な経歴を詐称して雇用された場合
4. 故意または重大な過失により会社に損害を与えた場合
5. 刑事事件に関し起訴された場合
6. その他前各号に準ずる程度のやむを得ない事由がある場合''',
                'special_conditions': '研修期間中は別途定める研修規程に従う'
            }
            
            print("📄 雇用契約書PDF生成中...")
            pdf_buffer = generate_employment_contract_pdf(contract_data)
            
            # PDFファイルとして保存
            filename = f'test_employment_contract_{contract_data["employee_name"].replace(" ", "_")}.pdf'
            with open(filename, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            
            print(f"✅ 雇用契約書PDF生成完了: {filename}")
            print(f"📊 ファイルサイズ: {len(pdf_buffer.getvalue())} bytes")
            
            return True
            
        except Exception as e:
            print(f"❌ エラー発生: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_employment_contract_pdf()
    exit(0 if success else 1)
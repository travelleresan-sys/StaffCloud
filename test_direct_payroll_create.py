#!/usr/bin/env python3
"""
Flaskアプリ内での給与明細書作成機能の直接テスト
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Flask環境をセットアップ
os.environ['FLASK_APP'] = 'app.py'

from app import app, db, Employee, PayrollCalculation, EmployeePayrollSettings, PayrollSlip
from payroll_slip_pdf_generator import create_payroll_slip_pdf
from datetime import date, datetime

def test_direct_payroll_create():
    """Flaskアプリ内での給与明細書作成テスト"""
    print("🧪 Flaskアプリ内給与明細書作成テスト")
    print("=" * 55)
    
    with app.app_context():
        try:
            # 1. データベースから実際のデータを取得
            print("1️⃣ データベースからデータ取得")
            
            employee = Employee.query.get(4)  # 月曜起算テスト太郎
            if not employee:
                print("❌ 従業員データが見つかりません")
                return False
            print(f"✅ 従業員データ取得: {employee.name}")
            
            payroll_calculation = PayrollCalculation.query.filter(
                PayrollCalculation.employee_id == 4,
                PayrollCalculation.year == 2024,
                PayrollCalculation.month == 9
            ).first()
            if not payroll_calculation:
                print("❌ 給与計算データが見つかりません")
                return False
            print(f"✅ 給与計算データ取得: 基本給 {payroll_calculation.base_salary}")
            
            payroll_settings = EmployeePayrollSettings.query.filter(
                EmployeePayrollSettings.employee_id == 4,
                EmployeePayrollSettings.effective_from <= date(2024, 9, 1)
            ).first()
            print(f"✅ 給与設定取得: {'有り' if payroll_settings else '無し'}")
            
            # 2. PayrollSlipオブジェクトを作成
            print("\n2️⃣ PayrollSlipオブジェクト作成")
            
            slip = PayrollSlip(
                employee_id=employee.id,
                payroll_calculation_id=payroll_calculation.id,
                slip_year=2024,
                slip_month=9
            )
            
            # 基本情報の設定
            slip.base_salary = payroll_calculation.base_salary
            slip.overtime_allowance = payroll_calculation.overtime_allowance or 0
            slip.holiday_allowance = payroll_calculation.holiday_allowance or 0
            slip.night_allowance = payroll_calculation.night_allowance or 0
            
            # 諸手当の設定
            if payroll_settings:
                slip.position_allowance = payroll_settings.position_allowance or 0
                slip.family_allowance = payroll_settings.family_allowance or 0
                slip.transportation_allowance = payroll_settings.transportation_allowance or 0
                slip.housing_allowance = payroll_settings.housing_allowance or 0
                slip.meal_allowance = payroll_settings.meal_allowance or 0
                slip.skill_allowance = payroll_settings.skill_allowance or 0
            
            slip.other_allowance = 0
            
            # 総支給額計算
            slip.gross_salary = (slip.base_salary + slip.overtime_allowance + slip.holiday_allowance + 
                               slip.night_allowance + slip.position_allowance + slip.family_allowance + 
                               slip.transportation_allowance + slip.housing_allowance + slip.meal_allowance + 
                               slip.skill_allowance + slip.other_allowance)
            
            # 社会保険料計算（簡易版）
            gross_salary = slip.gross_salary
            slip.health_insurance = int(gross_salary * 0.0495)  # 4.95%
            slip.pension_insurance = int(gross_salary * 0.0915)  # 9.15%
            slip.employment_insurance = int(gross_salary * 0.003)  # 0.3%
            slip.long_term_care_insurance = 0
            slip.income_tax = 5000
            slip.resident_tax = 8000
            slip.other_deduction = 0
            
            # 総控除額・手取額
            slip.total_deduction = (slip.health_insurance + slip.pension_insurance + slip.employment_insurance + 
                                  slip.long_term_care_insurance + slip.income_tax + slip.resident_tax + 
                                  slip.other_deduction)
            slip.net_salary = slip.gross_salary - slip.total_deduction
            
            # 休暇情報
            slip.absence_days = payroll_calculation.absence_days or 0
            slip.paid_leave_days = payroll_calculation.paid_leave_days or 0
            
            slip.remarks = "直接テスト用給与明細書"
            slip.issued_at = datetime.now()
            
            print(f"✅ PayrollSlipオブジェクト作成完了")
            print(f"   総支給額: {slip.gross_salary:,}")
            print(f"   総控除額: {slip.total_deduction:,}")
            print(f"   手取額: {slip.net_salary:,}")
            
            # 3. PDF生成テスト
            print("\n3️⃣ PDF生成テスト")
            
            pdf_buffer = create_payroll_slip_pdf(slip, employee, payroll_calculation, payroll_settings)
            
            if pdf_buffer:
                pdf_size = len(pdf_buffer.getvalue())
                print(f"✅ PDF生成成功: {pdf_size} bytes")
                
                # テスト用にファイル保存
                with open('test_direct_payroll_slip.pdf', 'wb') as f:
                    f.write(pdf_buffer.getvalue())
                print("✅ テストPDFファイル 'test_direct_payroll_slip.pdf' を保存しました")
                
                return True
            else:
                print("❌ PDF生成失敗")
                return False
                
        except Exception as e:
            print(f"❌ エラー発生: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """メイン実行"""
    success = test_direct_payroll_create()
    
    print(f"\n" + "=" * 55)
    if success:
        print("✅ Flaskアプリ内給与明細書作成テスト成功")
    else:
        print("❌ Flaskアプリ内給与明細書作成テストで問題発生")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
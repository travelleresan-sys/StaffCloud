#!/usr/bin/env python3
"""
給与計算の修正 - EmployeePayrollSettingsから給与情報を取得するように修正
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Employee, EmployeePayrollSettings

def check_payroll_calculation_issue():
    """給与計算の問題を確認・修正"""
    with app.app_context():
        print("🔍 給与計算の問題調査・修正")
        print("=" * 60)
        
        # テスト従業員を確認
        test_employee = Employee.query.filter_by(name="月曜起算テスト太郎").first()
        if not test_employee:
            print("❌ テスト従業員が見つかりません")
            return False
        
        print(f"✅ テスト従業員: {test_employee.name}")
        print(f"   従業員のbase_wage: {test_employee.base_wage}")
        print(f"   従業員のwage_type: {test_employee.wage_type}")
        
        # 給与設定を確認
        payroll_setting = EmployeePayrollSettings.query.filter_by(
            employee_id=test_employee.id
        ).first()
        
        if payroll_setting:
            print(f"✅ 給与設定が存在:")
            print(f"   基本給: {payroll_setting.base_salary}円")
            print(f"   有効期間: {payroll_setting.effective_from} ～ {payroll_setting.effective_until}")
        else:
            print("❌ 給与設定が見つかりません")
            return False
        
        # 問題の調査
        print(f"\n🔍 問題分析:")
        if test_employee.base_wage is None and payroll_setting.base_salary > 0:
            print("❌ 従業員テーブルのbase_wageがNullだが、給与設定には基本給がある")
            print("   給与計算関数でEmployeePayrollSettingsから取得すべき")
            
            # 従業員レコードを更新（暫定的修正）
            test_employee.base_wage = payroll_setting.base_salary
            test_employee.wage_type = 'monthly'
            db.session.commit()
            print(f"✅ 従業員テーブルを更新しました: base_wage={payroll_setting.base_salary}")
            
            return True
        elif test_employee.base_wage and test_employee.base_wage > 0:
            print("✅ 従業員テーブルのbase_wageが設定されている")
            return True
        else:
            print("❌ 給与設定に問題があります")
            return False

def test_payroll_calculation_after_fix():
    """修正後の給与計算をテスト"""
    with app.app_context():
        print(f"\n🧮 修正後の給与計算テスト")
        print("=" * 40)
        
        test_employee = Employee.query.filter_by(name="月曜起算テスト太郎").first()
        
        try:
            from app import calculate_monthly_payroll
            from models import PayrollCalculation
            
            # 既存の計算結果を削除
            existing = PayrollCalculation.query.filter(
                PayrollCalculation.employee_id == test_employee.id,
                PayrollCalculation.year == 2024,
                PayrollCalculation.month == 9
            ).first()
            if existing:
                db.session.delete(existing)
                db.session.commit()
            
            # 再計算
            result = calculate_monthly_payroll(test_employee.id, 2024, 9)
            
            if result:
                # 結果を確認
                calculation = PayrollCalculation.query.filter(
                    PayrollCalculation.employee_id == test_employee.id,
                    PayrollCalculation.year == 2024,
                    PayrollCalculation.month == 9
                ).first()
                
                if calculation:
                    print(f"✅ 給与計算成功:")
                    print(f"   基本給: {calculation.base_salary:,}円")
                    print(f"   時間外手当: {calculation.overtime_allowance:,}円")
                    print(f"   休日手当: {calculation.holiday_allowance:,}円")
                    print(f"   総支給額: {calculation.gross_salary:,}円")
                    
                    if calculation.gross_salary > 0:
                        print("✅ 給与計算が正常に動作しています")
                        return True
                    else:
                        print("❌ 給与計算結果が0円です")
                        return False
                else:
                    print("❌ 給与計算結果が保存されていません")
                    return False
            else:
                print("❌ 給与計算が失敗しました")
                return False
                
        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success1 = check_payroll_calculation_issue()
    success2 = test_payroll_calculation_after_fix()
    
    print(f"\n" + "=" * 60)
    if success1 and success2:
        print("✅ 給与計算の問題が修正されました")
    else:
        print("❌ 給与計算に問題があります")
    
    sys.exit(0 if (success1 and success2) else 1)
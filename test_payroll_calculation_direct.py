#!/usr/bin/env python3
"""
給与計算機能の直接テスト
"""

import sys
import os
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Employee, EmployeePayrollSettings, WorkingTimeRecord, PayrollCalculation

def test_payroll_calculation():
    """給与計算機能の直接テスト"""
    with app.app_context():
        print("🔍 給与計算機能直接テスト")
        print("=" * 60)
        
        # テスト従業員を確認
        test_employee = Employee.query.filter_by(name="月曜起算テスト太郎").first()
        if not test_employee:
            print("❌ テスト従業員が見つかりません")
            return False
        
        print(f"✅ テスト従業員: {test_employee.name} (ID: {test_employee.id})")
        
        # 給与設定を確認
        payroll_settings = EmployeePayrollSettings.query.filter_by(
            employee_id=test_employee.id
        ).first()
        
        if not payroll_settings:
            print("❌ 給与設定が見つかりません - 作成します")
            # デフォルトの給与設定を作成
            payroll_settings = EmployeePayrollSettings(
                employee_id=test_employee.id,
                base_salary=250000,  # 基本給25万円
                effective_from=date(2024, 1, 1)
            )
            db.session.add(payroll_settings)
            db.session.commit()
            print("✅ デフォルト給与設定を作成しました")
        else:
            print(f"✅ 給与設定が存在: 基本給 {payroll_settings.base_salary}円")
        
        # 勤怠データを確認
        working_records = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == test_employee.id,
            db.extract('year', WorkingTimeRecord.work_date) == 2024,
            db.extract('month', WorkingTimeRecord.work_date) == 9
        ).all()
        
        if not working_records:
            print("❌ 2024年9月の勤怠データが見つかりません")
            return False
        
        print(f"✅ 勤怠データ: {len(working_records)}件")
        
        # 勤怠データの詳細を表示
        total_regular = 0
        total_overtime = 0
        total_holiday = 0
        
        for record in working_records:
            total_regular += record.regular_working_minutes or 0
            total_overtime += record.overtime_minutes or 0
            total_holiday += record.holiday_minutes or 0
            
            print(f"   {record.work_date}: 法定内{record.regular_working_minutes}分 "
                  f"+ 法定外{record.overtime_minutes}分 + 休日{record.holiday_minutes}分")
        
        print(f"月合計: 法定内{total_regular}分({total_regular//60}h{total_regular%60}m) "
              f"+ 法定外{total_overtime}分({total_overtime//60}h{total_overtime%60}m) "
              f"+ 休日{total_holiday}分({total_holiday//60}h{total_holiday%60}m)")
        
        # calculate_monthly_payroll関数をインポートして実行
        try:
            from app import calculate_monthly_payroll
            print("\n🧮 給与計算実行中...")
            
            result = calculate_monthly_payroll(test_employee.id, 2024, 9)
            
            if result:
                print("✅ 給与計算成功")
                
                # 計算結果を確認
                calculation = PayrollCalculation.query.filter(
                    PayrollCalculation.employee_id == test_employee.id,
                    PayrollCalculation.year == 2024,
                    PayrollCalculation.month == 9
                ).first()
                
                if calculation:
                    print(f"\n📊 給与計算結果:")
                    print(f"   基本給: {calculation.base_salary or 0:,}円")
                    print(f"   法定内労働時間: {calculation.regular_working_minutes or 0}分")
                    print(f"   法定外残業時間: {calculation.overtime_minutes or 0}分")
                    print(f"   法定外休日労働時間: {calculation.holiday_minutes or 0}分")
                    print(f"   時間外手当: {calculation.overtime_allowance or 0:,}円")
                    print(f"   休日手当: {calculation.holiday_allowance or 0:,}円")
                    print(f"   総支給額: {calculation.gross_salary or 0:,}円")
                    print(f"   総控除額: {calculation.total_deductions or 0:,}円")
                    print(f"   差引支給額: {calculation.net_salary or 0:,}円")
                    return True
                else:
                    print("❌ 給与計算結果が保存されていません")
                    return False
            else:
                print("❌ 給与計算が失敗しました")
                return False
                
        except Exception as e:
            print(f"❌ 給与計算でエラー: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_payroll_calculation()
    print(f"\n" + "=" * 60)
    if success:
        print("✅ 給与計算機能は正常に動作しています")
    else:
        print("❌ 給与計算機能に問題があります")
    
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
給与設定表示問題の調査
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Employee, EmployeePayrollSettings, PayrollCalculation

def debug_payroll_settings():
    """給与設定の表示問題を調査"""
    with app.app_context():
        print("🔍 給与設定表示問題の調査")
        print("=" * 50)
        
        # テスト従業員を確認
        test_employee = Employee.query.filter_by(name="月曜起算テスト太郎").first()
        if not test_employee:
            print("❌ テスト従業員が見つかりません")
            return False
        
        print(f"✅ テスト従業員: {test_employee.name} (ID: {test_employee.id})")
        
        # 給与設定を確認（現在のapp.pyのロジックと同じ）
        target_date = date(2024, 9, 1)
        payroll_settings = EmployeePayrollSettings.query.filter(
            EmployeePayrollSettings.employee_id == test_employee.id,
            EmployeePayrollSettings.effective_from <= target_date
        ).filter(
            db.or_(
                EmployeePayrollSettings.effective_until.is_(None),
                EmployeePayrollSettings.effective_until >= target_date
            )
        ).first()
        
        print(f"\n📋 給与設定取得結果 (対象日: {target_date}):")
        if payroll_settings:
            print(f"✅ 給与設定が見つかりました:")
            print(f"   ID: {payroll_settings.id}")
            print(f"   基本給: {payroll_settings.base_salary:,}円")
            print(f"   有効期間: {payroll_settings.effective_from} ～ {payroll_settings.effective_until}")
            print(f"   交通費: {payroll_settings.transportation_allowance or 0:,}円")
            print(f"   役職手当: {payroll_settings.position_allowance or 0:,}円")
            
            # テンプレートでの表示をシミュレート
            print(f"\n📄 テンプレートでの表示シミュレート:")
            print(f"   payroll_data.settings: {payroll_settings}")
            print(f"   payroll_data.settings.base_salary: {payroll_settings.base_salary}")
            
            return True
        else:
            print("❌ 給与設定が見つかりません")
            
            # 全ての給与設定を表示
            all_settings = EmployeePayrollSettings.query.filter_by(
                employee_id=test_employee.id
            ).all()
            
            print(f"\n📝 従業員の全給与設定:")
            for setting in all_settings:
                print(f"   ID: {setting.id}, 基本給: {setting.base_salary:,}円")
                print(f"   有効期間: {setting.effective_from} ～ {setting.effective_until}")
            
            return False

def test_payroll_dashboard_data():
    """給与計算ダッシュボードのデータ取得をテスト"""
    with app.app_context():
        print(f"\n🌐 給与計算ダッシュボードのデータ取得テスト")
        print("=" * 50)
        
        test_employee = Employee.query.filter_by(name="月曜起算テスト太郎").first()
        employee_id = test_employee.id
        selected_year = 2024
        selected_month = 9
        
        # app.pyのpayroll_dashboardと同じロジック
        selected_employee = Employee.query.get(employee_id)
        
        # 既存の給与計算結果を取得
        existing_calculation = PayrollCalculation.query.filter(
            PayrollCalculation.employee_id == employee_id,
            PayrollCalculation.year == selected_year,
            PayrollCalculation.month == selected_month
        ).first()
        
        # 従業員の給与設定を取得
        payroll_settings = EmployeePayrollSettings.query.filter(
            EmployeePayrollSettings.employee_id == employee_id,
            EmployeePayrollSettings.effective_from <= date(selected_year, selected_month, 1)
        ).filter(
            db.or_(
                EmployeePayrollSettings.effective_until.is_(None),
                EmployeePayrollSettings.effective_until >= date(selected_year, selected_month, 1)
            )
        ).first()
        
        # 勤怠データを取得
        from models import WorkingTimeRecord
        working_records = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == employee_id,
            db.extract('year', WorkingTimeRecord.work_date) == selected_year,
            db.extract('month', WorkingTimeRecord.work_date) == selected_month
        ).all()
        
        payroll_data = {
            'employee': selected_employee,
            'calculation': existing_calculation,
            'settings': payroll_settings,
            'records': working_records,
            'year': selected_year,
            'month': selected_month
        }
        
        print(f"📊 payroll_data の内容:")
        print(f"   employee: {payroll_data['employee'].name if payroll_data['employee'] else None}")
        print(f"   calculation: {'あり' if payroll_data['calculation'] else 'なし'}")
        print(f"   settings: {'あり' if payroll_data['settings'] else 'なし'}")
        print(f"   records: {len(payroll_data['records'])}件")
        
        if payroll_data['settings']:
            print(f"   settings.base_salary: {payroll_data['settings'].base_salary:,}円")
        else:
            print("   ❌ settings が None です")
        
        return payroll_data['settings'] is not None

if __name__ == "__main__":
    success1 = debug_payroll_settings()
    success2 = test_payroll_dashboard_data()
    
    print(f"\n" + "=" * 50)
    if success1 and success2:
        print("✅ 給与設定は正常に取得できています")
        print("   問題はテンプレート側にある可能性があります")
    else:
        print("❌ 給与設定の取得に問題があります")
    
    sys.exit(0 if (success1 and success2) else 1)
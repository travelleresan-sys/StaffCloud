#!/usr/bin/env python3
"""
賃金台帳データの確認スクリプト
"""

import sqlite3
from datetime import datetime
from models import db, Employee, PayrollCalculation, WageRegister
from app import app

def check_wage_register_data():
    """賃金台帳データの存在を確認"""
    
    with app.app_context():
        print("=" * 60)
        print("賃金台帳データ確認")
        print("=" * 60)
        
        # 1. 従業員リスト確認
        print("\n1. 在籍中の従業員:")
        employees = Employee.query.filter_by(status='在籍中').all()
        for emp in employees:
            print(f"  - ID: {emp.id}, 名前: {emp.name}")
        
        # 2. 給与計算データ確認
        print("\n2. 給与計算データ:")
        payroll_data = PayrollCalculation.query.order_by(
            PayrollCalculation.year.desc(), 
            PayrollCalculation.month.desc()
        ).limit(10).all()
        
        for payroll in payroll_data:
            employee = Employee.query.get(payroll.employee_id)
            print(f"  - {payroll.year}年{payroll.month}月: {employee.name if employee else 'Unknown'}")
        
        # 3. 賃金台帳データ確認
        print("\n3. 賃金台帳データ (wage_register):")
        wage_registers = WageRegister.query.all()
        
        if not wage_registers:
            print("  ⚠️ 賃金台帳データが存在しません")
        else:
            for wage_reg in wage_registers:
                employee = Employee.query.get(wage_reg.employee_id)
                print(f"  - {wage_reg.year}年: {employee.name if employee else 'Unknown'} (ID: {wage_reg.employee_id})")
        
        # 4. 田中太郎の2023年データ確認
        print("\n4. 田中太郎の2023年データ確認:")
        tanaka = Employee.query.filter_by(name='田中 太郎').first()
        if tanaka:
            print(f"  田中太郎 ID: {tanaka.id}")
            
            # 2023年の給与計算データ
            payroll_2023 = PayrollCalculation.query.filter_by(
                employee_id=tanaka.id,
                year=2023
            ).all()
            
            if payroll_2023:
                print(f"  2023年給与計算データ: {len(payroll_2023)}件")
                for p in payroll_2023:
                    print(f"    - {p.month}月")
            else:
                print("  ⚠️ 2023年の給与計算データなし")
            
            # 2023年の賃金台帳データ
            wage_2023 = WageRegister.query.filter_by(
                employee_id=tanaka.id,
                year=2023
            ).first()
            
            if wage_2023:
                print("  ✅ 2023年の賃金台帳データあり")
            else:
                print("  ❌ 2023年の賃金台帳データなし")
                
                # 2024年のデータを確認
                wage_2024 = WageRegister.query.filter_by(
                    employee_id=tanaka.id,
                    year=2024
                ).first()
                
                if wage_2024:
                    print("  ✅ 2024年の賃金台帳データはあり")

def create_sample_wage_register():
    """サンプルの賃金台帳データを作成"""
    
    from wage_register_manager import WageRegisterManager
    
    with app.app_context():
        print("\n" + "=" * 60)
        print("サンプル賃金台帳データ作成")
        print("=" * 60)
        
        tanaka = Employee.query.filter_by(name='田中 太郎').first()
        if not tanaka:
            print("❌ 田中太郎が見つかりません")
            return
        
        # 2023年の給与計算データがあるか確認
        payroll_2023 = PayrollCalculation.query.filter_by(
            employee_id=tanaka.id,
            year=2023
        ).all()
        
        if not payroll_2023:
            print("⚠️ 2023年の給与計算データがないため、サンプルデータを作成します")
            
            # サンプル給与計算データを作成
            for month in [10, 11, 12]:
                payroll = PayrollCalculation(
                    employee_id=tanaka.id,
                    year=2023,
                    month=month,
                    wage_type='monthly',
                    base_salary=250000,
                    regular_working_minutes=10560,
                    overtime_minutes=1200,
                    overtime_allowance=30000,
                    transportation_allowance=10000,
                    housing_allowance=20000,
                    health_insurance=15000,
                    pension_insurance=27000,
                    employment_insurance=2000,
                    income_tax=20000,
                    resident_tax=18000,
                    gross_salary=310000,
                    total_deductions=82000,
                    net_salary=228000,
                    calculated_at=datetime.now()
                )
                db.session.add(payroll)
            
            db.session.commit()
            print("✅ 2023年10-12月の給与計算データを作成しました")
        
        # 賃金台帳データを更新
        wage_manager = WageRegisterManager()
        
        for payroll in PayrollCalculation.query.filter_by(
            employee_id=tanaka.id,
            year=2023
        ).all():
            payroll_data = {
                'base_salary': payroll.base_salary,
                'overtime_allowance': payroll.overtime_allowance or 0,
                'night_allowance': payroll.night_allowance or 0,
                'holiday_allowance': payroll.holiday_allowance or 0,
                'commute_allowance': payroll.transportation_allowance or 0,
                'housing_allowance': payroll.housing_allowance or 0,
                'health_insurance': payroll.health_insurance or 0,
                'pension_insurance': payroll.pension_insurance or 0,
                'employment_insurance': payroll.employment_insurance or 0,
                'income_tax': payroll.income_tax or 0,
                'resident_tax': payroll.resident_tax or 0,
                'gross_pay': payroll.gross_salary or 0,
                'deductions': payroll.total_deductions or 0,
                'net_pay': payroll.net_salary or 0,
                'working_days': 22,
                'working_hours': 176.0,
                'overtime_hours': 20.0,
                'night_hours': 0,
                'holiday_hours': 0
            }
            
            success = wage_manager.update_wage_register(
                tanaka.id, 
                2023, 
                payroll.month, 
                payroll_data
            )
            
            if success:
                print(f"✅ 2023年{payroll.month}月の賃金台帳データを作成/更新")
        
        print("\n賃金台帳データの作成が完了しました")

if __name__ == '__main__':
    # データ確認
    check_wage_register_data()
    
    # 必要に応じてサンプルデータ作成
    response = input("\n2023年の賃金台帳データを作成しますか？ (y/n): ")
    if response.lower() == 'y':
        create_sample_wage_register()
        print("\n再度データを確認します...")
        check_wage_register_data()
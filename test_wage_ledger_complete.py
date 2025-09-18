#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
賃金台帳システム完全テスト
- 給与計算を実行
- 賃金台帳データを自動生成
- PDF出力をテスト
"""

import os
import sys
from datetime import datetime, date
from models import db, Employee, PayrollCalculation, EmployeePayrollSettings
from wage_register_manager import WageRegisterManager
from wage_ledger_pdf_generator import WageLedgerPDFGenerator

# Flask app context
from app import app

def test_complete_wage_ledger_system():
    """賃金台帳システムの完全テスト"""
    
    with app.app_context():
        print("=== 賃金台帳システム完全テスト開始 ===")
        
        # 1. 従業員データ確認
        employee = Employee.query.filter_by(status='在籍中').first()
        if not employee:
            print("❌ 在籍中の従業員が見つかりません")
            return False
        
        print(f"✅ テスト対象従業員: {employee.name} (ID: {employee.id})")
        
        # 2. 給与設定確認・作成
        payroll_settings = EmployeePayrollSettings.query.filter_by(employee_id=employee.id).first()
        if not payroll_settings:
            print("📝 給与設定を作成中...")
            payroll_settings = EmployeePayrollSettings(
                employee_id=employee.id,
                base_salary=300000,
                hourly_rate=1500,
                transportation_allowance=10000,
                housing_allowance=20000
            )
            db.session.add(payroll_settings)
            db.session.commit()
            print("✅ 給与設定を作成しました")
        
        # 3. 複数月の給与計算テスト実行
        year = 2024
        months = [10, 11, 12]  # 3ヶ月分テスト
        
        print(f"\n📊 {year}年度 {len(months)}ヶ月分の給与計算実行...")
        
        for month in months:
            # 既存の計算があるかチェック
            existing = PayrollCalculation.query.filter_by(
                employee_id=employee.id,
                year=year,
                month=month
            ).first()
            
            if existing:
                print(f"  ✅ {month}月分の給与計算は既に完了済み")
                continue
            
            # 給与計算データ作成
            payroll = PayrollCalculation(
                employee_id=employee.id,
                year=year,
                month=month,
                base_salary=payroll_settings.base_salary,
                wage_type='monthly',
                regular_working_minutes=10560,  # 176h * 60min = 10,560min
                overtime_minutes=1200,          # 20h * 60min = 1,200min
                night_working_minutes=300,      # 5h * 60min = 300min
                holiday_minutes=480,            # 8h * 60min = 480min
                overtime_allowance=37500,       # 20h * 1500 * 1.25
                night_allowance=9375,           # 5h * 1500 * 1.25
                holiday_allowance=16200,        # 8h * 1500 * 1.35
                transportation_allowance=payroll_settings.transportation_allowance,
                housing_allowance=payroll_settings.housing_allowance,
                health_insurance=15000,
                pension_insurance=27150,
                employment_insurance=2000,
                income_tax=25000,
                resident_tax=18000,
                calculated_at=datetime.now()
            )
            
            # 支給額・控除額・差引支給額計算
            payroll.gross_pay = (payroll.base_salary + payroll.overtime_allowance + 
                               payroll.night_allowance + payroll.holiday_allowance +
                               payroll.transportation_allowance + payroll.housing_allowance)
            
            payroll.deductions = (payroll.health_insurance + payroll.pension_insurance +
                                payroll.employment_insurance + payroll.income_tax + 
                                payroll.resident_tax)
            
            payroll.net_pay = payroll.gross_pay - payroll.deductions
            
            db.session.add(payroll)
            db.session.commit()
            
            print(f"  ✅ {month}月分給与計算完了 (総支給額: ¥{payroll.gross_pay:,})")
            
            # 賃金台帳データ自動更新
            try:
                wage_manager = WageRegisterManager()
                payroll_data = {
                    'base_salary': payroll.base_salary,
                    'overtime_allowance': payroll.overtime_allowance,
                    'night_allowance': payroll.night_allowance,
                    'holiday_allowance': payroll.holiday_allowance,
                    'commute_allowance': payroll.transportation_allowance,
                    'housing_allowance': payroll.housing_allowance,
                    'health_insurance': payroll.health_insurance,
                    'pension_insurance': payroll.pension_insurance,
                    'employment_insurance': payroll.employment_insurance,
                    'income_tax': payroll.income_tax,
                    'resident_tax': payroll.resident_tax,
                    'gross_pay': payroll.gross_pay,
                    'deductions': payroll.deductions,
                    'net_pay': payroll.net_pay,
                    'working_days': 22,  # fixed for testing
                    'working_hours': round(payroll.regular_working_minutes / 60, 1),
                    'overtime_hours': round(payroll.overtime_minutes / 60, 1),
                    'night_hours': round(payroll.night_working_minutes / 60, 1),
                    'holiday_hours': round(payroll.holiday_minutes / 60, 1)
                }
                
                success = wage_manager.update_wage_register(employee.id, year, month, payroll_data)
                if success:
                    print(f"  ✅ {month}月分賃金台帳データ更新完了")
                else:
                    print(f"  ⚠️ {month}月分賃金台帳データ更新失敗")
                    
            except Exception as e:
                print(f"  ❌ 賃金台帳更新エラー: {e}")
        
        # 4. 賃金台帳データ確認
        print(f"\n📋 {year}年度賃金台帳データ確認...")
        wage_manager = WageRegisterManager()
        wage_data = wage_manager.get_wage_register_data(employee.id, year)
        
        if not wage_data:
            print("❌ 賃金台帳データが見つかりません")
            return False
        
        print(f"✅ 賃金台帳データ取得成功")
        print(f"   基本給年間合計: ¥{wage_data.get('annual_base_salary', 0):,}")
        print(f"   総支給額年間合計: ¥{wage_data.get('annual_gross_pay', 0):,}")
        print(f"   差引支給額年間合計: ¥{wage_data.get('annual_net_pay', 0):,}")
        
        # 5. PDF生成テスト
        print(f"\n📄 {year}年度賃金台帳PDF生成テスト...")
        
        employee_data = {
            'id': employee.id,
            'name': employee.name,
            'employee_number': f'EMP{employee.id:03d}'
        }
        
        generator = WageLedgerPDFGenerator()
        output_path = f'test_wage_ledger_{employee.name}_{year}.pdf'
        
        success = generator.generate_wage_ledger_pdf(employee_data, wage_data, year, output_path)
        
        if success:
            print(f"✅ 賃金台帳PDF生成完了: {output_path}")
            
            # ファイルサイズ確認
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   ファイルサイズ: {file_size:,} bytes")
        else:
            print("❌ 賃金台帳PDF生成失敗")
            return False
        
        print("\n🎉 賃金台帳システム完全テスト成功！")
        print("\n=== テスト結果サマリー ===")
        print(f"- 対象従業員: {employee.name}")
        print(f"- 対象年度: {year}年")
        print(f"- 給与計算月数: {len(months)}ヶ月")
        print(f"- 賃金台帳データ: 生成済み")
        print(f"- PDF出力: 完了 ({output_path})")
        
        return True

if __name__ == '__main__':
    success = test_complete_wage_ledger_system()
    sys.exit(0 if success else 1)
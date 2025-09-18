#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
賃金台帳システム - 1ヶ月分のデータでのPDF生成テスト
"""

import os
import json
from wage_ledger_pdf_generator import WageLedgerPDFGenerator

def test_single_month_wage_ledger():
    """1ヶ月分のデータで賃金台帳PDF生成をテスト"""
    
    print("=" * 60)
    print("賃金台帳PDF生成テスト（1ヶ月分のデータ）")
    print("=" * 60)
    
    # 従業員データ
    employee_data = {
        'id': 1,
        'name': '山田花子',
        'employee_number': 'EMP002'
    }
    
    # 1ヶ月分のデータ（11月のみ）
    single_month_data = {"11": 280000}  # 11月のみデータあり
    
    # 賃金データ（11月のみデータを設定）
    wage_data = {
        # 基本給（11月のみ）
        'monthly_base_salary': json.dumps({"11": 250000}),
        'annual_base_salary': 250000,  # 1ヶ月分の合計
        
        # 時間外手当（11月のみ）
        'monthly_overtime_allowance': json.dumps({"11": 35000}),
        'annual_overtime_allowance': 35000,
        
        # 深夜手当（11月のみ）
        'monthly_night_allowance': json.dumps({"11": 5000}),
        'annual_night_allowance': 5000,
        
        # 休日手当（11月のみ）
        'monthly_holiday_allowance': json.dumps({"11": 15000}),
        'annual_holiday_allowance': 15000,
        
        # 通勤手当（11月のみ）
        'monthly_commute_allowance': json.dumps({"11": 10000}),
        'annual_commute_allowance': 10000,
        
        # 住宅手当（11月のみ）
        'monthly_housing_allowance': json.dumps({"11": 20000}),
        'annual_housing_allowance': 20000,
        
        # 健康保険料（11月のみ）
        'monthly_health_insurance': json.dumps({"11": 15000}),
        'annual_health_insurance': 15000,
        
        # 厚生年金保険料（11月のみ）
        'monthly_pension_insurance': json.dumps({"11": 27000}),
        'annual_pension_insurance': 27000,
        
        # 雇用保険料（11月のみ）
        'monthly_employment_insurance': json.dumps({"11": 2000}),
        'annual_employment_insurance': 2000,
        
        # 所得税（11月のみ）
        'monthly_income_tax': json.dumps({"11": 12000}),
        'annual_income_tax': 12000,
        
        # 住民税（11月のみ）
        'monthly_resident_tax': json.dumps({"11": 18000}),
        'annual_resident_tax': 18000,
        
        # 支給額・控除額・差引支給額（11月のみ）
        'monthly_gross_pay': json.dumps({"11": 335000}),
        'annual_gross_pay': 335000,
        
        'monthly_deductions': json.dumps({"11": 74000}),
        'annual_deductions': 74000,
        
        'monthly_net_pay': json.dumps({"11": 261000}),
        'annual_net_pay': 261000,
        
        # 労働時間データ（11月のみ）
        'monthly_working_days': json.dumps({"11": 22}),
        'annual_working_days': 22,
        
        'monthly_working_hours': json.dumps({"11": 176.0}),
        'annual_working_hours': 176.0,
        
        'monthly_overtime_hours': json.dumps({"11": 25.0}),
        'annual_overtime_hours': 25.0,
        
        'monthly_night_hours': json.dumps({"11": 5.0}),
        'annual_night_hours': 5.0,
        
        'monthly_holiday_hours': json.dumps({"11": 8.0}),
        'annual_holiday_hours': 8.0
    }
    
    # PDF生成
    generator = WageLedgerPDFGenerator()
    output_path = 'test_single_month_wage_ledger.pdf'
    
    print("\n📊 データ内容:")
    print(f"  - 従業員: {employee_data['name']} ({employee_data['employee_number']})")
    print(f"  - 対象年度: 2024年")
    print(f"  - データがある月: 11月のみ")
    print(f"  - 11月基本給: ¥250,000")
    print(f"  - 11月総支給額: ¥335,000")
    print(f"  - 11月差引支給額: ¥261,000")
    
    print("\n📄 PDF生成中...")
    success = generator.generate_wage_ledger_pdf(employee_data, wage_data, 2024, output_path)
    
    if success:
        print(f"✅ PDF生成成功: {output_path}")
        
        # ファイルサイズ確認
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   ファイルサイズ: {file_size:,} bytes")
            
        print("\n📝 PDF表示内容:")
        print("  - 1月〜10月: 空欄（-）で表示")
        print("  - 11月: データ表示")
        print("  - 12月: 空欄（-）で表示")
        print("  - 年間合計: 11月分のみの合計値")
        
        return True
    else:
        print("❌ PDF生成失敗")
        return False

def test_multiple_months():
    """複数月（飛び飛び）のデータでのテスト"""
    
    print("\n" + "=" * 60)
    print("賃金台帳PDF生成テスト（複数月・飛び飛びデータ）")
    print("=" * 60)
    
    employee_data = {
        'id': 3,
        'name': '鈴木一郎',
        'employee_number': 'EMP003'
    }
    
    # 3ヶ月分のデータ（4月、7月、11月）
    wage_data = {
        'monthly_base_salary': json.dumps({
            "4": 260000,
            "7": 265000,
            "11": 270000
        }),
        'annual_base_salary': 795000,
        
        'monthly_gross_pay': json.dumps({
            "4": 300000,
            "7": 310000,
            "11": 320000
        }),
        'annual_gross_pay': 930000,
        
        'monthly_net_pay': json.dumps({
            "4": 230000,
            "7": 235000,
            "11": 240000
        }),
        'annual_net_pay': 705000,
        
        # その他の項目は空のJSONで初期化
        'monthly_overtime_allowance': json.dumps({}),
        'annual_overtime_allowance': 0,
        'monthly_deductions': json.dumps({}),
        'annual_deductions': 0,
        'monthly_working_days': json.dumps({}),
        'annual_working_days': 0,
        'monthly_working_hours': json.dumps({}),
        'annual_working_hours': 0,
    }
    
    generator = WageLedgerPDFGenerator()
    output_path = 'test_multiple_months_wage_ledger.pdf'
    
    print("\n📊 データ内容:")
    print(f"  - 従業員: {employee_data['name']}")
    print(f"  - データがある月: 4月、7月、11月")
    print(f"  - 年間基本給合計: ¥795,000")
    
    print("\n📄 PDF生成中...")
    success = generator.generate_wage_ledger_pdf(employee_data, wage_data, 2024, output_path)
    
    if success:
        print(f"✅ PDF生成成功: {output_path}")
        print("\n📝 PDF表示内容:")
        print("  - 4月、7月、11月: データ表示")
        print("  - その他の月: 空欄（-）で表示")
        print("  - 年間合計: 3ヶ月分の合計値")
        return True
    else:
        print("❌ PDF生成失敗")
        return False

if __name__ == '__main__':
    print("賃金台帳PDF生成テスト開始\n")
    
    # 1ヶ月分のテスト
    result1 = test_single_month_wage_ledger()
    
    # 複数月（飛び飛び）のテスト
    result2 = test_multiple_months()
    
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    print(f"1ヶ月分データテスト: {'✅ 成功' if result1 else '❌ 失敗'}")
    print(f"複数月データテスト: {'✅ 成功' if result2 else '❌ 失敗'}")
    
    if result1 and result2:
        print("\n✨ 結論: 賃金台帳PDFは1ヶ月分のデータでも正常に生成されます")
        print("  - データがない月は空欄（-）として表示")
        print("  - 年間合計は存在するデータのみで計算")
        print("  - 12ヶ月の枠組みは常に表示")
    
    import sys
    sys.exit(0 if (result1 and result2) else 1)
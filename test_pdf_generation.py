#!/usr/bin/env python3
"""
PDF生成機能の単体テスト
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from payroll_slip_pdf_generator import create_payroll_slip_pdf
from datetime import datetime

def test_pdf_generation():
    """PDF生成機能の単体テスト"""
    print("🔧 PDF生成機能単体テスト")
    print("=" * 50)
    
    try:
        # モックデータを作成
        class MockPayrollSlip:
            def __init__(self):
                self.slip_year = 2024
                self.slip_month = 9
                self.base_salary = 250000
                self.overtime_allowance = 27966
                self.holiday_allowance = 0
                self.night_allowance = 0
                self.transportation_allowance = 0
                self.position_allowance = 0
                self.other_allowance = 0
                self.gross_salary = 277966
                self.health_insurance = 13760
                self.pension_insurance = 25429
                self.employment_insurance = 834
                self.long_term_care_insurance = 0
                self.income_tax = 5000
                self.resident_tax = 8000
                self.other_deduction = 0
                self.total_deduction = 53023
                self.net_salary = 224943
                self.paid_leave_days = 0
                self.absence_days = 0
                self.remarks = "テスト用給与明細書"
                self.issued_at = datetime.now()
        
        class MockEmployee:
            def __init__(self):
                self.name = "月曜起算テスト太郎"
                self.employee_id = "EMP001"
        
        class MockPayrollCalculation:
            def __init__(self):
                self.regular_working_minutes = 9600  # 160時間
                self.overtime_minutes = 2400  # 40時間
        
        # PDF生成テスト
        print("1️⃣ PDF生成開始")
        slip = MockPayrollSlip()
        employee = MockEmployee()
        calculation = MockPayrollCalculation()
        
        pdf_buffer = create_payroll_slip_pdf(slip, employee, calculation)
        
        if pdf_buffer:
            pdf_size = len(pdf_buffer.getvalue())
            print(f"✅ PDF生成成功: {pdf_size} bytes")
            
            # テスト用にファイル保存
            with open('test_pdf_generation.pdf', 'wb') as f:
                f.write(pdf_buffer.getvalue())
            print("✅ テストPDFファイル 'test_pdf_generation.pdf' を保存しました")
            return True
        else:
            print("❌ PDF生成失敗: バッファが空です")
            return False
            
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ PDF生成エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    success = test_pdf_generation()
    
    print(f"\n" + "=" * 50)
    if success:
        print("✅ PDF生成機能単体テストが成功しました")
    else:
        print("❌ PDF生成機能に問題があります")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
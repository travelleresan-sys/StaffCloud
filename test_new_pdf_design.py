#!/usr/bin/env python3
"""
新しいPDFデザインのテスト
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from payroll_slip_pdf_generator import create_payroll_slip_pdf
from datetime import datetime

def test_new_pdf_design():
    """新しいPDFデザインのテスト"""
    print("🎨 新しいPDFデザインのテスト")
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
                self.transportation_allowance = 15000
                self.position_allowance = 0
                self.other_allowance = 5000
                self.gross_salary = 297966
                self.health_insurance = 14748
                self.pension_insurance = 27243
                self.employment_insurance = 894
                self.long_term_care_insurance = 0
                self.income_tax = 8000
                self.resident_tax = 12000
                self.other_deduction = 2000
                self.total_deduction = 64885
                self.net_salary = 233081
                
                # 勤怠情報
                self.working_days = 22
                self.absence_days = 0
                self.paid_leave_days = 1
                
                self.remarks = "新しいテーブルデザインのテスト用給与明細書"
                self.issued_at = datetime.now()
        
        class MockEmployee:
            def __init__(self):
                self.name = "月曜起算テスト太郎"
                self.id = 4
        
        class MockPayrollCalculation:
            def __init__(self):
                self.regular_working_minutes = 10080  # 168時間
                self.overtime_minutes = 2400  # 40時間
        
        # PDF生成テスト
        print("1️⃣ 新しいテーブルデザインPDF生成開始")
        slip = MockPayrollSlip()
        employee = MockEmployee()
        calculation = MockPayrollCalculation()
        
        pdf_buffer = create_payroll_slip_pdf(slip, employee, calculation)
        
        if pdf_buffer:
            pdf_size = len(pdf_buffer.getvalue())
            print(f"✅ 新デザインPDF生成成功: {pdf_size} bytes")
            
            # テスト用にファイル保存
            with open('test_new_design_payroll.pdf', 'wb') as f:
                f.write(pdf_buffer.getvalue())
            print("✅ 新デザインPDFファイル 'test_new_design_payroll.pdf' を保存しました")
            
            print("\n📋 新デザインの特徴:")
            print("  • テーブル形式のレイアウト")
            print("  • 項目別の整理された表示")
            print("  • 差引支給額のハイライト表示")
            print("  • 勤怠情報の統合表示")
            
            return True
        else:
            print("❌ PDF生成失敗: バッファが空です")
            return False
            
    except Exception as e:
        print(f"❌ PDF生成エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    success = test_new_pdf_design()
    
    print(f"\n" + "=" * 50)
    if success:
        print("✅ 新しいPDFデザインのテストが成功しました")
        print("   実際のWebアプリケーションでも確認してください")
    else:
        print("❌ 新しいPDFデザインに問題があります")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
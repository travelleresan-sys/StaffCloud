#!/usr/bin/env python3
"""
日本標準給与明細書フォーマットテスト
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from payroll_slip_pdf_generator import create_payroll_slip_pdf
from datetime import datetime

def test_standard_payroll_format():
    """日本標準給与明細書フォーマットテスト"""
    print("📋 日本標準給与明細書フォーマットテスト")
    print("=" * 50)
    
    try:
        # モックデータを作成（リアルな日本企業の数値）
        class MockPayrollSlip:
            def __init__(self):
                self.slip_year = 2025
                self.slip_month = 4
                # 支給項目
                self.base_salary = 280000  # 基本給
                self.overtime_allowance = 43750  # 時間外手当（25時間×1750円）
                self.holiday_allowance = 0  # 休日出勤手当
                self.night_allowance = 0  # 深夜手当
                self.transportation_allowance = 12000  # 交通費
                self.position_allowance = 0  # 役職手当
                self.other_allowance = 5000  # その他手当
                self.gross_salary = 340750  # 支給合計
                
                # 控除項目
                self.health_insurance = 16906  # 健康保険料
                self.pension_insurance = 31110  # 厚生年金保険料
                self.employment_insurance = 1022  # 雇用保険料
                self.long_term_care_insurance = 0  # 介護保険料
                self.income_tax = 8640  # 所得税
                self.resident_tax = 15000  # 住民税
                self.other_deduction = 2000  # その他控除
                self.total_deduction = 74678  # 控除合計
                
                self.net_salary = 266072  # 差引支給額
                
                # 勤怠情報
                self.working_days = 20  # 出勤日数
                self.absence_days = 0  # 欠勤日数
                self.paid_leave_days = 1  # 有給取得日数
                
                self.remarks = "日本標準フォーマットに準拠した給与明細書"
                self.issued_at = datetime.now()
        
        class MockEmployee:
            def __init__(self):
                self.name = "田中 太郎"
                self.id = 1001
        
        class MockPayrollCalculation:
            def __init__(self):
                self.regular_working_minutes = 9600  # 160時間（8時間×20日）
                self.overtime_minutes = 1500  # 25時間
        
        # PDF生成テスト
        print("1️⃣ 日本標準フォーマットPDF生成開始")
        slip = MockPayrollSlip()
        employee = MockEmployee()
        calculation = MockPayrollCalculation()
        
        pdf_buffer = create_payroll_slip_pdf(slip, employee, calculation)
        
        if pdf_buffer:
            pdf_size = len(pdf_buffer.getvalue())
            print(f"✅ 日本標準フォーマットPDF生成成功: {pdf_size} bytes")
            
            # テスト用にファイル保存
            with open('standard_format_payroll.pdf', 'wb') as f:
                f.write(pdf_buffer.getvalue())
            print("✅ 標準フォーマットPDFファイル 'standard_format_payroll.pdf' を保存しました")
            
            print("\\n📋 日本標準フォーマットの特徴:")
            print("  • 会社名とタイトルの明確な表示")
            print("  • 勤怠情報セクション（2列構成）")
            print("  • 支給・控除・その他の3列構成")
            print("  • 差引支給額の強調表示")
            print("  • 日本の給与明細書の一般的なレイアウト")
            
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
    success = test_standard_payroll_format()
    
    print(f"\\n" + "=" * 50)
    if success:
        print("✅ 日本標準給与明細書フォーマットテストが成功しました")
        print("   実際のWebアプリケーションでも確認してください")
    else:
        print("❌ 日本標準給与明細書フォーマットに問題があります")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
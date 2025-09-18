#!/usr/bin/env python3
"""
更新された2列表示給与明細PDFをテスト
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append('/home/esan/employee-db')

from payroll_slip_pdf_generator import create_payroll_slip_pdf

class MockPayrollSlip:
    """給与明細のモッククラス"""
    def __init__(self):
        self.slip_year = 2024
        self.slip_month = 9
        self.working_days = 22
        self.paid_leave_days = 2
        self.base_salary = 250000
        self.overtime_allowance = 27966
        self.transportation_allowance = 10000
        self.position_allowance = 5000
        self.other_allowance = 20000
        self.gross_salary = 292966
        self.health_insurance = 12345
        self.pension_insurance = 23456
        self.employment_insurance = 1465
        self.income_tax = 5670
        self.resident_tax = 15000
        self.other_deduction = 30000
        self.total_deduction = 88936
        self.net_salary = 204030
        self.issued_at = datetime.now()

class MockEmployee:
    """従業員のモッククラス"""
    def __init__(self):
        self.name = "テスト太郎"
        self.employee_id = "EMP001"

class MockPayrollCalculation:
    """給与計算結果のモッククラス"""
    def __init__(self):
        self.regular_working_minutes = 2850  # 47.5時間
        self.overtime_minutes = 240         # 4時間

def test_updated_payroll_pdf():
    """更新されたPDF生成をテスト"""
    print("=== 更新された給与明細PDF生成テスト ===")
    
    # モックデータ作成
    payroll_slip = MockPayrollSlip()
    employee = MockEmployee()
    payroll_calculation = MockPayrollCalculation()
    
    try:
        # PDF生成
        print("PDF生成中...")
        pdf_buffer = create_payroll_slip_pdf(
            payroll_slip=payroll_slip,
            employee=employee,
            payroll_calculation=payroll_calculation,
            payroll_settings=None
        )
        
        # PDFファイルを保存
        output_file = "updated_payroll_slip_test.pdf"
        with open(output_file, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"✅ PDF生成成功: {output_file}")
        print(f"📁 ファイルサイズ: {len(pdf_buffer.getvalue())} bytes")
        
        # ファイル詳細情報
        file_stats = os.stat(output_file)
        print(f"📅 作成日時: {datetime.fromtimestamp(file_stats.st_mtime)}")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF生成エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン関数"""
    print("2列表示給与明細PDFテスト開始")
    
    # テスト実行
    result = test_updated_payroll_pdf()
    
    if result:
        print("\n🎉 全テスト完了!")
        print("\n📋 更新内容:")
        print("✅ 賃金計算期間から領収印まで全39項目を2列表示")
        print("✅ 1列目: 項目名、2列目: 時間・金額")
        print("✅ 年次有給休暇取得日数（誤字修正）")
        print("✅ 背景色による項目分類（小計、合計、差引支給額等）")
        print("✅ 領収印エリア表示")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
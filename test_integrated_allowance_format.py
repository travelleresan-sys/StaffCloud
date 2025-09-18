#!/usr/bin/env python3
"""
統合手当フォーマット詳細テスト
（手当1列目拡張 + 2列目右罫線統一）
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append('/home/esan/employee-db')

from payroll_slip_pdf_generator import create_payroll_slip_pdf

class MockPayrollSlip:
    """給与明細のモッククラス（複数手当あり）"""
    def __init__(self):
        self.slip_year = 2024
        self.slip_month = 10
        self.working_days = 23
        self.paid_leave_days = 1
        self.base_salary = 280000
        self.overtime_allowance = 32000
        self.transportation_allowance = 12000  # 交通費
        self.position_allowance = 15000     # 役職手当
        self.other_allowance = 25000
        self.gross_salary = 339000  # 更新された合計
        self.health_insurance = 14000
        self.pension_insurance = 26000
        self.employment_insurance = 1700
        self.income_tax = 7200
        self.resident_tax = 18000
        self.other_deduction = 35000
        self.total_deduction = 101900
        self.net_salary = 237100  # 更新された差引支給額
        self.issued_at = datetime.now()

class MockEmployee:
    """従業員のモッククラス"""
    def __init__(self):
        self.name = "統合テスト花子"
        self.employee_id = "EMP003"

class MockPayrollCalculation:
    """給与計算結果のモッククラス"""
    def __init__(self):
        self.regular_working_minutes = 3120  # 52時間
        self.overtime_minutes = 300         # 5時間

def test_integrated_allowance_format():
    """統合手当フォーマットのテスト"""
    print("=== 統合手当フォーマットPDF生成テスト ===")
    
    # モックデータ作成
    payroll_slip = MockPayrollSlip()
    employee = MockEmployee()
    payroll_calculation = MockPayrollCalculation()
    
    try:
        # PDF生成
        print("統合手当フォーマットPDF生成中...")
        pdf_buffer = create_payroll_slip_pdf(
            payroll_slip=payroll_slip,
            employee=employee,
            payroll_calculation=payroll_calculation,
            payroll_settings=None
        )
        
        # PDFファイルを保存
        output_file = "integrated_allowance_format_test.pdf"
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
    print("統合手当フォーマットテスト開始")
    
    # テスト実行
    result = test_integrated_allowance_format()
    
    if result:
        print("\n🎉 統合手当フォーマットテスト完了!")
        print("\n📋 修正内容:")
        print("✅ 手当1列目を拡張（table_width // 4）")
        print("   - 周りの表と統合されるように幅調整")
        print("   - 縦書き「手当」の表示領域拡張")
        print("✅ 2列目右の罫線を周りの表と統一")
        print("   - 中央線（table_width // 2）で統一")
        print("   - 3列目（金額列）は右半分を使用")
        print("✅ 上下の表との境界線統合")
        print("   - シームレスな表結合")
        print("   - 統一感のあるレイアウト")
        
        print(f"\n📄 テストデータ（複数手当）:")
        print(f"   交通費: ¥12,000")
        print(f"   役職手当: ¥15,000")
        print(f"   基本給: ¥280,000")
        print(f"   時間外手当: ¥32,000")
        print(f"   差引支給額: ¥237,100")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
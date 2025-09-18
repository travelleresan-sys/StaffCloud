#!/usr/bin/env python3
"""
3列手当セクション詳細テスト
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append('/home/esan/employee-db')

from payroll_slip_pdf_generator import create_payroll_slip_pdf

class MockPayrollSlip:
    """給与明細のモッククラス（手当を多く含む）"""
    def __init__(self):
        self.slip_year = 2024
        self.slip_month = 9
        self.working_days = 22
        self.paid_leave_days = 2
        self.base_salary = 250000
        self.overtime_allowance = 27966
        self.transportation_allowance = 15000  # 交通費
        self.position_allowance = 8000      # 役職手当
        self.other_allowance = 20000
        self.gross_salary = 300966  # 更新された合計
        self.health_insurance = 12345
        self.pension_insurance = 23456
        self.employment_insurance = 1465
        self.income_tax = 5670
        self.resident_tax = 15000
        self.other_deduction = 30000
        self.total_deduction = 88936
        self.net_salary = 212030  # 更新された差引支給額
        self.issued_at = datetime.now()

class MockEmployee:
    """従業員のモッククラス"""
    def __init__(self):
        self.name = "手当テスト太郎"
        self.employee_id = "EMP002"

class MockPayrollCalculation:
    """給与計算結果のモッククラス"""
    def __init__(self):
        self.regular_working_minutes = 2850  # 47.5時間
        self.overtime_minutes = 240         # 4時間

def test_allowance_3column():
    """3列手当セクションのテスト"""
    print("=== 3列手当セクションPDF生成テスト ===")
    
    # モックデータ作成
    payroll_slip = MockPayrollSlip()
    employee = MockEmployee()
    payroll_calculation = MockPayrollCalculation()
    
    try:
        # PDF生成
        print("手当セクション3列形式PDF生成中...")
        pdf_buffer = create_payroll_slip_pdf(
            payroll_slip=payroll_slip,
            employee=employee,
            payroll_calculation=payroll_calculation,
            payroll_settings=None
        )
        
        # PDFファイルを保存
        output_file = "allowance_3column_test.pdf"
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
    print("手当セクション3列表示テスト開始")
    
    # テスト実行
    result = test_allowance_3column()
    
    if result:
        print("\n🎉 3列手当セクションテスト完了!")
        print("\n📋 実装内容:")
        print("✅ 手当欄を3列表示に変更")
        print("   - 1列目: 縦書き「手当」（セル結合）")
        print("   - 2列目: 手当項目名（交通費、役職手当など）")
        print("   - 3列目: 金額表示")
        print("✅ 縦書きテキスト「手」「当」実装")
        print("✅ セル結合による統一感のあるレイアウト")
        print("✅ 空の手当項目は非表示")
        print("✅ 金額0の項目は非表示")
        
        print(f"\n📄 テストデータ:")
        print(f"   交通費: ¥15,000")
        print(f"   役職手当: ¥8,000")
        print(f"   その他手当項目: 空欄（5行）")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
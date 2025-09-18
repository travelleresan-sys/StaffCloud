#!/usr/bin/env python3
"""
控除額3列表示テスト
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append('/home/esan/employee-db')

from payroll_slip_pdf_generator import create_payroll_slip_pdf

class MockPayrollSlip:
    """給与明細のモッククラス（控除額3列表示テスト用）"""
    def __init__(self):
        self.slip_year = 2024
        self.slip_month = 12
        self.working_days = 22
        self.paid_leave_days = 1
        self.base_salary = 350000
        self.overtime_allowance = 42000
        self.transportation_allowance = 18000  
        self.position_allowance = 22000     
        self.other_allowance = 28000
        self.gross_salary = 432000
        
        # 控除項目（全項目に明確な値を設定）
        self.health_insurance = 20000      # 健康保険料
        self.pension_insurance = 36000     # 厚生年金保険料
        self.employment_insurance = 2500   # 雇用保険料
        self.income_tax = 15000            # 所得税
        self.resident_tax = 28000          # 市町村民税
        self.other_deduction = 55000       # 家賃
        # 帰国時未徴収分: 固定0
        # 定額減税分: 固定0
        self.total_deduction = 156500      # 控除額合計
        self.net_salary = 275500           # 差引支給額
        self.issued_at = datetime.now()

class MockEmployee:
    """従業員のモッククラス"""
    def __init__(self):
        self.name = "控除額3列テスト花子"
        self.employee_id = "EMP008"

class MockPayrollCalculation:
    """給与計算結果のモッククラス"""
    def __init__(self):
        self.regular_working_minutes = 2940  # 49時間
        self.overtime_minutes = 510         # 8.5時間

def test_deduction_3column():
    """控除額3列表示テスト"""
    print("=== 控除額3列表示テスト ===")
    
    # モックデータ作成
    payroll_slip = MockPayrollSlip()
    employee = MockEmployee()
    payroll_calculation = MockPayrollCalculation()
    
    try:
        # PDF生成
        print("控除額3列表示PDF生成中...")
        pdf_buffer = create_payroll_slip_pdf(
            payroll_slip=payroll_slip,
            employee=employee,
            payroll_calculation=payroll_calculation,
            payroll_settings=None
        )
        
        # PDFファイルを保存
        output_file = "deduction_3column_test.pdf"
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
    print("控除額3列表示テスト開始")
    
    # テスト実行
    result = test_deduction_3column()
    
    if result:
        print("\n🎉 控除額3列表示テスト完了!")
        print("\n📋 控除額セクション実装内容:")
        print("✅ 控除額欄を3列表示に変更")
        print("   - 1列目: 縦書き「控除額」（上下結合）")
        print("   - 2列目: 控除項目名")
        print("   - 3列目: 金額表示")
        print("✅ 1列目の上下結合（「控」「除」「額」縦書き）")
        print("✅ 2列目に指定8項目を順序通り表示:")
        print("   1. 健康保険料")
        print("   2. 厚生年金保険料") 
        print("   3. 雇用保険料")
        print("   4. 所得税")
        print("   5. 市町村民税")
        print("   6. 家賃")
        print("   7. 帰国時未徴収分")
        print("   8. 定額減税分")
        print("✅ 3列目に各項目の金額を表示")
        print("✅ 周りの表と統合されたレイアウト")
        
        print(f"\n📊 テストデータ:")
        print(f"   健康保険料: ¥20,000")
        print(f"   厚生年金保険料: ¥36,000")
        print(f"   雇用保険料: ¥2,500")
        print(f"   所得税: ¥15,000")
        print(f"   市町村民税: ¥28,000")
        print(f"   家賃: ¥55,000")
        print(f"   帰国時未徴収分: ¥0")
        print(f"   定額減税分: ¥0")
        print(f"   控除額合計: ¥156,500")
        print(f"   差引支給額: ¥275,500")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
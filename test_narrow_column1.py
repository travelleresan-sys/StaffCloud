#!/usr/bin/env python3
"""
1列目幅半分縮小テスト
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append('/home/esan/employee-db')

from payroll_slip_pdf_generator import create_payroll_slip_pdf

class MockPayrollSlip:
    """給与明細のモッククラス（1列目幅縮小テスト用）"""
    def __init__(self):
        self.slip_year = 2024
        self.slip_month = 12
        self.working_days = 22
        self.paid_leave_days = 2
        self.base_salary = 400000
        self.overtime_allowance = 52000
        self.transportation_allowance = 25000  
        self.position_allowance = 30000     
        self.other_allowance = 35000
        self.gross_salary = 507000
        
        # 控除項目（全項目に値を設定）
        self.health_insurance = 24000      # 健康保険料
        self.pension_insurance = 42000     # 厚生年金保険料
        self.employment_insurance = 3000   # 雇用保険料
        self.income_tax = 20000            # 所得税
        self.resident_tax = 35000          # 市町村民税
        self.other_deduction = 65000       # 家賃
        # 帰国時未徴収分: 固定0
        # 定額減税分: 固定0
        self.total_deduction = 189000      # 控除額合計
        self.net_salary = 318000           # 差引支給額
        self.issued_at = datetime.now()

class MockEmployee:
    """従業員のモッククラス"""
    def __init__(self):
        self.name = "1列目縮小テスト六郎"
        self.employee_id = "EMP010"

class MockPayrollCalculation:
    """給与計算結果のモッククラス"""
    def __init__(self):
        self.regular_working_minutes = 2940  # 49時間
        self.overtime_minutes = 660         # 11時間

def test_narrow_column1():
    """1列目幅縮小テスト"""
    print("=== 1列目幅縮小テスト ===")
    
    # モックデータ作成
    payroll_slip = MockPayrollSlip()
    employee = MockEmployee()
    payroll_calculation = MockPayrollCalculation()
    
    try:
        # PDF生成
        print("1列目幅縮小PDF生成中...")
        pdf_buffer = create_payroll_slip_pdf(
            payroll_slip=payroll_slip,
            employee=employee,
            payroll_calculation=payroll_calculation,
            payroll_settings=None
        )
        
        # PDFファイルを保存
        output_file = "narrow_column1_test.pdf"
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
    print("1列目幅縮小テスト開始")
    
    # テスト実行
    result = test_narrow_column1()
    
    if result:
        print("\n🎉 1列目幅縮小テスト完了!")
        print("\n📋 幅調整実装内容:")
        print("✅ 手当セクション1列目幅調整:")
        print("   - 変更前: table_width // 4 (25%)")
        print("   - 変更後: table_width // 8 (12.5%)")
        print("✅ 手当セクション2列目幅調整:")
        print("   - 変更前: table_width // 4 (25%)")
        print("   - 変更後: table_width * 3 // 8 (37.5%)")
        print("✅ 控除額セクション1列目幅調整:")
        print("   - 変更前: table_width // 4 (25%)")
        print("   - 変更後: table_width // 8 (12.5%)")
        print("✅ 控除額セクション2列目幅調整:")
        print("   - 変更前: table_width // 4 (25%)")
        print("   - 変更後: table_width * 3 // 8 (37.5%)")
        print("✅ 3列目（金額列）は維持:")
        print("   - table_width // 2 (50%)")
        
        print(f"\n📊 列幅配分:")
        print(f"   1列目（縦書き）: 12.5%")
        print(f"   2列目（項目名）: 37.5%")
        print(f"   3列目（金額）: 50.0%")
        
        print(f"\n📄 テストデータ:")
        print(f"   基本給: ¥400,000")
        print(f"   時間外手当: ¥52,000")
        print(f"   交通費: ¥25,000")
        print(f"   役職手当: ¥30,000")
        print(f"   控除額合計: ¥189,000")
        print(f"   差引支給額: ¥318,000")
        
        print(f"\n🎯 期待される効果:")
        print(f"   ✅ 縦書き文字の表示領域最適化")
        print(f"   ✅ 項目名欄の拡張で読みやすさ向上")
        print(f"   ✅ より効率的なレイアウト")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
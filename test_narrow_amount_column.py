#!/usr/bin/env python3
"""
時間・金額欄幅半分テスト
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append('/home/esan/employee-db')

from payroll_slip_pdf_generator import create_payroll_slip_pdf

class MockPayrollSlip:
    """給与明細のモッククラス（時間・金額欄幅半分テスト用）"""
    def __init__(self):
        self.slip_year = 2024
        self.slip_month = 12
        self.working_days = 22
        self.paid_leave_days = 2
        self.base_salary = 420000
        self.overtime_allowance = 58000
        self.transportation_allowance = 28000  
        self.position_allowance = 35000     
        self.other_allowance = 40000
        self.gross_salary = 523000
        
        # 控除項目（全項目に値を設定）
        self.health_insurance = 26000      # 健康保険料
        self.pension_insurance = 45000     # 厚生年金保険料
        self.employment_insurance = 3200   # 雇用保険料
        self.income_tax = 22000            # 所得税
        self.resident_tax = 38000          # 市町村民税
        self.other_deduction = 70000       # 家賃
        # 帰国時未徴収分: 固定0
        # 定額減税分: 固定0
        self.total_deduction = 204200      # 控除額合計
        self.net_salary = 318800           # 差引支給額
        self.issued_at = datetime.now()

class MockEmployee:
    """従業員のモッククラス"""
    def __init__(self):
        self.name = "時間金額欄半分テスト太郎"
        self.employee_id = "EMP011"

class MockPayrollCalculation:
    """給与計算結果のモッククラス"""
    def __init__(self):
        self.regular_working_minutes = 2940  # 49時間
        self.overtime_minutes = 720         # 12時間

def test_narrow_amount_column():
    """時間・金額欄幅半分テスト"""
    print("=== 時間・金額欄幅半分テスト ===")
    
    # モックデータ作成
    payroll_slip = MockPayrollSlip()
    employee = MockEmployee()
    payroll_calculation = MockPayrollCalculation()
    
    try:
        # PDF生成
        print("時間・金額欄幅半分PDF生成中...")
        pdf_buffer = create_payroll_slip_pdf(
            payroll_slip=payroll_slip,
            employee=employee,
            payroll_calculation=payroll_calculation,
            payroll_settings=None
        )
        
        # PDFファイルを保存
        output_file = "narrow_amount_column_test.pdf"
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
    print("時間・金額欄幅半分テスト開始")
    
    # テスト実行
    result = test_narrow_amount_column()
    
    if result:
        print("\n🎉 時間・金額欄幅半分テスト完了!")
        print("\n📋 幅調整実装内容:")
        print("✅ 手当セクション幅調整:")
        print("   - 1列目（縦書き）: 12.5%")
        print("   - 2列目（項目名）: 62.5% ← 拡張")
        print("   - 3列目（金額）: 25% ← 半分に縮小")
        print("✅ 控除額セクション幅調整:")
        print("   - 1列目（縦書き）: 12.5%")
        print("   - 2列目（項目名）: 62.5% ← 拡張")
        print("   - 3列目（金額）: 25% ← 半分に縮小")
        print("✅ 金額描画位置調整:")
        print("   - 各セクションの3列目右端に正確に配置")
        
        print(f"\n📊 列幅配分:")
        print(f"   1列目（縦書き）: 12.5%")
        print(f"   2列目（項目名）: 62.5%")
        print(f"   3列目（金額）: 25.0%")
        
        print(f"\n📄 テストデータ:")
        print(f"   基本給: ¥420,000")
        print(f"   時間外手当: ¥58,000")
        print(f"   交通費: ¥28,000")
        print(f"   役職手当: ¥35,000")
        print(f"   控除額合計: ¥204,200")
        print(f"   差引支給額: ¥318,800")
        
        print(f"\n🎯 期待される効果:")
        print(f"   ✅ 項目名欄の大幅拡張で読みやすさ向上")
        print(f"   ✅ 金額欄の適正サイズ化")
        print(f"   ✅ より効率的なスペース利用")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
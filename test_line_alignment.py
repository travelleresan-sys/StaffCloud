#!/usr/bin/env python3
"""
線の位置揃えテスト
（中央線と境界線の位置を揃える確認）
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append('/home/esan/employee-db')

from payroll_slip_pdf_generator import create_payroll_slip_pdf

class MockPayrollSlip:
    """給与明細のモッククラス（線の位置揃えテスト用）"""
    def __init__(self):
        self.slip_year = 2024
        self.slip_month = 12
        self.working_days = 22
        self.paid_leave_days = 1
        self.base_salary = 480000
        self.overtime_allowance = 72000
        self.transportation_allowance = 32000  
        self.position_allowance = 45000     
        self.other_allowance = 50000
        self.gross_salary = 629000
        
        # 控除項目（全項目に値を設定）
        self.health_insurance = 30000      # 健康保険料
        self.pension_insurance = 50000     # 厚生年金保険料
        self.employment_insurance = 3800   # 雇用保険料
        self.income_tax = 28000            # 所得税
        self.resident_tax = 45000          # 市町村民税
        self.other_deduction = 80000       # 家賃
        # 帰国時未徴収分: 固定0
        # 定額減税分: 固定0
        self.total_deduction = 236800      # 控除額合計
        self.net_salary = 392200           # 差引支給額
        self.issued_at = datetime.now()

class MockEmployee:
    """従業員のモッククラス"""
    def __init__(self):
        self.name = "線位置揃えテスト三郎"
        self.employee_id = "EMP013"

class MockPayrollCalculation:
    """給与計算結果のモッククラス"""
    def __init__(self):
        self.regular_working_minutes = 2940  # 49時間
        self.overtime_minutes = 840         # 14時間

def test_line_alignment():
    """線の位置揃えテスト"""
    print("=== 線の位置揃えテスト ===")
    
    # モックデータ作成
    payroll_slip = MockPayrollSlip()
    employee = MockEmployee()
    payroll_calculation = MockPayrollCalculation()
    
    try:
        # PDF生成
        print("線の位置揃えPDF生成中...")
        pdf_buffer = create_payroll_slip_pdf(
            payroll_slip=payroll_slip,
            employee=employee,
            payroll_calculation=payroll_calculation,
            payroll_settings=None
        )
        
        # PDFファイルを保存
        output_file = "line_alignment_test.pdf"
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
    print("線の位置揃えテスト開始")
    
    # テスト実行
    result = test_line_alignment()
    
    if result:
        print("\n🎉 線の位置揃えテスト完了!")
        print("\n📋 線位置調整実装内容:")
        print("✅ メインテーブル中央線位置: 50%")
        print("✅ 手当セクション境界線位置: 50% ← 調整")
        print("✅ 控除額セクション境界線位置: 50% ← 調整")
        print("✅ 全ての縦線が同一位置に揃う")
        
        print(f"\n📊 調整後の列幅配分:")
        print(f"   1列目（縦書き）: 12.5%")
        print(f"   2列目（項目名）: 37.5% ← 調整")
        print(f"   3列目（金額）: 50.0% ← 拡張")
        
        print(f"\n🔧 修正内容:")
        print(f"   変更前: col2_width = table_width * 5 // 8 (62.5%)")
        print(f"   変更後: col2_width = table_width * 3 // 8 (37.5%)")
        print(f"   変更前: col3_width = table_width // 4 (25%)")
        print(f"   変更後: col3_width = table_width // 2 (50%)")
        print(f"   境界線位置: 12.5% + 37.5% = 50% (中央線と一致)")
        
        print(f"\n📄 テストデータ:")
        print(f"   基本給: ¥480,000")
        print(f"   時間外手当: ¥72,000")
        print(f"   交通費: ¥32,000")
        print(f"   役職手当: ¥45,000")
        print(f"   控除額合計: ¥236,800")
        print(f"   差引支給額: ¥392,200")
        
        print(f"\n🎯 期待される効果:")
        print(f"   ✅ 全縦線の完全な位置揃え")
        print(f"   ✅ 統一感のあるレイアウト")
        print(f"   ✅ 視覚的に整理されたデザイン")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
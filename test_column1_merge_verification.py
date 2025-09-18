#!/usr/bin/env python3
"""
1列目結合検証詳細テスト
（手当欄1列目の上下結合確認）
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append('/home/esan/employee-db')

from payroll_slip_pdf_generator import create_payroll_slip_pdf

class MockPayrollSlip:
    """給与明細のモッククラス（多数の手当で結合確認）"""
    def __init__(self):
        self.slip_year = 2024
        self.slip_month = 11
        self.working_days = 21
        self.paid_leave_days = 3
        self.base_salary = 300000
        self.overtime_allowance = 40000
        self.transportation_allowance = 18000  # 交通費
        self.position_allowance = 25000     # 役職手当
        self.other_allowance = 30000
        self.gross_salary = 383000
        self.health_insurance = 16000
        self.pension_insurance = 30000
        self.employment_insurance = 1900
        self.income_tax = 9500
        self.resident_tax = 22000
        self.other_deduction = 40000
        self.total_deduction = 119400
        self.net_salary = 263600
        self.issued_at = datetime.now()

class MockEmployee:
    """従業員のモッククラス"""
    def __init__(self):
        self.name = "結合確認次郎"
        self.employee_id = "EMP004"

class MockPayrollCalculation:
    """給与計算結果のモッククラス"""
    def __init__(self):
        self.regular_working_minutes = 2940  # 49時間
        self.overtime_minutes = 420         # 7時間

def test_column1_merge_verification():
    """1列目結合検証テスト"""
    print("=== 1列目結合検証PDF生成テスト ===")
    
    # モックデータ作成
    payroll_slip = MockPayrollSlip()
    employee = MockEmployee()
    payroll_calculation = MockPayrollCalculation()
    
    try:
        # PDF生成
        print("1列目結合検証PDF生成中...")
        pdf_buffer = create_payroll_slip_pdf(
            payroll_slip=payroll_slip,
            employee=employee,
            payroll_calculation=payroll_calculation,
            payroll_settings=None
        )
        
        # PDFファイルを保存
        output_file = "column1_merge_verification_test.pdf"
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
    print("1列目結合検証テスト開始")
    
    # テスト実行
    result = test_column1_merge_verification()
    
    if result:
        print("\n🎉 1列目結合検証テスト完了!")
        print("\n📋 1列目結合修正内容:")
        print("✅ 1列目の横線を削除")
        print("   - 手当セクション全体を1つの矩形で描画")
        print("   - 1列目の右境界線のみ描画")
        print("   - 2列目・3列目のみに横線を描画")
        print("✅ 縦書き「手当」が1列目全体に表示")
        print("   - セクション中央に「手」「当」配置")
        print("   - 上下結合されたセル内に統一表示")
        print("✅ 2列目・3列目は通常の行分割")
        print("   - 各手当項目ごとに行分割")
        print("   - 項目名と金額の個別表示")
        
        print(f"\n📄 検証データ:")
        print(f"   手当項目数: 7行（2行に実データ、5行空欄）")
        print(f"   交通費: ¥18,000")
        print(f"   役職手当: ¥25,000")
        print(f"   1列目: 上下結合された単一セル")
        print(f"   2・3列目: 7行に分割されたセル")
        
        print(f"\n🔍 視覚確認ポイント:")
        print(f"   - 1列目に横線が表示されないこと")
        print(f"   - 2・3列目には横線が表示されること")
        print(f"   - 縦書き「手当」が1列目中央に表示されること")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
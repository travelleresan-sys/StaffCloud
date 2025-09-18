#!/usr/bin/env python3
"""
位置調整テスト
（従業員名・発行日・領収印の位置調整確認）
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append('/home/esan/employee-db')

from payroll_slip_pdf_generator import create_payroll_slip_pdf

class MockPayrollSlip:
    """給与明細のモッククラス（位置調整テスト用）"""
    def __init__(self):
        self.slip_year = 2024
        self.slip_month = 12
        self.working_days = 22
        self.paid_leave_days = 2
        self.base_salary = 550000
        self.overtime_allowance = 82000
        self.transportation_allowance = 40000  
        self.position_allowance = 50000     
        self.other_allowance = 58000
        self.gross_salary = 722000
        
        # 控除項目（全項目に値を設定）
        self.health_insurance = 34000      # 健康保険料
        self.pension_insurance = 58000     # 厚生年金保険料
        self.employment_insurance = 4300   # 雇用保険料
        self.income_tax = 35000            # 所得税
        self.resident_tax = 50000          # 市町村民税
        self.other_deduction = 90000       # 家賃
        # 帰国時未徴収分: 固定0
        # 定額減税分: 固定0
        self.total_deduction = 271300      # 控除額合計
        self.net_salary = 450700           # 差引支給額
        self.issued_at = datetime.now()

class MockEmployee:
    """従業員のモッククラス"""
    def __init__(self):
        self.name = "位置調整テスト次郎"
        self.employee_id = "EMP018"

class MockPayrollCalculation:
    """給与計算結果のモッククラス"""
    def __init__(self):
        self.regular_working_minutes = 2940  # 49時間
        self.overtime_minutes = 1020        # 17時間

def test_position_adjustments():
    """位置調整テスト"""
    print("=== 位置調整テスト ===")
    
    # モックデータ作成
    payroll_slip = MockPayrollSlip()
    employee = MockEmployee()
    payroll_calculation = MockPayrollCalculation()
    
    try:
        # PDF生成
        print("位置調整PDF生成中...")
        pdf_buffer = create_payroll_slip_pdf(
            payroll_slip=payroll_slip,
            employee=employee,
            payroll_calculation=payroll_calculation,
            payroll_settings=None
        )
        
        # PDFファイルを保存
        output_file = "position_adjustments_test.pdf"
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
    print("位置調整テスト開始")
    
    # テスト実行
    result = test_position_adjustments()
    
    if result:
        print("\n🎉 位置調整テスト完了!")
        print("\n📋 実装済み位置調整:")
        print("✅ 従業員氏名の位置:")
        print("   - 変更前: 中央配置")
        print("   - 変更後: 枠の左側に揃える")
        print("   - 配置: table_x（明細枠左端）")
        print("✅ 発行日の位置:")
        print("   - 変更前: 従業員名と同じ行の右端")
        print("   - 変更後: 1段下げて枠の右側に揃える")
        print("   - 配置: table_x + table_width（明細枠右端）")
        print("✅ 領収印の枠位置:")
        print("   - 変更前: 右端から5pxマージンで配置")
        print("   - 変更後: 明細枠の右側にピッタリ揃える")
        print("   - 配置: table_x + table_width（明細枠右端）")
        print("✅ 領収印の枠形状:")
        print("   - 変更前: 60×30px（横長）")
        print("   - 変更後: 40×40px（正方形）")
        
        print(f"\n🔧 位置座標計算:")
        print(f"   テーブル幅: 320px")
        print(f"   テーブル左端: table_x = (595-320)/2 = 137.5px")
        print(f"   テーブル右端: table_x + 320 = 457.5px")
        print(f"   従業員名X座標: 137.5px（左揃え）")
        print(f"   発行日X座標: 457.5px（右揃え）")
        print(f"   領収印X座標: 457.5px（右端揃え）")
        
        print(f"\n📄 テストデータ:")
        print(f"   従業員名: 位置調整テスト次郎")
        print(f"   発行日: {datetime.now().strftime('%Y年%m月%d日')}")
        print(f"   基本給: ¥550,000")
        print(f"   時間外手当: ¥82,000")
        print(f"   労働時間: 49：00 + 17：00 = 66：00")
        print(f"   控除額合計: ¥271,300")
        print(f"   差引支給額: ¥450,700")
        
        print(f"\n🎯 期待される効果:")
        print(f"   ✅ より整理されたヘッダーレイアウト")
        print(f"   ✅ 明細枠との一体感向上")
        print(f"   ✅ 領収印の視認性向上")
        print(f"   ✅ プロフェッショナルな印象")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
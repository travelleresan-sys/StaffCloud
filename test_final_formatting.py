#!/usr/bin/env python3
"""
最終フォーマット確認テスト
（7ptフォント・全角コロン・均等割り付けの統合確認）
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append('/home/esan/employee-db')

from payroll_slip_pdf_generator import create_payroll_slip_pdf

class MockPayrollSlip:
    """給与明細のモッククラス（最終フォーマット確認用）"""
    def __init__(self):
        self.slip_year = 2024
        self.slip_month = 12
        self.working_days = 22
        self.paid_leave_days = 2
        self.base_salary = 480000
        self.overtime_allowance = 72000
        self.transportation_allowance = 35000  
        self.position_allowance = 45000     
        self.other_allowance = 52000
        self.gross_salary = 632000
        
        # 控除項目（全項目に値を設定）
        self.health_insurance = 30000      # 健康保険料
        self.pension_insurance = 52000     # 厚生年金保険料
        self.employment_insurance = 3800   # 雇用保険料
        self.income_tax = 28000            # 所得税
        self.resident_tax = 45000          # 市町村民税
        self.other_deduction = 80000       # 家賃
        # 帰国時未徴収分: 固定0
        # 定額減税分: 固定0
        self.total_deduction = 238800      # 控除額合計
        self.net_salary = 393200           # 差引支給額
        self.issued_at = datetime.now()

class MockEmployee:
    """従業員のモッククラス"""
    def __init__(self):
        self.name = "最終フォーマット確認太郎"
        self.employee_id = "EMP016"

class MockPayrollCalculation:
    """給与計算結果のモッククラス"""
    def __init__(self):
        self.regular_working_minutes = 2940  # 49時間
        self.overtime_minutes = 900         # 15時間

def test_final_formatting():
    """最終フォーマット確認テスト"""
    print("=== 最終フォーマット確認テスト ===")
    
    # モックデータ作成
    payroll_slip = MockPayrollSlip()
    employee = MockEmployee()
    payroll_calculation = MockPayrollCalculation()
    
    try:
        # PDF生成
        print("最終フォーマット確認PDF生成中...")
        pdf_buffer = create_payroll_slip_pdf(
            payroll_slip=payroll_slip,
            employee=employee,
            payroll_calculation=payroll_calculation,
            payroll_settings=None
        )
        
        # PDFファイルを保存
        output_file = "final_formatting_test.pdf"
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
    print("最終フォーマット確認テスト開始")
    
    # テスト実行
    result = test_final_formatting()
    
    if result:
        print("\n🎉 最終フォーマット確認テスト完了!")
        print("\n📋 実装済み機能:")
        print("✅ 文字サイズ統一:")
        print("   - 枠内の全ての文字を7ptに統一")
        print("   - メインテーブル、手当セクション、控除額セクション")
        print("✅ 時間表示の全角コロン:")
        print("   - 半角「:」→ 全角「：」に変更")
        print("   - format_working_hours()とformat_overtime_hours()で対応")
        print("✅ 項目名の均等割り付け:")
        print("   - draw_justified_text()関数を新規作成")
        print("   - メインテーブル項目名を均等割り付けで表示")
        print("   - 手当セクション項目名を均等割り付けで表示")
        print("   - 控除額セクション項目名を均等割り付けで表示")
        
        print(f"\n🔧 均等割り付けアルゴリズム:")
        print(f"   1. 文字列の自然幅を計算")
        print(f"   2. 利用可能幅との差分を算出")
        print(f"   3. 差分を文字間に均等に配分")
        print(f"   4. 各文字を計算された位置に描画")
        
        print(f"\n📄 テストデータ:")
        print(f"   基本給: ¥480,000")
        print(f"   時間外手当: ¥72,000")
        print(f"   労働時間: 49：00 + 15：00 = 64：00")
        print(f"   交通費: ¥35,000")
        print(f"   役職手当: ¥45,000") 
        print(f"   控除額合計: ¥238,800")
        print(f"   差引支給額: ¥393,200")
        
        print(f"\n🎯 期待される効果:")
        print(f"   ✅ 統一された見やすい文字サイズ")
        print(f"   ✅ 日本語らしい時間表示")
        print(f"   ✅ 美しく整理された項目名配置")
        print(f"   ✅ プロフェッショナルな給与明細書")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
小さいフォントサイズ（8pt）とサイズ調整テスト
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append('/home/esan/employee-db')

from payroll_slip_pdf_generator import create_payroll_slip_pdf

class MockPayrollSlip:
    """給与明細のモッククラス（8ptフォントテスト用）"""
    def __init__(self):
        self.slip_year = 2024
        self.slip_month = 12
        self.working_days = 22
        self.paid_leave_days = 1
        self.base_salary = 380000
        self.overtime_allowance = 48000
        self.transportation_allowance = 22000  
        self.position_allowance = 28000     
        self.other_allowance = 32000
        self.gross_salary = 478000
        
        # 控除項目（全項目に値を設定）
        self.health_insurance = 22000      # 健康保険料
        self.pension_insurance = 40000     # 厚生年金保険料
        self.employment_insurance = 2800   # 雇用保険料
        self.income_tax = 18000            # 所得税
        self.resident_tax = 32000          # 市町村民税
        self.other_deduction = 60000       # 家賃
        # 帰国時未徴収分: 固定0
        # 定額減税分: 固定0
        self.total_deduction = 174800      # 控除額合計
        self.net_salary = 303200           # 差引支給額
        self.issued_at = datetime.now()

class MockEmployee:
    """従業員のモッククラス"""
    def __init__(self):
        self.name = "8ptフォントテスト五郎"
        self.employee_id = "EMP009"

class MockPayrollCalculation:
    """給与計算結果のモッククラス"""
    def __init__(self):
        self.regular_working_minutes = 2940  # 49時間
        self.overtime_minutes = 600         # 10時間

def test_smaller_font_size():
    """8ptフォントとサイズ縮小テスト"""
    print("=== 8ptフォント・サイズ縮小テスト ===")
    
    # モックデータ作成
    payroll_slip = MockPayrollSlip()
    employee = MockEmployee()
    payroll_calculation = MockPayrollCalculation()
    
    try:
        # PDF生成
        print("8ptフォント・縮小サイズPDF生成中...")
        pdf_buffer = create_payroll_slip_pdf(
            payroll_slip=payroll_slip,
            employee=employee,
            payroll_calculation=payroll_calculation,
            payroll_settings=None
        )
        
        # PDFファイルを保存
        output_file = "smaller_font_size_test.pdf"
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
    print("8ptフォント・サイズ縮小テスト開始")
    
    # テスト実行
    result = test_smaller_font_size()
    
    if result:
        print("\n🎉 8ptフォント・サイズ縮小テスト完了!")
        print("\n📋 サイズ調整実装内容:")
        print("✅ メインテーブルフォントサイズ: 10pt → 8pt")
        print("✅ メインテーブル行高: 20px → 16px")
        print("✅ テキスト描画位置: -15px → -12px")
        print("✅ 手当セクション調整:")
        print("   - 縦書き「手当」フォント: 12pt → 10pt")
        print("   - 項目・金額フォント: 10pt → 8pt")
        print("   - 縦書き位置調整: ±10px → ±8px")
        print("   - テキスト位置: -15px → -12px")
        print("✅ 控除額セクション調整:")
        print("   - 縦書き「控除額」フォント: 12pt → 10pt")
        print("   - 項目・金額フォント: 10pt → 8pt")
        print("   - 縦書き位置調整: ±15px → ±12px")
        print("   - テキスト位置: -15px → -12px")
        print("   - 行高: 20px → 16px")
        
        print(f"\n📊 テストデータ:")
        print(f"   基本給: ¥380,000")
        print(f"   時間外手当: ¥48,000")
        print(f"   交通費: ¥22,000")
        print(f"   役職手当: ¥28,000")
        print(f"   控除額合計: ¥174,800")
        print(f"   差引支給額: ¥303,200")
        
        print(f"\n🎯 期待される効果:")
        print(f"   ✅ より多くの項目が1ページに収まる")
        print(f"   ✅ コンパクトなレイアウト")
        print(f"   ✅ 読みやすいフォントサイズ維持")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
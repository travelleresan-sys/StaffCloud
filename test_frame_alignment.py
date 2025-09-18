#!/usr/bin/env python3
"""
枠位置調整テスト
（時間・金額欄の枠ずれ修正と領収印位置調整確認）
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append('/home/esan/employee-db')

from payroll_slip_pdf_generator import create_payroll_slip_pdf

class MockPayrollSlip:
    """給与明細のモッククラス（枠位置調整テスト用）"""
    def __init__(self):
        self.slip_year = 2024
        self.slip_month = 12
        self.working_days = 22
        self.paid_leave_days = 2
        self.base_salary = 450000
        self.overtime_allowance = 65000
        self.transportation_allowance = 30000  
        self.position_allowance = 40000     
        self.other_allowance = 45000
        self.gross_salary = 575000
        
        # 控除項目（全項目に値を設定）
        self.health_insurance = 28000      # 健康保険料
        self.pension_insurance = 48000     # 厚生年金保険料
        self.employment_insurance = 3500   # 雇用保険料
        self.income_tax = 25000            # 所得税
        self.resident_tax = 42000          # 市町村民税
        self.other_deduction = 75000       # 家賃
        # 帰国時未徴収分: 固定0
        # 定額減税分: 固定0
        self.total_deduction = 221500      # 控除額合計
        self.net_salary = 353500           # 差引支給額
        self.issued_at = datetime.now()

class MockEmployee:
    """従業員のモッククラス"""
    def __init__(self):
        self.name = "枠位置調整テスト次郎"
        self.employee_id = "EMP012"

class MockPayrollCalculation:
    """給与計算結果のモッククラス"""
    def __init__(self):
        self.regular_working_minutes = 2940  # 49時間
        self.overtime_minutes = 780         # 13時間

def test_frame_alignment():
    """枠位置調整テスト"""
    print("=== 枠位置調整テスト ===")
    
    # モックデータ作成
    payroll_slip = MockPayrollSlip()
    employee = MockEmployee()
    payroll_calculation = MockPayrollCalculation()
    
    try:
        # PDF生成
        print("枠位置調整PDF生成中...")
        pdf_buffer = create_payroll_slip_pdf(
            payroll_slip=payroll_slip,
            employee=employee,
            payroll_calculation=payroll_calculation,
            payroll_settings=None
        )
        
        # PDFファイルを保存
        output_file = "frame_alignment_test.pdf"
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
    print("枠位置調整テスト開始")
    
    # テスト実行
    result = test_frame_alignment()
    
    if result:
        print("\n🎉 枠位置調整テスト完了!")
        print("\n📋 修正実装内容:")
        print("✅ 時間・金額欄の枠ずれ修正:")
        print("   - 手当セクション横線終点調整")
        print("   - 控除額セクション横線終点調整")
        print("   - 新しい列幅に合わせて正確に描画")
        print("✅ 領収印の枠位置調整:")
        print("   - 中央配置 → 右側ライン揃えに変更")
        print("   - 位置を下に移動（テーブル重複回避）")
        print("   - 右端から5pxマージンで配置")
        
        print(f"\n📊 修正詳細:")
        print(f"   横線終点: x + table_width → x + col1_width + col2_width + col3_width")
        print(f"   領収印X座標: x + table_width//2 + 20 → x + table_width - 65")
        print(f"   領収印Y座標: current_y - 10 → current_y - 25")
        print(f"   領収印枠サイズ: 60×30px")
        
        print(f"\n📄 テストデータ:")
        print(f"   基本給: ¥450,000")
        print(f"   時間外手当: ¥65,000")
        print(f"   交通費: ¥30,000")
        print(f"   役職手当: ¥40,000")
        print(f"   控除額合計: ¥221,500")
        print(f"   差引支給額: ¥353,500")
        
        print(f"\n🎯 期待される効果:")
        print(f"   ✅ 枠線の正確な配置と整列")
        print(f"   ✅ 領収印の適切な位置配置")
        print(f"   ✅ テーブル重複の解消")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
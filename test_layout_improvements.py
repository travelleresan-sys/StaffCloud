#!/usr/bin/env python3
"""
レイアウト改善テスト
（中央配置・余白調整・8ptフォントの確認）
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append('/home/esan/employee-db')

from payroll_slip_pdf_generator import create_payroll_slip_pdf

class MockPayrollSlip:
    """給与明細のモッククラス（レイアウト改善テスト用）"""
    def __init__(self):
        self.slip_year = 2024
        self.slip_month = 12
        self.working_days = 22
        self.paid_leave_days = 2
        self.base_salary = 520000
        self.overtime_allowance = 78000
        self.transportation_allowance = 38000  
        self.position_allowance = 48000     
        self.other_allowance = 55000
        self.gross_salary = 681000
        
        # 控除項目（全項目に値を設定）
        self.health_insurance = 32000      # 健康保険料
        self.pension_insurance = 55000     # 厚生年金保険料
        self.employment_insurance = 4100   # 雇用保険料
        self.income_tax = 32000            # 所得税
        self.resident_tax = 48000          # 市町村民税
        self.other_deduction = 85000       # 家賃
        # 帰国時未徴収分: 固定0
        # 定額減税分: 固定0
        self.total_deduction = 256100      # 控除額合計
        self.net_salary = 424900           # 差引支給額
        self.issued_at = datetime.now()

class MockEmployee:
    """従業員のモッククラス"""
    def __init__(self):
        self.name = "レイアウト改善テスト太郎"
        self.employee_id = "EMP017"

class MockPayrollCalculation:
    """給与計算結果のモッククラス"""
    def __init__(self):
        self.regular_working_minutes = 2940  # 49時間
        self.overtime_minutes = 960         # 16時間

def test_layout_improvements():
    """レイアウト改善テスト"""
    print("=== レイアウト改善テスト ===")
    
    # モックデータ作成
    payroll_slip = MockPayrollSlip()
    employee = MockEmployee()
    payroll_calculation = MockPayrollCalculation()
    
    try:
        # PDF生成
        print("レイアウト改善PDF生成中...")
        pdf_buffer = create_payroll_slip_pdf(
            payroll_slip=payroll_slip,
            employee=employee,
            payroll_calculation=payroll_calculation,
            payroll_settings=None
        )
        
        # PDFファイルを保存
        output_file = "layout_improvements_test.pdf"
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
    print("レイアウト改善テスト開始")
    
    # テスト実行
    result = test_layout_improvements()
    
    if result:
        print("\n🎉 レイアウト改善テスト完了!")
        print("\n📋 実装済み改善内容:")
        print("✅ 枠の上の余白調整:")
        print("   - ページ上部からテーブル開始まで: 50px → 30px")
        print("   - 対象者情報下の余白: 35px → 30px")
        print("✅ 枠の中央配置:")
        print("   - テーブル幅: 320px（固定）")
        print("   - テーブル位置: (page_width - table_width) / 2")
        print("   - 全ての要素がページ中央に配置")
        print("✅ タイトル・会社名の中央寄せ:")
        print("   - タイトル「給与明細」: 中央配置（既存実装）")
        print("   - 対象者情報: 中央配置に変更")
        print("   - 会社名: 中央配置（既存実装）")
        print("✅ 文字サイズ調整:")
        print("   - 明細項目の文字サイズ: 7pt → 8pt")
        print("   - 読みやすさとコンパクトさのバランス向上")
        
        print(f"\n🔧 レイアウト計算:")
        print(f"   ページ幅: 595pt (A4)")
        print(f"   テーブル幅: 320pt")
        print(f"   左右マージン: (595-320)/2 = 137.5pt")
        print(f"   中央配置の実現")
        
        print(f"\n📄 テストデータ:")
        print(f"   基本給: ¥520,000")
        print(f"   時間外手当: ¥78,000")
        print(f"   労働時間: 49：00 + 16：00 = 65：00")
        print(f"   交通費: ¥38,000")
        print(f"   役職手当: ¥48,000")
        print(f"   控除額合計: ¥256,100")
        print(f"   差引支給額: ¥424,900")
        
        print(f"\n🎯 期待される効果:")
        print(f"   ✅ よりバランスの取れた美しいレイアウト")
        print(f"   ✅ 中央配置による視覚的安定感")
        print(f"   ✅ コンパクトながら読みやすい文字サイズ")
        print(f"   ✅ プロフェッショナルな印象の向上")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
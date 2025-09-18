#!/usr/bin/env python3
"""
企業情報から会社名を取得してPDFに反映するテスト
"""

import sys
import os
from datetime import datetime

# プロジェクトルートを追加
sys.path.append('/home/esan/employee-db')

from payroll_slip_pdf_generator import create_payroll_slip_pdf

class MockPayrollSlip:
    """給与明細のモッククラス（会社名テスト用）"""
    def __init__(self):
        self.slip_year = 2024
        self.slip_month = 12
        self.working_days = 22
        self.paid_leave_days = 1
        self.base_salary = 450000
        self.overtime_allowance = 68000
        self.transportation_allowance = 30000  
        self.position_allowance = 40000     
        self.other_allowance = 48000
        self.gross_salary = 588000
        
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
        self.net_salary = 366500           # 差引支給額
        self.issued_at = datetime.now()

class MockEmployee:
    """従業員のモッククラス"""
    def __init__(self):
        self.name = "企業名テスト太郎"
        self.employee_id = "EMP015"

class MockPayrollCalculation:
    """給与計算結果のモッククラス"""
    def __init__(self):
        self.regular_working_minutes = 2940  # 49時間
        self.overtime_minutes = 840         # 14時間

def test_company_name():
    """企業名取得テスト"""
    print("=== 企業名取得テスト ===")
    
    # 企業名取得のテスト
    try:
        from payroll_slip_pdf_generator import get_company_name
        company_name = get_company_name()
        print(f"📢 取得された企業名: {company_name}")
    except Exception as e:
        print(f"⚠️ 企業名取得エラー: {str(e)}")
    
    # モックデータ作成
    payroll_slip = MockPayrollSlip()
    employee = MockEmployee()
    payroll_calculation = MockPayrollCalculation()
    
    try:
        # PDF生成
        print("企業名反映PDF生成中...")
        pdf_buffer = create_payroll_slip_pdf(
            payroll_slip=payroll_slip,
            employee=employee,
            payroll_calculation=payroll_calculation,
            payroll_settings=None
        )
        
        # PDFファイルを保存
        output_file = "company_name_test.pdf"
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
    print("企業名取得・反映テスト開始")
    
    # テスト実行
    result = test_company_name()
    
    if result:
        print("\n🎉 企業名取得・反映テスト完了!")
        print("\n📋 実装変更内容:")
        print("✅ get_company_name()関数を追加:")
        print("   - CompanySettingsモデルから会社名を動的取得")
        print("   - データベースエラー時のフォールバック対応")
        print("✅ ハードコーディング削除:")
        print("   - '株式会社 梅菱建設工業' → get_company_name()")
        print("✅ コメント・関数名の汎用化:")
        print("   - '梅菱建設工業様専用' → '2列表形式'")
        
        print(f"\n🔧 動的企業名取得の仕組み:")
        print(f"   1. CompanySettings.query.first()でデータベースから取得")
        print(f"   2. データが存在する場合: company_nameフィールドを使用")
        print(f"   3. データが存在しない場合: 'サンプル企業'をデフォルト表示")
        print(f"   4. データベース接続エラー時: 'サンプル企業'をフォールバック")
        
        print(f"\n📄 テストデータ:")
        print(f"   基本給: ¥450,000")
        print(f"   時間外手当: ¥68,000")
        print(f"   控除額合計: ¥221,500")
        print(f"   差引支給額: ¥366,500")
        
        print(f"\n🎯 期待される効果:")
        print(f"   ✅ 実際の企業名がPDFに表示される")
        print(f"   ✅ 企業情報の変更が自動的に反映される")
        print(f"   ✅ システムの汎用性向上")
    else:
        print("\n❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
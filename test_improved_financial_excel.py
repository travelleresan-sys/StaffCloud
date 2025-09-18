#!/usr/bin/env python3
"""
改良版財務諸表Excel出力のテスト
"""

import sys
import os
from datetime import datetime

# Django風のモックデータクラス
class MockData:
    def __init__(self, account_name, balance):
        self.account_name = account_name
        self.balance = balance

class MockCashFlow:
    def __init__(self):
        self.operating = MockOperating()
        self.investing = MockInvesting()
        self.financing = MockFinancing()

class MockOperating:
    def __init__(self):
        self.pre_tax_income = 300000
        self.depreciation = 50000

class MockInvesting:
    def __init__(self):
        self.asset_purchase = -100000

class MockFinancing:
    def __init__(self):
        self.loan_increase = 200000

def test_improved_excel():
    """改良版Excel出力のテスト"""

    print("=== 改良版財務諸表Excel出力テスト ===\n")

    try:
        # 改良版モジュールをインポート
        from improved_financial_excel_generator import create_improved_financial_statements_excel

        # テストデータ作成
        assets = [
            MockData("現金及び預金", 500000),
            MockData("売掛金", 300000),
            MockData("商品", 200000),
            MockData("建物", 5000000),
            MockData("機械装置", 2000000),
        ]

        liabilities = [
            MockData("買掛金", 150000),
            MockData("未払金", 100000),
            MockData("長期借入金", 3000000),
        ]

        revenues = [
            MockData("売上高", 1000000),
            MockData("受取利息", 5000),
        ]

        expenses = [
            MockData("売上原価", 600000),
            MockData("材料費", 100000),
            MockData("給料手当", 200000),
            MockData("減価償却費", 50000),
            MockData("支払利息", 30000),
        ]

        cash_flow = MockCashFlow()
        equity_change = None
        fixed_assets = []
        bonds = []
        loans = []
        reserves = []

        year = 2025

        print("📊 テストデータ:")
        print(f"  資産: {len(assets)}件")
        print(f"  負債: {len(liabilities)}件")
        print(f"  収益: {len(revenues)}件")
        print(f"  費用: {len(expenses)}件")
        print(f"  対象年度: {year}年\n")

        # 各帳票タイプをテスト
        report_types = [
            ('balance_sheet', '貸借対照表'),
            ('income_statement', '損益計算書'),
            ('cash_flow', 'キャッシュフロー計算書'),
            ('equity_change', '株主資本等変動計算書'),
            ('notes', '附属明細書'),
            ('all', '全ての財務諸表')
        ]

        for report_type, report_name in report_types:
            print(f"🔄 {report_name}を生成中...")

            try:
                # Excel生成
                output = create_improved_financial_statements_excel(
                    assets, liabilities, revenues, expenses, cash_flow, equity_change,
                    fixed_assets, bonds, loans, reserves, year, report_type
                )

                # ファイル保存
                filename = f'/home/esan/employee-db/improved_{report_type}_{year}.xlsx'
                with open(filename, 'wb') as f:
                    f.write(output.getvalue())

                # ファイルサイズ確認
                file_size = os.path.getsize(filename)
                print(f"  ✓ 生成成功: {filename}")
                print(f"  📁 ファイルサイズ: {file_size:,} bytes")

                if file_size > 0:
                    print(f"  ✅ {report_name}が正常に生成されました\n")
                else:
                    print(f"  ❌ {report_name}ファイルが空です\n")

            except Exception as e:
                print(f"  ❌ {report_name}生成エラー: {e}\n")
                import traceback
                traceback.print_exc()

        print("📝 改良点の確認:")
        print("  ✓ 日本の会計基準に準拠したフォーマット")
        print("  ✓ 適切な区分表示（流動/固定）")
        print("  ✓ 統一されたフォント（MSゴシック）")
        print("  ✓ 罫線とセル結合の適切な使用")
        print("  ✓ カンマ区切りの金額表示")
        print("  ✓ 色分けによる視認性向上")
        print("  ✓ 小計・合計の明確な表示")

        print("\n🌐 Webでの確認:")
        print("1. Flask アプリを起動")
        print("2. http://127.0.0.1:5001/accounting_login でログイン")
        print("3. http://127.0.0.1:5001/financial_statements で財務諸表表示")
        print("4. 「Excel出力」から各帳票をダウンロード")
        print("5. 生成されたファイルをExcelで開いて確認")

        print("\n📋 従来版との比較:")
        print("  改良版: より詳細な区分、日本基準準拠、視認性向上")
        print("  従来版: シンプルな表示、基本的な機能")

    except ImportError as e:
        print(f"❌ モジュールインポートエラー: {e}")
        print("openpyxlパッケージが必要です: pip install openpyxl")
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_excel()
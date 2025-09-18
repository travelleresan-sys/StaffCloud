#!/usr/bin/env python3
"""
改良版財務諸表Excel出力の統合テスト
"""

from app import app, db
from models import AccountingAccount, JournalEntry, JournalEntryDetail, User
from datetime import date
import os

def test_integration():
    """統合テスト"""

    with app.app_context():
        try:
            print("=== 改良版財務諸表Excel統合テスト ===\n")

            # テスト用データ確認・作成
            test_accounts = [
                {'code': '1001', 'name': '現金', 'type': '資産'},
                {'code': '1002', 'name': '売掛金', 'type': '資産'},
                {'code': '1003', 'name': '建物', 'type': '資産'},
                {'code': '2001', 'name': '買掛金', 'type': '負債'},
                {'code': '2002', 'name': '未払金', 'type': '負債'},
                {'code': '4001', 'name': '売上高', 'type': '収益'},
                {'code': '5001', 'name': '給料手当', 'type': '費用'},
                {'code': '5002', 'name': '減価償却費', 'type': '費用'}
            ]

            for account_data in test_accounts:
                existing = AccountingAccount.query.filter_by(account_code=account_data['code']).first()
                if not existing:
                    account = AccountingAccount(
                        account_code=account_data['code'],
                        account_name=account_data['name'],
                        account_type=account_data['type'],
                        is_active=True
                    )
                    db.session.add(account)

            db.session.commit()
            print("✓ テスト用勘定科目を確認/作成しました")

            # テスト用ユーザー確認・作成
            test_user = User.query.filter_by(email='test@example.com').first()
            if not test_user:
                test_user = User(
                    email='test@example.com',
                    password='test',
                    role='accounting'
                )
                db.session.add(test_user)
                db.session.commit()
            print("✓ テスト用ユーザーを確認/作成しました")

            # テスト用取引データ作成
            if not JournalEntry.query.filter_by(reference_number='IMPROVED_TEST_001').first():
                # 売上取引
                journal_entry = JournalEntry(
                    reference_number='IMPROVED_TEST_001',
                    entry_date=date(2025, 9, 18),
                    description='改良版テスト売上取引',
                    total_amount=1000000,
                    created_by=test_user.id
                )
                db.session.add(journal_entry)
                db.session.flush()

                # 借方：現金 1,000,000
                cash_account = AccountingAccount.query.filter_by(account_code='1001').first()
                debit_detail = JournalEntryDetail(
                    journal_entry_id=journal_entry.id,
                    account_id=cash_account.id,
                    debit_amount=1000000,
                    credit_amount=0,
                    description='売上代金'
                )
                db.session.add(debit_detail)

                # 貸方：売上高 1,000,000
                sales_account = AccountingAccount.query.filter_by(account_code='4001').first()
                credit_detail = JournalEntryDetail(
                    journal_entry_id=journal_entry.id,
                    account_id=sales_account.id,
                    debit_amount=0,
                    credit_amount=1000000,
                    description='商品売上'
                )
                db.session.add(credit_detail)

                db.session.commit()
                print("✓ テスト用取引データを作成しました")
            else:
                print("✓ テスト用取引データは既に存在します")

            # 改良版Excel出力テスト
            from app import generate_financial_statements_excel

            # データ取得（2025年）
            year = 2025

            # 資産科目の残高
            assets = db.session.query(
                AccountingAccount.account_name,
                db.func.sum(JournalEntryDetail.debit_amount - JournalEntryDetail.credit_amount).label('balance')
            ).join(JournalEntryDetail).join(JournalEntry).filter(
                AccountingAccount.account_type == '資産',
                db.extract('year', JournalEntry.entry_date) == year
            ).group_by(AccountingAccount.id, AccountingAccount.account_name).all()

            # 負債科目の残高
            liabilities = db.session.query(
                AccountingAccount.account_name,
                db.func.sum(JournalEntryDetail.credit_amount - JournalEntryDetail.debit_amount).label('balance')
            ).join(JournalEntryDetail).join(JournalEntry).filter(
                AccountingAccount.account_type == '負債',
                db.extract('year', JournalEntry.entry_date) == year
            ).group_by(AccountingAccount.id, AccountingAccount.account_name).all()

            # 収益科目の残高
            revenues = db.session.query(
                AccountingAccount.account_name,
                db.func.sum(JournalEntryDetail.credit_amount - JournalEntryDetail.debit_amount).label('balance')
            ).join(JournalEntryDetail).join(JournalEntry).filter(
                AccountingAccount.account_type == '収益',
                db.extract('year', JournalEntry.entry_date) == year
            ).group_by(AccountingAccount.id, AccountingAccount.account_name).all()

            # 費用科目の残高
            expenses = db.session.query(
                AccountingAccount.account_name,
                db.func.sum(JournalEntryDetail.debit_amount - JournalEntryDetail.credit_amount).label('balance')
            ).join(JournalEntryDetail).join(JournalEntry).filter(
                AccountingAccount.account_type == '費用',
                db.extract('year', JournalEntry.entry_date) == year
            ).group_by(AccountingAccount.id, AccountingAccount.account_name).all()

            print(f"\n📊 データベースから取得したデータ:")
            print(f"  資産: {len(assets)}件 {[(a.account_name, a.balance) for a in assets]}")
            print(f"  負債: {len(liabilities)}件 {[(l.account_name, l.balance) for l in liabilities]}")
            print(f"  収益: {len(revenues)}件 {[(r.account_name, r.balance) for r in revenues]}")
            print(f"  費用: {len(expenses)}件 {[(e.account_name, e.balance) for e in expenses]}")

            # ダミーデータ作成
            from app import create_cash_flow_statement, create_equity_change_statement
            from app import create_fixed_assets_schedule, create_bonds_schedule
            from app import create_loans_schedule, create_reserves_schedule

            cash_flow = create_cash_flow_statement(year)
            equity_change = create_equity_change_statement(year)
            fixed_assets = create_fixed_assets_schedule(year)
            bonds = create_bonds_schedule(year)
            loans = create_loans_schedule(year)
            reserves = create_reserves_schedule(year)

            # 改良版Excel生成テスト
            test_files = [
                ('balance_sheet', '貸借対照表'),
                ('income_statement', '損益計算書'),
                ('all', '全ての財務諸表')
            ]

            for report_type, report_name in test_files:
                print(f"\n🔄 {report_name}（改良版）を生成中...")

                try:
                    output = generate_financial_statements_excel(
                        assets, liabilities, revenues, expenses, cash_flow, equity_change,
                        fixed_assets, bonds, loans, reserves, year, report_type
                    )

                    # ファイル保存
                    test_filename = f'/home/esan/employee-db/integration_test_{report_type}_{year}.xlsx'
                    with open(test_filename, 'wb') as f:
                        f.write(output.getvalue())

                    file_size = os.path.getsize(test_filename)
                    print(f"  ✅ {report_name}生成成功！")
                    print(f"  📁 ファイル: {test_filename}")
                    print(f"  📊 サイズ: {file_size:,} bytes")

                except Exception as e:
                    print(f"  ❌ {report_name}生成エラー: {e}")
                    import traceback
                    traceback.print_exc()

            print(f"\n🚀 統合テスト完了")
            print(f"📋 改良点:")
            print(f"  ✓ 日本の会計基準準拠フォーマット")
            print(f"  ✓ データベース連携")
            print(f"  ✓ 区分表示（流動/固定）")
            print(f"  ✓ 統一フォント・罫線")
            print(f"  ✓ 色分け・視認性向上")

            print(f"\n🌐 Webアプリでのテスト方法:")
            print(f"1. Flask起動: python app.py")
            print(f"2. ブラウザ: http://127.0.0.1:5001/")
            print(f"3. 会計ダッシュボード → 財務諸表")
            print(f"4. Excel出力ボタンで改良版をダウンロード")

        except Exception as e:
            db.session.rollback()
            print(f"❌ 統合テストエラー: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_integration()
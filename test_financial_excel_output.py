#!/usr/bin/env python3
"""
財務諸表Excel出力のテスト
"""

from app import app, db
from models import AccountingAccount, JournalEntry, JournalEntryDetail, User
from datetime import date
import sys
import os

def test_excel_output():
    """財務諸表Excel出力のテスト"""
    
    with app.app_context():
        try:
            print("=== 財務諸表Excel出力テスト開始 ===\n")
            
            # テスト用勘定科目を確認・作成
            test_accounts = [
                {'code': '1001', 'name': '現金', 'type': '資産'},
                {'code': '4001', 'name': '売上高', 'type': '収益'},
                {'code': '5001', 'name': '給料手当', 'type': '費用'},
                {'code': '2001', 'name': '未払金', 'type': '負債'}
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
            cash_account = AccountingAccount.query.filter_by(account_code='1001').first()
            sales_account = AccountingAccount.query.filter_by(account_code='4001').first()
            expense_account = AccountingAccount.query.filter_by(account_code='5001').first()
            liability_account = AccountingAccount.query.filter_by(account_code='2001').first()
            
            # 既存のテスト取引確認
            test_entry = JournalEntry.query.filter_by(reference_number='TEST_EXCEL_001').first()
            if not test_entry:
                # 売上取引
                journal_entry = JournalEntry(
                    reference_number='TEST_EXCEL_001',
                    entry_date=date(2025, 9, 17),
                    description='テスト売上取引',
                    total_amount=500000,
                    created_by=test_user.id
                )
                db.session.add(journal_entry)
                db.session.flush()
                
                # 借方：現金 500,000
                debit_detail = JournalEntryDetail(
                    journal_entry_id=journal_entry.id,
                    account_id=cash_account.id,
                    debit_amount=500000,
                    credit_amount=0,
                    description='売上代金'
                )
                db.session.add(debit_detail)
                
                # 貸方：売上高 500,000
                credit_detail = JournalEntryDetail(
                    journal_entry_id=journal_entry.id,
                    account_id=sales_account.id,
                    debit_amount=0,
                    credit_amount=500000,
                    description='商品売上'
                )
                db.session.add(credit_detail)
                
                # 費用取引
                expense_entry = JournalEntry(
                    reference_number='TEST_EXCEL_002',
                    entry_date=date(2025, 9, 17),
                    description='テスト費用取引',
                    total_amount=200000,
                    created_by=test_user.id
                )
                db.session.add(expense_entry)
                db.session.flush()
                
                # 借方：給料手当 200,000
                expense_debit = JournalEntryDetail(
                    journal_entry_id=expense_entry.id,
                    account_id=expense_account.id,
                    debit_amount=200000,
                    credit_amount=0,
                    description='給料支払'
                )
                db.session.add(expense_debit)
                
                # 貸方：未払金 200,000
                liability_credit = JournalEntryDetail(
                    journal_entry_id=expense_entry.id,
                    account_id=liability_account.id,
                    debit_amount=0,
                    credit_amount=200000,
                    description='給料未払計上'
                )
                db.session.add(liability_credit)
                
                db.session.commit()
                print("✓ テスト用取引データを作成しました")
            else:
                print("✓ テスト用取引データは既に存在します")
            
            # Excel出力機能をテスト
            try:
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
                
                print(f"\n残高データ確認:")
                print(f"資産: {[(a.account_name, a.balance) for a in assets]}")
                print(f"負債: {[(l.account_name, l.balance) for l in liabilities]}")
                print(f"収益: {[(r.account_name, r.balance) for r in revenues]}")
                print(f"費用: {[(e.account_name, e.balance) for e in expenses]}")
                
                # キャッシュフロー等のダミーデータ
                from app import create_cash_flow_statement, create_equity_change_statement
                from app import create_fixed_assets_schedule, create_bonds_schedule
                from app import create_loans_schedule, create_reserves_schedule
                
                cash_flow = create_cash_flow_statement(year)
                equity_change = create_equity_change_statement(year)
                fixed_assets = create_fixed_assets_schedule(year)
                bonds = create_bonds_schedule(year)
                loans = create_loans_schedule(year)
                reserves = create_reserves_schedule(year)
                
                # Excel生成テスト（貸借対照表のみ）
                print(f"\n=== Excel生成テスト ===")
                output = generate_financial_statements_excel(
                    assets, liabilities, revenues, expenses, cash_flow, equity_change,
                    fixed_assets, bonds, loans, reserves, year, 'balance_sheet'
                )
                
                # ファイル保存テスト
                test_filename = f'/home/esan/employee-db/test_financial_statements_{year}.xlsx'
                with open(test_filename, 'wb') as f:
                    f.write(output.getvalue())
                
                print(f"✓ Excel出力テスト成功！")
                print(f"✓ ファイル保存: {test_filename}")
                
                # ファイルサイズ確認
                file_size = os.path.getsize(test_filename)
                print(f"✓ ファイルサイズ: {file_size:,} bytes")
                
                if file_size > 0:
                    print("✓ ファイルが正常に生成されました")
                else:
                    print("✗ ファイルが空です")
                
            except Exception as excel_error:
                print(f"✗ Excel出力エラー: {excel_error}")
                import traceback
                traceback.print_exc()
                
            print(f"\n=== 動作確認 ===")
            print("Webブラウザで以下を確認してください：")
            print("1. http://127.0.0.1:5001/accounting_login でログイン")
            print("2. http://127.0.0.1:5001/financial_statements で財務諸表表示")
            print("3. 「Excel出力」ボタンで各帳票のダウンロードテスト")
            print("4. ダウンロードしたファイルをExcelで開いて内容確認")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_excel_output()
#!/usr/bin/env python3
"""
繰越機能のテスト用データ作成と動作確認
"""

from app import app, db
from models import (AccountingAccount, JournalEntry, JournalEntryDetail, 
                   OpeningBalance, AccountingPeriod)
from datetime import date, datetime

def create_test_data():
    """テスト用のデータを作成"""
    
    with app.app_context():
        try:
            # テスト用勘定科目作成（現金、売上高）
            cash_account = AccountingAccount.query.filter_by(account_code='1001').first()
            if not cash_account:
                cash_account = AccountingAccount(
                    account_code='1001',
                    account_name='現金',
                    account_type='資産',
                    is_active=True
                )
                db.session.add(cash_account)
            
            sales_account = AccountingAccount.query.filter_by(account_code='4001').first()
            if not sales_account:
                sales_account = AccountingAccount(
                    account_code='4001',
                    account_name='売上高',
                    account_type='収益',
                    is_active=True
                )
                db.session.add(sales_account)
            
            db.session.commit()
            print("✓ 勘定科目を作成しました")
            
            # 2024年度の期首残高を設定（現金：100,000円）
            existing_opening = OpeningBalance.query.filter_by(
                fiscal_year=2024,
                account_id=cash_account.id
            ).first()
            
            if not existing_opening:
                opening_balance = OpeningBalance(
                    fiscal_year=2024,
                    account_id=cash_account.id,
                    opening_balance=100000,  # 現金100,000円
                    source_type='manual'
                )
                db.session.add(opening_balance)
                print("✓ 2024年度期首残高を設定しました（現金：100,000円）")
            
            # 2024年度の取引データ作成（売上）
            existing_entry = JournalEntry.query.filter_by(reference_number='TEST001').first()
            if not existing_entry:
                # 売上取引
                journal_entry = JournalEntry(
                    reference_number='TEST001',
                    entry_date=date(2024, 5, 15),
                    description='商品販売'
                )
                db.session.add(journal_entry)
                db.session.flush()  # IDを取得するため
                
                # 借方：現金 50,000
                debit_detail = JournalEntryDetail(
                    journal_entry_id=journal_entry.id,
                    account_id=cash_account.id,
                    debit_amount=50000,
                    credit_amount=0,
                    description='商品販売'
                )
                db.session.add(debit_detail)
                
                # 貸方：売上高 50,000
                credit_detail = JournalEntryDetail(
                    journal_entry_id=journal_entry.id,
                    account_id=sales_account.id,
                    debit_amount=0,
                    credit_amount=50000,
                    description='商品販売'
                )
                db.session.add(credit_detail)
                
                print("✓ 2024年度取引データを作成しました（売上：50,000円）")
            
            db.session.commit()
            print("✓ テストデータの作成が完了しました")
            
            # 現在の残高を表示
            print("\n=== 2024年度期末残高 ===")
            
            # 現金の残高計算
            cash_balance = 100000  # 期首残高
            cash_transactions = db.session.query(
                db.func.sum(JournalEntryDetail.debit_amount - JournalEntryDetail.credit_amount)
            ).join(JournalEntry).filter(
                JournalEntryDetail.account_id == cash_account.id,
                JournalEntry.entry_date >= date(2024, 4, 1),
                JournalEntry.entry_date <= date(2025, 3, 31)
            ).scalar() or 0
            
            cash_ending_balance = cash_balance + cash_transactions
            print(f"現金: {cash_ending_balance:,}円 (期首:{cash_balance:,} + 取引:{cash_transactions:,})")
            
            # 売上高の残高計算
            sales_balance = db.session.query(
                db.func.sum(JournalEntryDetail.credit_amount - JournalEntryDetail.debit_amount)
            ).join(JournalEntry).filter(
                JournalEntryDetail.account_id == sales_account.id,
                JournalEntry.entry_date >= date(2024, 4, 1),
                JournalEntry.entry_date <= date(2025, 3, 31)
            ).scalar() or 0
            
            print(f"売上高: {sales_balance:,}円")
            
            print("\n繰越処理のテスト準備が完了しました！")
            print("Webブラウザで以下を確認してください：")
            print("1. 総勘定元帳で現金の2024年度を表示")
            print("2. 年度管理画面で2024→2025年度の繰越処理を実行")
            print("3. 総勘定元帳で現金の2025年度を表示（期首残高が表示されるか確認）")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ エラーが発生しました: {e}")
            raise

if __name__ == "__main__":
    create_test_data()
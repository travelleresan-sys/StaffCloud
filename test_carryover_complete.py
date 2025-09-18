#!/usr/bin/env python3
"""
繰越処理の完全な動作確認テスト
"""

from app import app, db
from models import (AccountingAccount, JournalEntry, JournalEntryDetail, 
                   OpeningBalance, AccountingPeriod)
from datetime import date, datetime

def test_carryover_complete():
    """繰越処理の完全テスト"""
    
    with app.app_context():
        try:
            print("=== 繰越処理テスト開始 ===\n")
            
            # 現金勘定の確認
            cash_account = AccountingAccount.query.filter_by(account_code='1001').first()
            if not cash_account:
                print("✗ 現金勘定が見つかりません")
                return
            
            print(f"現金勘定: {cash_account.account_code} - {cash_account.account_name}")
            
            # 2024年度の期首残高確認
            opening_2024 = OpeningBalance.query.filter_by(
                fiscal_year=2024,
                account_id=cash_account.id
            ).first()
            
            if opening_2024:
                print(f"2024年度期首残高: {opening_2024.opening_balance:,}円")
            else:
                print("2024年度期首残高: 0円（未設定）")
            
            # 2024年度の取引データ確認
            details_2024 = db.session.query(
                db.func.sum(JournalEntryDetail.debit_amount - JournalEntryDetail.credit_amount)
            ).join(JournalEntry).filter(
                JournalEntryDetail.account_id == cash_account.id,
                JournalEntry.entry_date >= date(2024, 4, 1),
                JournalEntry.entry_date <= date(2025, 3, 31)
            ).scalar() or 0
            
            print(f"2024年度取引合計: {details_2024:,}円")
            
            # 2024年度期末残高計算
            opening_balance_2024 = opening_2024.opening_balance if opening_2024 else 0
            ending_balance_2024 = opening_balance_2024 + details_2024
            print(f"2024年度期末残高: {ending_balance_2024:,}円")
            
            # 繰越処理を実行（手動で）
            print("\n--- 繰越処理実行 ---")
            
            # 2025年度に既存の期首残高があるかチェック
            existing_opening_2025 = OpeningBalance.query.filter_by(
                fiscal_year=2025,
                account_id=cash_account.id
            ).first()
            
            if existing_opening_2025:
                print(f"既存の2025年度期首残高: {existing_opening_2025.opening_balance:,}円")
                existing_opening_2025.opening_balance = ending_balance_2024
                existing_opening_2025.source_type = 'carryover'
                existing_opening_2025.updated_at = datetime.now()
                print("期首残高を更新しました")
            else:
                new_opening_2025 = OpeningBalance(
                    fiscal_year=2025,
                    account_id=cash_account.id,
                    opening_balance=ending_balance_2024,
                    source_type='carryover'
                )
                db.session.add(new_opening_2025)
                print("新しい期首残高を作成しました")
            
            db.session.commit()
            print(f"2025年度期首残高: {ending_balance_2024:,}円 を設定しました")
            
            # 2025年度の確認
            print("\n--- 2025年度確認 ---")
            opening_2025 = OpeningBalance.query.filter_by(
                fiscal_year=2025,
                account_id=cash_account.id
            ).first()
            
            if opening_2025:
                print(f"2025年度期首残高: {opening_2025.opening_balance:,}円")
                print(f"設定方法: {opening_2025.source_type}")
                print(f"更新日時: {opening_2025.updated_at}")
            
            # 2025年度の取引データ確認
            details_2025 = db.session.query(
                db.func.sum(JournalEntryDetail.debit_amount - JournalEntryDetail.credit_amount)
            ).join(JournalEntry).filter(
                JournalEntryDetail.account_id == cash_account.id,
                JournalEntry.entry_date >= date(2025, 4, 1),
                JournalEntry.entry_date <= date(2026, 3, 31)
            ).scalar() or 0
            
            print(f"2025年度取引合計: {details_2025:,}円")
            
            opening_balance_2025 = opening_2025.opening_balance if opening_2025 else 0
            current_balance_2025 = opening_balance_2025 + details_2025
            print(f"2025年度現在残高: {current_balance_2025:,}円")
            
            print("\n=== 繰越処理テスト完了 ===")
            print("\nWebブラウザで以下を確認してください：")
            print("1. http://127.0.0.1:5001/accounting_ledger?account_id=2&year=2024")
            print("   → 2024年度の現金勘定を表示（期首残高100,000円）")
            print("2. http://127.0.0.1:5001/accounting_ledger?account_id=2&year=2025")
            print("   → 2025年度の現金勘定を表示（期首残高が繰越されているか確認）")
            print("3. Excelエクスポートも試してください")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ エラーが発生しました: {e}")
            raise

if __name__ == "__main__":
    test_carryover_complete()
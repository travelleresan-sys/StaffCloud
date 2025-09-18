#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import TransactionPattern, AccountingAccount

def check_equipment_rules():
    """備品購入に関する仕訳ルールを確認"""
    
    with app.app_context():
        # 備品に関する取引パターンを検索
        equipment_patterns = TransactionPattern.query.filter(
            TransactionPattern.pattern_name.like('%備品%')
        ).all()
        
        print("=== 備品関連の取引パターン ===")
        for pattern in equipment_patterns:
            print(f"\nパターンID: {pattern.id}")
            print(f"パターン名: {pattern.pattern_name}")
            print(f"カテゴリ: {pattern.category}")
            print(f"借方科目コード: {pattern.debit_account_code}")
            print(f"貸方科目コード: {pattern.credit_account_code}")
            print(f"取引タイプ: {pattern.transaction_type}")
            print(f"アクティブ: {pattern.is_active}")
            
            # 対応する勘定科目の詳細を表示
            debit_account = AccountingAccount.query.filter_by(account_code=pattern.debit_account_code).first()
            credit_account = AccountingAccount.query.filter_by(account_code=pattern.credit_account_code).first()
            
            if debit_account:
                print(f"借方科目: {debit_account.account_code} - {debit_account.account_name} ({debit_account.account_type})")
            else:
                print(f"借方科目: {pattern.debit_account_code} (科目不明)")
                
            if credit_account:
                print(f"貸方科目: {credit_account.account_code} - {credit_account.account_name} ({credit_account.account_type})")
            else:
                print(f"貸方科目: {pattern.credit_account_code} (科目不明)")
            
            print("-" * 50)
        
        # 備品関連の勘定科目を確認
        print("\n=== 備品関連の勘定科目 ===")
        equipment_accounts = AccountingAccount.query.filter(
            AccountingAccount.account_name.like('%備品%')
        ).all()
        
        for account in equipment_accounts:
            print(f"科目コード: {account.account_code}")
            print(f"科目名: {account.account_name}")
            print(f"科目種別: {account.account_type}")
            print(f"アクティブ: {account.is_active}")
            print("-" * 30)

if __name__ == '__main__':
    check_equipment_rules()
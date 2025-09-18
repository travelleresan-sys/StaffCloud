#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import AccountingAccount

def add_missing_accounts():
    """不足している勘定科目を追加"""
    
    # 追加する勘定科目のリスト
    new_accounts = [
        # 資産
        {'account_code': '1501', 'account_name': '車両運搬具', 'account_type': 'asset'},
        {'account_code': '1601', 'account_name': '工具器具備品', 'account_type': 'asset'},
        {'account_code': '1602', 'account_name': '減価償却累計額', 'account_type': 'asset'},
        {'account_code': '1701', 'account_name': 'ソフトウェア', 'account_type': 'asset'},
        
        # 負債
        {'account_code': '2501', 'account_name': '借入金', 'account_type': 'liability'},
        
        # 収益
        {'account_code': '4201', 'account_name': '受取利息', 'account_type': 'revenue'},
        {'account_code': '4301', 'account_name': '雑収入', 'account_type': 'revenue'},
        
        # 経費
        {'account_code': '5201', 'account_name': '消耗品費', 'account_type': 'expense'},
        {'account_code': '5301', 'account_name': '修繕費', 'account_type': 'expense'},
        {'account_code': '5401', 'account_name': '保険料', 'account_type': 'expense'},
        {'account_code': '5501', 'account_name': '租税公課', 'account_type': 'expense'},
        {'account_code': '5601', 'account_name': '減価償却費', 'account_type': 'expense'},
    ]
    
    with app.app_context():
        for account_data in new_accounts:
            # 既存の勘定科目があるかチェック
            existing = AccountingAccount.query.filter_by(
                account_code=account_data['account_code']
            ).first()
            
            if not existing:
                account = AccountingAccount(**account_data)
                db.session.add(account)
                print(f"追加: {account_data['account_code']} - {account_data['account_name']}")
            else:
                print(f"既存: {account_data['account_code']} - {account_data['account_name']}")
        
        try:
            db.session.commit()
            print("勘定科目の追加が完了しました。")
        except Exception as e:
            db.session.rollback()
            print(f"エラー: {e}")

if __name__ == '__main__':
    add_missing_accounts()
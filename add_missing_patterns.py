#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import TransactionPattern

def add_missing_patterns():
    """不足している取引パターンを追加"""
    
    # 追加する取引パターンのリスト
    new_patterns = [
        # 資産関係
        {
            'pattern_name': '備品・器具の購入',
            'category': '資産関係',
            'transaction_type': '出金',
            'debit_account_code': '1601',  # 工具器具備品
            'credit_account_code': None,  # 現金・預金（動的）
            'main_account_side': 'cash_credit',
            'tax_type': '課税',
            'description': '事務用品、機械、工具等の購入'
        },
        {
            'pattern_name': '車両の購入',
            'category': '資産関係',
            'transaction_type': '出金',
            'debit_account_code': '1501',  # 車両運搬具
            'credit_account_code': None,
            'main_account_side': 'cash_credit',
            'tax_type': '課税',
            'description': '営業車両、配送車両等の購入'
        },
        {
            'pattern_name': 'ソフトウェアの購入',
            'category': '資産関係',
            'transaction_type': '出金',
            'debit_account_code': '1701',  # ソフトウェア
            'credit_account_code': None,
            'main_account_side': 'cash_credit',
            'tax_type': '課税',
            'description': '業務用ソフトウェア、ライセンス等'
        },
        
        # 負債関係
        {
            'pattern_name': '借入金の返済',
            'category': '負債関係',
            'transaction_type': '出金',
            'debit_account_code': '2501',  # 借入金
            'credit_account_code': None,
            'main_account_side': 'cash_credit',
            'tax_type': '不課税',
            'description': '銀行借入金、役員借入金等の返済'
        },
        {
            'pattern_name': '借入金の受入',
            'category': '負債関係',
            'transaction_type': '入金',
            'debit_account_code': None,
            'credit_account_code': '2501',  # 借入金
            'main_account_side': 'cash_debit',
            'tax_type': '不課税',
            'description': '銀行借入金、役員借入金等の受入'
        },
        
        # 詳細経費関係
        {
            'pattern_name': '消耗品費',
            'category': '経費関係',
            'transaction_type': '出金',
            'debit_account_code': '5201',  # 消耗品費
            'credit_account_code': None,
            'main_account_side': 'cash_credit',
            'tax_type': '課税',
            'description': '事務用品、清掃用品等の消耗品'
        },
        {
            'pattern_name': '修繕費',
            'category': '経費関係',
            'transaction_type': '出金',
            'debit_account_code': '5301',  # 修繕費
            'credit_account_code': None,
            'main_account_side': 'cash_credit',
            'tax_type': '課税',
            'description': '設備、車両等の修理費用'
        },
        {
            'pattern_name': '保険料',
            'category': '経費関係',
            'transaction_type': '出金',
            'debit_account_code': '5401',  # 保険料
            'credit_account_code': None,
            'main_account_side': 'cash_credit',
            'tax_type': '非課税',
            'description': '損害保険料、生命保険料等'
        },
        {
            'pattern_name': '租税公課',
            'category': '経費関係',
            'transaction_type': '出金',
            'debit_account_code': '5501',  # 租税公課
            'credit_account_code': None,
            'main_account_side': 'cash_credit',
            'tax_type': '不課税',
            'description': '印紙税、登録免許税、固定資産税等'
        },
        {
            'pattern_name': '減価償却費',
            'category': '経費関係',
            'transaction_type': '振替',
            'debit_account_code': '5601',  # 減価償却費
            'credit_account_code': '1602',  # 減価償却累計額
            'main_account_side': 'none',
            'tax_type': '不課税',
            'description': '固定資産の減価償却'
        },
        
        # その他収益
        {
            'pattern_name': '受取利息',
            'category': '売上関係',
            'transaction_type': '入金',
            'debit_account_code': None,
            'credit_account_code': '4201',  # 受取利息
            'main_account_side': 'cash_debit',
            'tax_type': '非課税',
            'description': '預金利息、貸付利息等'
        },
        {
            'pattern_name': '雑収入',
            'category': '売上関係',
            'transaction_type': '入金',
            'debit_account_code': None,
            'credit_account_code': '4301',  # 雑収入
            'main_account_side': 'cash_debit',
            'tax_type': '課税',
            'description': 'その他の収入'
        }
    ]
    
    with app.app_context():
        for pattern_data in new_patterns:
            # 既存のパターンがあるかチェック
            existing = TransactionPattern.query.filter_by(
                pattern_name=pattern_data['pattern_name']
            ).first()
            
            if not existing:
                pattern = TransactionPattern(**pattern_data)
                db.session.add(pattern)
                print(f"追加: {pattern_data['pattern_name']}")
            else:
                print(f"既存: {pattern_data['pattern_name']}")
        
        try:
            db.session.commit()
            print("取引パターンの追加が完了しました。")
        except Exception as e:
            db.session.rollback()
            print(f"エラー: {e}")

if __name__ == '__main__':
    add_missing_patterns()
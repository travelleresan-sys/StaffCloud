#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import TransactionPattern, AccountingAccount, BusinessPartner

def create_missing_tables():
    """必要なテーブルを作成し、サンプルデータを追加"""
    
    with app.app_context():
        try:
            # すべてのテーブルを作成（既存のテーブルは無視される）
            db.create_all()
            print("テーブルの作成/確認が完了しました。")
            
            # TransactionPatternのサンプルデータが存在するかチェック
            existing_patterns = TransactionPattern.query.count()
            if existing_patterns == 0:
                print("TransactionPatternのサンプルデータを追加します...")
                
                patterns = [
                    TransactionPattern(
                        id=1,
                        pattern_name="現金売上",
                        description="現金による売上の記録",
                        debit_account_code="101",  # 現金
                        credit_account_code="401", # 売上高
                        is_active=True
                    ),
                    TransactionPattern(
                        id=2,
                        pattern_name="備品購入",
                        description="備品の現金購入",
                        debit_account_code="164",  # 備品
                        credit_account_code="101", # 現金
                        is_active=True
                    ),
                    TransactionPattern(
                        id=3,
                        pattern_name="消耗品購入",
                        description="消耗品の現金購入",
                        debit_account_code="612",  # 消耗品費
                        credit_account_code="101", # 現金
                        is_active=True
                    )
                ]
                
                for pattern in patterns:
                    db.session.add(pattern)
                
                db.session.commit()
                print("TransactionPatternのサンプルデータを追加しました。")
            else:
                print(f"TransactionPatternには既に{existing_patterns}件のデータがあります。")
                
        except Exception as e:
            db.session.rollback()
            print(f"エラー: {e}")

if __name__ == '__main__':
    create_missing_tables()
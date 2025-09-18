#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import TransactionPattern

def fix_equipment_rules():
    """備品購入の仕訳ルールを修正"""
    
    with app.app_context():
        # 備品購入パターンを取得
        equipment_pattern = TransactionPattern.query.filter(
            TransactionPattern.pattern_name.like('%備品%')
        ).first()
        
        if equipment_pattern:
            print(f"修正前:")
            print(f"パターン名: {equipment_pattern.pattern_name}")
            print(f"借方科目コード: {equipment_pattern.debit_account_code}")
            print(f"貸方科目コード: {equipment_pattern.credit_account_code}")
            
            # 貸方科目を現金（101）に設定
            equipment_pattern.credit_account_code = "101"
            
            db.session.commit()
            
            print(f"\n修正後:")
            print(f"パターン名: {equipment_pattern.pattern_name}")
            print(f"借方科目コード: {equipment_pattern.debit_account_code} (工具器具備品)")
            print(f"貸方科目コード: {equipment_pattern.credit_account_code} (現金)")
            print("\n備品購入の仕訳ルールを修正しました。")
        else:
            print("備品購入パターンが見つかりませんでした。")

if __name__ == '__main__':
    fix_equipment_rules()
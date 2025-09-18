#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db

def add_fax_field():
    """BusinessPartnerテーブルにFAXフィールドを追加"""
    
    with app.app_context():
        try:
            # データベーステーブルを更新
            db.create_all()
            print("データベーステーブルが更新されました（FAXフィールド追加）。")
            
        except Exception as e:
            print(f"エラー: {e}")

if __name__ == '__main__':
    add_fax_field()
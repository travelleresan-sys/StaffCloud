#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db

def add_fax_column():
    """BusinessPartnerテーブルにFAXカラムを直接追加"""
    
    with app.app_context():
        try:
            # SQLiteでALTER TABLEを実行してFAXカラムを追加
            with db.engine.connect() as connection:
                connection.execute(db.text('ALTER TABLE business_partner ADD COLUMN fax VARCHAR(20)'))
                connection.commit()
            print("FAXカラムが正常に追加されました。")
            
        except Exception as e:
            if "duplicate column name" in str(e) or "already exists" in str(e):
                print("FAXカラムは既に存在します。")
            else:
                print(f"エラー: {e}")

if __name__ == '__main__':
    add_fax_column()
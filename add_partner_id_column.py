#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db

def add_partner_id_column():
    """JournalEntryテーブルにpartner_idカラムを追加"""
    
    with app.app_context():
        try:
            # SQLiteでALTER TABLEを実行してpartner_idカラムを追加
            with db.engine.connect() as connection:
                connection.execute(db.text('ALTER TABLE journal_entry ADD COLUMN partner_id INTEGER'))
                connection.commit()
            print("partner_idカラムが正常に追加されました。")
            
        except Exception as e:
            if "duplicate column name" in str(e) or "already exists" in str(e):
                print("partner_idカラムは既に存在します。")
            else:
                print(f"エラー: {e}")

if __name__ == '__main__':
    add_partner_id_column()
#!/usr/bin/env python3
"""
CompanySettingsテーブルに会計年度設定カラムを追加
"""

import sqlite3
import os

def add_fiscal_year_columns():
    """CompanySettingsテーブルに会計年度関連カラムを追加"""
    
    db_path = 'instance/employees.db'
    
    if not os.path.exists(db_path):
        print(f"✗ データベースファイルが見つかりません: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 既存のカラムを確認
        cursor.execute("PRAGMA table_info(company_settings)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"現在のカラム: {columns}")
        
        # fiscal_year_start_monthカラムを追加
        if 'fiscal_year_start_month' not in columns:
            cursor.execute("""
                ALTER TABLE company_settings 
                ADD COLUMN fiscal_year_start_month INTEGER DEFAULT 4
            """)
            print("✓ fiscal_year_start_monthカラムを追加しました")
        else:
            print("fiscal_year_start_monthカラムは既に存在します")
        
        # fiscal_year_start_dayカラムを追加
        if 'fiscal_year_start_day' not in columns:
            cursor.execute("""
                ALTER TABLE company_settings 
                ADD COLUMN fiscal_year_start_day INTEGER DEFAULT 1
            """)
            print("✓ fiscal_year_start_dayカラムを追加しました")
        else:
            print("fiscal_year_start_dayカラムは既に存在します")
        
        conn.commit()
        print("✓ カラム追加が完了しました")
        
    except Exception as e:
        print(f"✗ エラーが発生しました: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_fiscal_year_columns()
#!/usr/bin/env python3
"""
PayrollSlipテーブルに新しい支給項目フィールドを追加するマイグレーション
"""

import sqlite3
import os

def migrate_payroll_fields():
    """PayrollSlipテーブルに新しいフィールドを追加"""
    db_path = 'instance/employees.db'
    
    if not os.path.exists(db_path):
        print(f"❌ データベースファイルが見つかりません: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 PayrollSlipテーブルに新しい支給項目フィールドを追加中...")
        
        # 新しいカラムを追加
        new_columns = [
            'temporary_closure_compensation INTEGER DEFAULT 0',  # 臨時の休業補償
            'salary_payment INTEGER DEFAULT 0',  # 給与
            'bonus_payment INTEGER DEFAULT 0',  # 賞与
        ]
        
        # テーブル構造確認
        cursor.execute("PRAGMA table_info(payroll_slip)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # 新しいカラムを追加
        for column in new_columns:
            column_name = column.split()[0]
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE payroll_slip ADD COLUMN {column}")
                    print(f"✅ 追加: {column_name}")
                except Exception as e:
                    print(f"⚠️  {column_name} 追加スキップ: {e}")
            else:
                print(f"ℹ️  {column_name} は既に存在します")
        
        conn.commit()
        conn.close()
        
        print("✅ PayrollSlipテーブルのマイグレーションが完了しました")
        return True
        
    except Exception as e:
        print(f"❌ マイグレーション中にエラーが発生しました: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == '__main__':
    print("🚀 PayrollSlip新しい支給項目のマイグレーションを開始...")
    success = migrate_payroll_fields()
    
    if success:
        print("🎉 マイグレーションが正常に完了しました！")
        print("💡 アプリケーションを再起動してください。")
    else:
        print("💔 マイグレーションに失敗しました。")
        exit(1)
#!/usr/bin/env python3
"""
週40時間超過分時間外労働フィールドを追加するデータベーススキーマ更新スクリプト
"""
from app import app, db
import sqlite3

def update_payroll_calculation_schema():
    with app.app_context():
        # データベースファイルに直接接続してスキーマを確認・更新
        db_path = 'instance/employees.db'
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("現在のPayrollCalculationテーブルの構造を確認中...")
            cursor.execute("PRAGMA table_info(payroll_calculation)")
            columns = cursor.fetchall()
            existing_columns = [col[1] for col in columns]
            
            print(f"既存カラム: {existing_columns}")
            
            # 週40時間超過分時間外労働の新しいカラムを追加
            new_columns = [
                ('weekly_overtime_minutes', 'INTEGER DEFAULT 0'),
                ('weekly_overtime_pay', 'INTEGER DEFAULT 0')
            ]
            
            for col_name, col_type in new_columns:
                if col_name not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE payroll_calculation ADD COLUMN {col_name} {col_type}")
                        print(f"✅ カラム '{col_name}' を追加しました")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" in str(e):
                            print(f"⚠️ カラム '{col_name}' は既に存在します")
                        else:
                            print(f"❌ カラム '{col_name}' の追加に失敗: {e}")
                else:
                    print(f"⚠️ カラム '{col_name}' は既に存在します")
            
            conn.commit()
            conn.close()
            
            print("✅ 週40時間超過分時間外労働フィールドの追加が完了しました")
            
        except Exception as e:
            print(f"❌ データベース更新中にエラーが発生: {e}")

if __name__ == '__main__':
    update_payroll_calculation_schema()
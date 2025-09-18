#!/usr/bin/env python3
"""
データベースに休暇関連カラムを追加する
"""

import sqlite3
import sys

def add_leave_columns():
    """PayrollCalculationテーブルに休暇関連カラムを追加"""
    print("🔧 PayrollCalculationテーブルに休暇カラムを追加中...")
    
    try:
        # データベースに接続
        conn = sqlite3.connect('instance/employees.db')
        cursor = conn.cursor()
        
        # 既存のカラムを確認
        cursor.execute("PRAGMA table_info(payroll_calculation)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 現在のカラム数: {len(columns)}")
        
        # 追加する必要があるカラム
        new_columns = [
            ("paid_leave_days", "REAL DEFAULT 0"),
            ("special_leave_days", "REAL DEFAULT 0"), 
            ("absence_days", "REAL DEFAULT 0")
        ]
        
        # カラムを追加
        for col_name, col_definition in new_columns:
            if col_name not in columns:
                print(f"➕ {col_name} カラムを追加中...")
                cursor.execute(f"ALTER TABLE payroll_calculation ADD COLUMN {col_name} {col_definition}")
                print(f"✅ {col_name} カラム追加完了")
            else:
                print(f"⏭️  {col_name} カラムは既に存在します")
        
        # 変更をコミット
        conn.commit()
        
        # 更新後のカラムを確認
        cursor.execute("PRAGMA table_info(payroll_calculation)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"🎉 更新完了! カラム数: {len(updated_columns)}")
        print("追加されたカラム:")
        for col_name, _ in new_columns:
            if col_name in updated_columns:
                print(f"  ✅ {col_name}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ データベースエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """メイン実行"""
    print("🚀 PayrollCalculation テーブル更新スクリプト")
    print("=" * 50)
    
    success = add_leave_columns()
    
    if success:
        print("\n✅ データベース更新が完了しました")
        print("   給与明細作成機能が使用可能になります")
    else:
        print("\n❌ データベース更新に失敗しました")
        print("   修正が必要です")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
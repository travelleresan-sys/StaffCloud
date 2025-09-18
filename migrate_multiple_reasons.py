#!/usr/bin/env python3
"""
36協定管理の複数理由対応とCompanySettings拡張のデータベースマイグレーション
"""

import sqlite3
import os

def migrate_database():
    """データベースに新しいカラムを追加"""
    db_path = 'instance/employees.db'
    
    if not os.path.exists(db_path):
        print(f"❌ データベースファイルが見つかりません: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Agreement36テーブルに複数理由フィールドを追加中...")
        
        # Agreement36テーブルに新しいカラムを追加
        overtime_columns = [
            'overtime_reason_1 TEXT',
            'overtime_reason_2 TEXT', 
            'overtime_reason_3 TEXT',
            'overtime_reason_4 TEXT',
            'overtime_business_type_1 VARCHAR(200)',
            'overtime_business_type_2 VARCHAR(200)',
            'overtime_business_type_3 VARCHAR(200)',
            'overtime_business_type_4 VARCHAR(200)',
        ]
        
        holiday_columns = [
            'holiday_work_reason_1 TEXT',
            'holiday_work_reason_2 TEXT',
            'holiday_work_reason_3 TEXT', 
            'holiday_work_reason_4 TEXT',
            'holiday_work_business_type_1 VARCHAR(200)',
            'holiday_work_business_type_2 VARCHAR(200)',
            'holiday_work_business_type_3 VARCHAR(200)',
            'holiday_work_business_type_4 VARCHAR(200)',
        ]
        
        # Agreement36テーブルの構造確認
        cursor.execute("PRAGMA table_info(agreement36)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # 時間外労働理由フィールドを追加
        for column in overtime_columns:
            column_name = column.split()[0]
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE agreement36 ADD COLUMN {column}")
                    print(f"✅ 追加: {column_name}")
                except Exception as e:
                    print(f"⚠️  {column_name} 追加スキップ: {e}")
        
        # 休日労働理由フィールドを追加
        for column in holiday_columns:
            column_name = column.split()[0]
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE agreement36 ADD COLUMN {column}")
                    print(f"✅ 追加: {column_name}")
                except Exception as e:
                    print(f"⚠️  {column_name} 追加スキップ: {e}")
        
        print("🔧 CompanySettingsテーブルに企業基本情報フィールドを追加中...")
        
        # CompanySettingsテーブルに新しいカラムを追加
        company_columns = [
            'company_code VARCHAR(50)',
            'address VARCHAR(500)',
            'phone VARCHAR(20)',
            'fax VARCHAR(20)',
            'email VARCHAR(120)',
            'representative VARCHAR(100)',
            'capital INTEGER',
        ]
        
        # CompanySettingsテーブルの構造確認
        cursor.execute("PRAGMA table_info(company_settings)")
        existing_company_columns = [column[1] for column in cursor.fetchall()]
        
        for column in company_columns:
            column_name = column.split()[0]
            if column_name not in existing_company_columns:
                try:
                    cursor.execute(f"ALTER TABLE company_settings ADD COLUMN {column}")
                    print(f"✅ 追加: {column_name}")
                except Exception as e:
                    print(f"⚠️  {column_name} 追加スキップ: {e}")
        
        # 既存データの移行（overtime_reasonをovertime_reason_1にコピー）
        print("🔄 既存データを新しいフィールドに移行中...")
        try:
            cursor.execute("""
                UPDATE agreement36 
                SET overtime_reason_1 = overtime_reason,
                    overtime_business_type_1 = overtime_business_type,
                    holiday_work_reason_1 = holiday_work_reason,
                    holiday_work_business_type_1 = holiday_work_business_type
                WHERE overtime_reason_1 IS NULL
            """)
            print("✅ 既存データの移行完了")
        except Exception as e:
            print(f"⚠️  データ移行スキップ: {e}")
        
        # company_addressとaddressの同期
        try:
            cursor.execute("""
                UPDATE company_settings 
                SET company_address = address,
                    company_phone = phone
                WHERE company_address IS NULL AND address IS NOT NULL
            """)
            cursor.execute("""
                UPDATE company_settings 
                SET address = company_address,
                    phone = company_phone
                WHERE address IS NULL AND company_address IS NOT NULL
            """)
            print("✅ 企業情報フィールドの同期完了")
        except Exception as e:
            print(f"⚠️  企業情報同期スキップ: {e}")
        
        conn.commit()
        conn.close()
        
        print("✅ データベースマイグレーションが完了しました")
        return True
        
    except Exception as e:
        print(f"❌ マイグレーション中にエラーが発生しました: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == '__main__':
    print("🚀 複数理由対応36協定管理のデータベースマイグレーションを開始...")
    success = migrate_database()
    
    if success:
        print("🎉 マイグレーションが正常に完了しました！")
        print("💡 アプリケーションを再起動してください。")
    else:
        print("💔 マイグレーションに失敗しました。")
        exit(1)
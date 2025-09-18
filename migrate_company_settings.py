#!/usr/bin/env python3
"""
CompanySettingsテーブルに新しいカラムを追加するマイグレーションスクリプト
"""

import sqlite3
import os
from datetime import datetime

def migrate_company_settings():
    """CompanySettingsテーブルに新しいカラムを追加"""
    db_path = 'instance/employees.db'
    
    if not os.path.exists(db_path):
        print(f"❌ データベースファイルが見つかりません: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 CompanySettingsテーブルの構造を確認中...")
        
        # 既存のテーブル構造を確認
        cursor.execute("PRAGMA table_info(company_settings)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 既存のカラム: {columns}")
        
        # 追加が必要なカラムを定義
        new_columns = {
            'company_postal_code': 'VARCHAR(10)',
            'representative_position': 'VARCHAR(100)',
            'business_description': 'TEXT'
        }
        
        # 各カラムをチェックして、存在しない場合は追加
        for column_name, column_type in new_columns.items():
            if column_name not in columns:
                print(f"➕ カラムを追加中: {column_name} ({column_type})")
                cursor.execute(f"ALTER TABLE company_settings ADD COLUMN {column_name} {column_type}")
                print(f"✅ {column_name} カラムを追加しました")
            else:
                print(f"⚠️  {column_name} カラムは既に存在します")
        
        conn.commit()
        
        # 更新後のテーブル構造を確認
        cursor.execute("PRAGMA table_info(company_settings)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 更新後のカラム: {updated_columns}")
        
        conn.close()
        
        print("✅ CompanySettingsテーブルのマイグレーションが完了しました")
        return True
        
    except Exception as e:
        print(f"❌ マイグレーション中にエラーが発生しました: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def create_agreement36_table():
    """Agreement36テーブルを作成"""
    db_path = 'instance/employees.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Agreement36テーブルを作成中...")
        
        # Agreement36テーブルが存在するかチェック
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agreement36'")
        if cursor.fetchone():
            print("⚠️  Agreement36テーブルは既に存在します")
            conn.close()
            return True
        
        # Agreement36テーブルを作成
        create_table_sql = """
        CREATE TABLE agreement36 (
            id INTEGER PRIMARY KEY,
            business_type VARCHAR(200),
            business_name VARCHAR(200),
            business_postal_code VARCHAR(10),
            business_address VARCHAR(500),
            business_phone VARCHAR(20),
            agreement_start_date DATE NOT NULL,
            agreement_end_date DATE NOT NULL,
            overtime_reason TEXT,
            overtime_business_type VARCHAR(200),
            overtime_employee_count INTEGER,
            overtime_hours_daily INTEGER,
            overtime_hours_monthly INTEGER,
            holiday_work_reason TEXT,
            holiday_work_business_type VARCHAR(200),
            holiday_work_employee_count INTEGER,
            legal_holiday_days_count INTEGER,
            holiday_work_start_time TIME,
            holiday_work_end_time TIME,
            agreement_conclusion_date DATE NOT NULL,
            worker_representative_position VARCHAR(100),
            worker_representative_name VARCHAR(100),
            worker_representative_employee_id INTEGER,
            worker_representative_selection_method VARCHAR(200),
            employer_position VARCHAR(100),
            employer_name VARCHAR(100),
            employer_employee_id INTEGER,
            submission_date DATE,
            labor_office_name VARCHAR(200),
            submission_method VARCHAR(50),
            document_number VARCHAR(100),
            is_active BOOLEAN DEFAULT 1,
            status VARCHAR(20) DEFAULT 'draft',
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY (worker_representative_employee_id) REFERENCES employee (id),
            FOREIGN KEY (employer_employee_id) REFERENCES employee (id),
            FOREIGN KEY (created_by) REFERENCES user (id)
        )
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        conn.close()
        
        print("✅ Agreement36テーブルが作成されました")
        return True
        
    except Exception as e:
        print(f"❌ Agreement36テーブル作成中にエラーが発生しました: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == '__main__':
    print("🚀 36協定管理機能のデータベースマイグレーションを開始します...\n")
    
    # CompanySettingsテーブルのマイグレーション
    success1 = migrate_company_settings()
    print()
    
    # Agreement36テーブルの作成
    success2 = create_agreement36_table()
    print()
    
    if success1 and success2:
        print("🎉 すべてのマイグレーションが正常に完了しました！")
        print("💡 アプリケーションを再起動してください。")
    else:
        print("💔 マイグレーションに失敗しました。")
        exit(1)
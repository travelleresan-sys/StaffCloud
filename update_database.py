#!/usr/bin/env python3
"""
データベーススキーマ更新スクリプト
新しいEmployeeフィールドとPerformanceEvaluationテーブルを追加
"""
from app import app, db
from models import Employee, PerformanceEvaluation
import sqlite3

def update_database_schema():
    with app.app_context():
        # データベースファイルに直接接続してスキーマを確認・更新
        db_path = 'instance/employees.db'
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("現在のEmployeeテーブルの構造を確認中...")
            cursor.execute("PRAGMA table_info(employee)")
            columns = cursor.fetchall()
            existing_columns = [col[1] for col in columns]
            
            print(f"既存カラム: {existing_columns}")
            
            # 新しいカラムを追加
            new_columns = [
                ('position', 'VARCHAR(100)'),
                ('department', 'VARCHAR(100)'), 
                ('manager_id', 'INTEGER'),
                ('work_history', 'TEXT'),
                ('skills', 'TEXT'),
                ('qualifications', 'TEXT'),
                ('hire_type', 'VARCHAR(50)'),
                ('salary_grade', 'VARCHAR(10)')
            ]
            
            for col_name, col_type in new_columns:
                if col_name not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE employee ADD COLUMN {col_name} {col_type}")
                        print(f"✅ カラム '{col_name}' を追加しました")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" in str(e):
                            print(f"⚠️ カラム '{col_name}' は既に存在します")
                        else:
                            print(f"❌ カラム '{col_name}' の追加に失敗: {e}")
                else:
                    print(f"⚠️ カラム '{col_name}' は既に存在します")
            
            # PerformanceEvaluationテーブルを作成
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_evaluation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    evaluation_period VARCHAR(20) NOT NULL,
                    overall_rating FLOAT,
                    performance_score FLOAT,
                    behavior_score FLOAT,
                    potential_score FLOAT,
                    strengths TEXT,
                    areas_for_improvement TEXT,
                    goals_next_period TEXT,
                    evaluator_comment TEXT,
                    evaluator_id INTEGER,
                    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employee (id),
                    FOREIGN KEY (evaluator_id) REFERENCES user (id)
                )
            """)
            print("✅ PerformanceEvaluationテーブルを作成/確認しました")
            
            conn.commit()
            conn.close()
            
            print("✅ データベーススキーマの更新が完了しました")
            
        except Exception as e:
            print(f"❌ データベース更新中にエラーが発生: {e}")

if __name__ == '__main__':
    update_database_schema()
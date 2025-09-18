#!/usr/bin/env python3
from app import app, Employee, db
import os

def add_test_residence_card():
    with app.app_context():
        # 最初の従業員に在留カード画像を追加
        employee = Employee.query.first()
        if employee:
            # サンプル画像ファイル名を設定（実際にはファイルが存在する必要があります）
            employee.residence_card_filename = 'sample_residence_card.txt'
            
            try:
                db.session.commit()
                print(f"✓ Added residence card file to employee: {employee.name}")
                print(f"✓ Filename: {employee.residence_card_filename}")
                
                # アップロードディレクトリにファイルが存在するか確認
                file_path = os.path.join('static/uploads', employee.residence_card_filename)
                if os.path.exists(file_path):
                    print(f"✓ File exists at: {file_path}")
                else:
                    print(f"⚠ File does not exist at: {file_path}")
                    
            except Exception as e:
                print(f"✗ Error: {str(e)}")
                db.session.rollback()
        else:
            print("✗ No employees found in database")

if __name__ == "__main__":
    add_test_residence_card()
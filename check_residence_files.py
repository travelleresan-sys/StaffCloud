#!/usr/bin/env python3
from app import app, Employee
import os

def check_residence_files():
    with app.app_context():
        employees = Employee.query.filter(Employee.residence_card_filename.isnot(None)).all()
        
        print("在留カードファイルがある従業員:")
        for employee in employees:
            print(f"  - {employee.name}: {employee.residence_card_filename}")
            
            # ファイルの存在確認
            file_path = os.path.join('static/uploads', employee.residence_card_filename)
            if os.path.exists(file_path):
                print(f"    ✓ ファイル存在: {file_path}")
            else:
                print(f"    ✗ ファイル未発見: {file_path}")
                
            # 代替ファイル名の確認
            alt_files = [
                'sample_residence_card.jpg',
                'sample_residence_card.pdf',
                f'residence_card_{employee.residence_card_filename}'
            ]
            
            for alt_file in alt_files:
                alt_path = os.path.join('static/uploads', alt_file)
                if os.path.exists(alt_path):
                    print(f"    📁 代替ファイル存在: {alt_path}")

if __name__ == "__main__":
    check_residence_files()
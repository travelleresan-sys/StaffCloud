#!/usr/bin/env python3
from app import app, Employee, db

def update_residence_card_filename():
    with app.app_context():
        # 最初の従業員の在留カードファイル名を画像ファイルに更新
        employee = Employee.query.first()
        if employee:
            employee.residence_card_filename = 'sample_residence_card.jpg'
            
            try:
                db.session.commit()
                print(f"✓ Updated residence card filename for {employee.name}")
                print(f"✓ New filename: {employee.residence_card_filename}")
            except Exception as e:
                print(f"✗ Error: {str(e)}")
                db.session.rollback()
        else:
            print("✗ No employees found")

if __name__ == "__main__":
    update_residence_card_filename()
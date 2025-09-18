#!/usr/bin/env python3
from app import app, User, Employee, PersonalInfoRequest, db
from flask_login import login_user

def test_personal_info_request():
    with app.app_context():
        with app.test_request_context():
            try:
                # 従業員ユーザーを取得
                employee_user = User.query.filter_by(role='employee').first()
                employee = Employee.query.get(employee_user.employee_id)
                
                print(f"✓ Testing with employee: {employee.name}")
                print(f"✓ Employee residence_card_filename: {employee.residence_card_filename}")
                
                # PersonalInfoRequestを作成してみる
                test_request = PersonalInfoRequest(
                    employee_id=employee.id,
                    request_type='address',
                    current_value=employee.address or '',
                    new_value='テスト住所',
                    uploaded_filename=None,
                    reason='テスト申請'
                )
                
                db.session.add(test_request)
                db.session.commit()
                print("✓ PersonalInfoRequest creation test passed")
                
                # 作成した申請を削除
                db.session.delete(test_request)
                db.session.commit()
                print("✓ PersonalInfoRequest deletion test passed")
                
                # 在留カードファイル申請をテスト
                residence_card_request = PersonalInfoRequest(
                    employee_id=employee.id,
                    request_type='residence_card_file',
                    current_value=employee.residence_card_filename or '',
                    new_value='test_file.pdf',
                    uploaded_filename='test_file.pdf',
                    reason='テストファイル申請'
                )
                
                db.session.add(residence_card_request)
                db.session.commit()
                print("✓ Residence card file request test passed")
                
                # 作成した申請を削除
                db.session.delete(residence_card_request)
                db.session.commit()
                print("✓ Residence card file request deletion test passed")
                
            except Exception as e:
                print(f"✗ Error: {str(e)}")
                db.session.rollback()

if __name__ == "__main__":
    test_personal_info_request()
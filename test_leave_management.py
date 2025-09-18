#!/usr/bin/env python3
"""
年休管理画面のエラーをテストするスクリプト
"""

from app import app, db
from models import Employee, User, LeaveCredit, LeaveRecord
from datetime import date, timedelta

def test_leave_management():
    with app.app_context():
        try:
            # テスト用の従業員を作成（存在しない場合）
            test_employee = Employee.query.filter_by(name='テスト従業員').first()
            if not test_employee:
                test_employee = Employee(
                    name='テスト従業員',
                    join_date=date(2022, 1, 1),
                    status='在籍中'
                )
                db.session.add(test_employee)
                db.session.commit()
                print(f"テスト従業員を作成しました: ID={test_employee.id}")
            
            # leave_management関数の処理をシミュレート
            employees = Employee.query.all()
            print(f"従業員数: {len(employees)}")
            
            for employee in employees:
                print(f"\n従業員: {employee.name} (ID: {employee.id})")
                
                # 年休付与合計の計算
                try:
                    total_credited = db.session.query(db.func.sum(LeaveCredit.days_credited))\
                        .filter(LeaveCredit.employee_id == employee.id)\
                        .scalar() or 0
                    print(f"  年休付与合計: {total_credited}")
                except Exception as e:
                    print(f"  年休付与合計の計算でエラー: {e}")
                    
                # 年休取得合計の計算
                try:
                    total_taken = db.session.query(db.func.sum(LeaveRecord.days_taken))\
                        .filter(LeaveRecord.employee_id == employee.id)\
                        .scalar() or 0
                    print(f"  年休取得合計: {total_taken}")
                except Exception as e:
                    print(f"  年休取得合計の計算でエラー: {e}")
                    
                # 入社日のチェック
                try:
                    print(f"  入社日: {employee.join_date}")
                    if employee.join_date:
                        from app import calculate_annual_leave_days
                        legal_days = calculate_annual_leave_days(employee.join_date)
                        print(f"  法定年休日数: {legal_days}")
                    else:
                        print("  入社日がNullです！")
                except Exception as e:
                    print(f"  入社日処理でエラー: {e}")
                    
                # 次回付与日の計算
                try:
                    if employee.status == '在籍中':
                        last_auto_grant = db.session.query(LeaveCredit)\
                            .filter(LeaveCredit.employee_id == employee.id)\
                            .order_by(LeaveCredit.date_credited.desc())\
                            .first()
                        
                        if last_auto_grant:
                            next_date = last_auto_grant.date_credited + timedelta(days=365)
                            print(f"  次回付与予定日: {next_date}")
                        else:
                            next_date = employee.join_date + timedelta(days=365)
                            print(f"  次回付与予定日: {next_date}")
                except Exception as e:
                    print(f"  次回付与日計算でエラー: {e}")
                    
        except Exception as e:
            print(f"メインエラー: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_leave_management()
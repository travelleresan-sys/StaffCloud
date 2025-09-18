#!/usr/bin/env python3
"""
6ヶ月経過時点からの自動付与機能をテストするスクリプト
"""

from app import app, db, should_auto_grant_leave, calculate_annual_leave_days
from models import Employee, LeaveCredit
from datetime import date, timedelta

def test_auto_grant_logic():
    with app.app_context():
        try:
            # テスト用従業員を作成
            # 6ヶ月経過した従業員
            employee_6months = Employee.query.filter_by(name='6ヶ月経過従業員').first()
            if not employee_6months:
                employee_6months = Employee(
                    name='6ヶ月経過従業員',
                    join_date=date.today() - timedelta(days=185),  # 約6ヶ月前
                    status='在籍中'
                )
                db.session.add(employee_6months)
            
            # 5ヶ月の従業員（まだ付与されない）
            employee_5months = Employee.query.filter_by(name='5ヶ月従業員').first()
            if not employee_5months:
                employee_5months = Employee(
                    name='5ヶ月従業員',
                    join_date=date.today() - timedelta(days=150),  # 約5ヶ月前
                    status='在籍中'
                )
                db.session.add(employee_5months)
            
            # 1年6ヶ月経過した従業員
            employee_1year6months = Employee.query.filter_by(name='1年6ヶ月従業員').first()
            if not employee_1year6months:
                employee_1year6months = Employee(
                    name='1年6ヶ月従業員',
                    join_date=date.today() - timedelta(days=550),  # 約1年6ヶ月前
                    status='在籍中'
                )
                db.session.add(employee_1year6months)
            
            db.session.commit()
            
            print("=== 自動付与判定テスト ===")
            
            # 6ヶ月経過従業員のテスト
            should_grant = should_auto_grant_leave(employee_6months)
            legal_days = calculate_annual_leave_days(employee_6months.join_date)
            print(f"{employee_6months.name}: 付与すべき={should_grant}, 法定日数={legal_days}日")
            
            # 5ヶ月従業員のテスト
            should_grant = should_auto_grant_leave(employee_5months)
            legal_days = calculate_annual_leave_days(employee_5months.join_date)
            print(f"{employee_5months.name}: 付与すべき={should_grant}, 法定日数={legal_days}日")
            
            # 1年6ヶ月経過従業員のテスト
            should_grant = should_auto_grant_leave(employee_1year6months)
            legal_days = calculate_annual_leave_days(employee_1year6months.join_date)
            print(f"{employee_1year6months.name}: 付与すべき={should_grant}, 法定日数={legal_days}日")
            
            print("\n=== 実際の自動付与処理テスト ===")
            
            # 自動付与処理をシミュレート
            current_date = date.today()
            granted_count = 0
            
            employees = [employee_6months, employee_5months, employee_1year6months]
            
            for employee in employees:
                if should_auto_grant_leave(employee, current_date):
                    days_to_grant = calculate_annual_leave_days(employee.join_date, current_date)
                    
                    if days_to_grant > 0:
                        print(f"✓ {employee.name}に{days_to_grant}日を自動付与")
                        granted_count += 1
                    else:
                        print(f"✗ {employee.name}: 法定日数が0のため付与なし")
                else:
                    print(f"- {employee.name}: 付与条件を満たしていません")
            
            print(f"\n合計付与対象者数: {granted_count}名")
            
        except Exception as e:
            print(f"エラー: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_auto_grant_logic()
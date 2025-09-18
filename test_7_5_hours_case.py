#!/usr/bin/env python3
"""
月〜土まで毎日7.5時間勤務の場合の土曜日時間振り分けテスト

週合計45時間（7.5時間 × 6日）
- 週40時間以内：法定内労働時間
- 週40時間超過：法定外労働時間（25%割増）

土曜日の7.5時間がどう振り分けられるかを確認
"""

import sys
import os
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Employee, WorkingTimeRecord
from app import calculate_weekly_overtime

def test_7_5_hours_daily():
    """月〜土まで毎日7.5時間勤務のテスト"""
    print("月〜土まで毎日7.5時間勤務テスト")
    print("=" * 50)
    
    with app.app_context():
        # テスト従業員を作成
        test_employee = Employee.query.filter_by(name="7.5時間テスト太郎").first()
        if not test_employee:
            test_employee = Employee(
                name="7.5時間テスト太郎",
                join_date=date(2024, 1, 1),
                status="在籍中",
                standard_working_hours=8
            )
            db.session.add(test_employee)
            db.session.commit()
        
        # 既存データをクリア
        WorkingTimeRecord.query.filter_by(employee_id=test_employee.id).delete()
        db.session.commit()
        
        # 月〜土の6日間、各日7.5時間勤務（450分）
        test_dates = [
            (date(2024, 9, 2), '月曜日'),   # 月曜日
            (date(2024, 9, 3), '火曜日'),   # 火曜日  
            (date(2024, 9, 4), '水曜日'),   # 水曜日
            (date(2024, 9, 5), '木曜日'),   # 木曜日
            (date(2024, 9, 6), '金曜日'),   # 金曜日
            (date(2024, 9, 7), '土曜日'),   # 土曜日
        ]
        
        print(f"\n勤務データ作成:")
        print(f"各日7.5時間勤務（週合計45時間 = 2700分）")
        
        for work_date, day_name in test_dates:
            record = WorkingTimeRecord(
                employee_id=test_employee.id,
                work_date=work_date,
                start_time=datetime.strptime('09:00', '%H:%M').time(),
                end_time=datetime.strptime('17:00', '%H:%M').time(),  # 9:00-17:00 = 8時間
                break_time_minutes=90,  # 1.5時間休憩で実働7.5時間
                regular_working_minutes=450,  # 7.5時間 = 450分
                overtime_minutes=0,
                holiday_minutes=0
            )
            db.session.add(record)
            print(f"  {work_date} ({day_name}): 450分（7.5時間）")
        
        db.session.commit()
        
        print(f"\n週40時間制限計算実行前:")
        records_before = WorkingTimeRecord.query.filter_by(employee_id=test_employee.id).order_by(WorkingTimeRecord.work_date).all()
        total_before = sum((r.regular_working_minutes or 0) + (r.overtime_minutes or 0) for r in records_before)
        print(f"  総労働時間: {total_before}分 ({total_before/60:.1f}時間)")
        
        # 週40時間制限計算実行
        print(f"\n週40時間制限計算実行...")
        calculate_weekly_overtime(test_employee.id, 2024, 9)
        db.session.commit()
        
        # 結果確認
        print(f"\n週40時間制限計算実行後:")
        records_after = WorkingTimeRecord.query.filter_by(employee_id=test_employee.id).order_by(WorkingTimeRecord.work_date).all()
        
        total_regular = 0
        total_overtime = 0
        total_holiday = 0
        
        print(f"\n各日の詳細:")
        for record in records_after:
            day_name = ['月', '火', '水', '木', '金', '土', '日'][record.work_date.weekday()]
            regular = record.regular_working_minutes or 0
            overtime = record.overtime_minutes or 0
            holiday = record.holiday_minutes or 0
            
            total_regular += regular
            total_overtime += overtime  
            total_holiday += holiday
            
            print(f"  {record.work_date} ({day_name}): 法定内{regular}分 + 法定外{overtime}分 + 休日{holiday}分")
        
        # 土曜日の詳細分析
        saturday_record = None
        for record in records_after:
            if record.work_date.weekday() == 5:  # 土曜日
                saturday_record = record
                break
        
        print(f"\n=== 集計結果 ===")
        print(f"総労働時間: {total_regular + total_overtime + total_holiday}分 ({(total_regular + total_overtime + total_holiday)/60:.1f}時間)")
        print(f"法定内労働時間: {total_regular}分 ({total_regular/60:.1f}時間)")
        print(f"法定外労働時間(25%): {total_overtime}分 ({total_overtime/60:.1f}時間)")
        print(f"法定休日労働(35%): {total_holiday}分 ({total_holiday/60:.1f}時間)")
        
        print(f"\n=== 土曜日の時間振り分け詳細 ===")
        if saturday_record:
            sat_regular = saturday_record.regular_working_minutes or 0
            sat_overtime = saturday_record.overtime_minutes or 0
            sat_holiday = saturday_record.holiday_minutes or 0
            
            print(f"土曜日 ({saturday_record.work_date})の7.5時間（450分）の振り分け:")
            print(f"  • 法定内労働時間: {sat_regular}分 ({sat_regular/60:.1f}時間)")
            print(f"  • 法定外労働時間(25%割増): {sat_overtime}分 ({sat_overtime/60:.1f}時間)")
            print(f"  • 法定休日労働(35%割増): {sat_holiday}分 ({sat_holiday/60:.1f}時間)")
            
            # 計算ロジックの説明
            print(f"\n=== 計算ロジック説明 ===")
            print(f"週合計労働時間: 2700分（45時間）")
            print(f"週40時間制限: 2400分")
            print(f"超過時間: 300分（5時間）")
            print(f"")
            print(f"週40時間制限により:")
            print(f"  - 週の最初の2400分（40時間）→ 法定内労働時間")
            print(f"  - 残りの300分（5時間）→ 法定外労働時間(25%割増)")
            print(f"")
            print(f"土曜日（最後の日）が調整対象となり:")
            if sat_regular > 0 and sat_overtime > 0:
                print(f"  - {sat_regular}分は法定内労働時間として残る")
                print(f"  - {sat_overtime}分が法定外労働時間(25%割増)に変更される")
            elif sat_overtime == 450:
                print(f"  - 全450分が法定外労働時間(25%割増)に変更される")
            elif sat_regular == 450:
                print(f"  - 全450分が法定内労働時間として残る")
        
        return saturday_record

def main():
    """テスト実行"""
    try:
        saturday_record = test_7_5_hours_daily()
        
        print(f"\n" + "=" * 50)
        print(f"🎯 結論:")
        
        if saturday_record:
            sat_regular = saturday_record.regular_working_minutes or 0
            sat_overtime = saturday_record.overtime_minutes or 0
            
            print(f"月〜土まで毎日7.5時間働いた場合、土曜日の時間振り分けは:")
            print(f"• 法定内労働時間: {sat_regular/60:.1f}時間")
            print(f"• 法定外労働時間(25%割増): {sat_overtime/60:.1f}時間")
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
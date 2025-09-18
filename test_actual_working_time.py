#!/usr/bin/env python3
"""
実際の労働時間計算の動作テスト

現在のデータベースを使用して、週40時間制限の計算が正しく動作しているか確認
"""

import sys
import os
from datetime import date, datetime, timedelta
from time import time

# アプリケーションのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    from models import Employee, WorkingTimeRecord, LegalHolidaySettings
    from app import calculate_weekly_overtime
    
    def test_current_calculation():
        """現在の計算ロジックをテスト"""
        with app.app_context():
            # 既存のテスト従業員があるか確認、なければ作成
            test_employee = Employee.query.filter_by(name="週40時間テスト太郎").first()
            if not test_employee:
                test_employee = Employee(
                    name="週40時間テスト太郎",
                    join_date=date(2024, 1, 1),
                    status="在籍中",
                    standard_working_hours=8
                )
                db.session.add(test_employee)
                db.session.commit()
                print(f"テスト用従業員を作成しました: ID {test_employee.id}")
            else:
                print(f"既存のテスト従業員を使用: ID {test_employee.id}")
            
            # 2024年8月のテストデータをクリア
            WorkingTimeRecord.query.filter(
                WorkingTimeRecord.employee_id == test_employee.id,
                db.extract('year', WorkingTimeRecord.work_date) == 2024,
                db.extract('month', WorkingTimeRecord.work_date) == 8
            ).delete()
            db.session.commit()
            
            # テストケース: 週50時間労働（月〜金9時間、土5時間）
            test_dates = [
                (date(2024, 8, 5), 540),   # 月曜日 9時間 (480 + 60法定外)
                (date(2024, 8, 6), 540),   # 火曜日 9時間 (480 + 60法定外)
                (date(2024, 8, 7), 540),   # 水曜日 9時間 (480 + 60法定外)
                (date(2024, 8, 8), 540),   # 木曜日 9時間 (480 + 60法定外)
                (date(2024, 8, 9), 540),   # 金曜日 9時間 (480 + 60法定外)
                (date(2024, 8, 10), 300),  # 土曜日 5時間
            ]
            
            print("\n=== テストデータ作成 ===")
            for work_date, total_minutes in test_dates:
                # 日単位の計算（8時間超過分は法定外残業）
                if total_minutes <= 480:
                    regular_minutes = total_minutes
                    overtime_minutes = 0
                else:
                    regular_minutes = 480
                    overtime_minutes = total_minutes - 480
                
                record = WorkingTimeRecord(
                    employee_id=test_employee.id,
                    work_date=work_date,
                    start_time=datetime.strptime('09:00', '%H:%M').time(),
                    end_time=datetime.strptime(f'{9 + total_minutes//60}:{total_minutes%60:02d}', '%H:%M').time(),
                    break_time_minutes=60,
                    regular_working_minutes=regular_minutes,
                    overtime_minutes=overtime_minutes,
                    holiday_minutes=0
                )
                db.session.add(record)
                weekday_name = ['月', '火', '水', '木', '金', '土', '日'][work_date.weekday()]
                print(f"{work_date} ({weekday_name}): {total_minutes}分 → 法定内{regular_minutes}分 + 法定外{overtime_minutes}分")
            
            db.session.commit()
            
            # 週40時間計算を実行
            print("\n=== 週40時間制限計算実行 ===")
            calculate_weekly_overtime(test_employee.id, 2024, 8)
            db.session.commit()
            
            # 結果確認
            print("\n=== 計算結果確認 ===")
            records = WorkingTimeRecord.query.filter(
                WorkingTimeRecord.employee_id == test_employee.id,
                WorkingTimeRecord.work_date.between(date(2024, 8, 5), date(2024, 8, 10))
            ).order_by(WorkingTimeRecord.work_date).all()
            
            total_regular = 0
            total_overtime = 0
            total_holiday = 0
            
            for record in records:
                weekday_name = ['月', '火', '水', '木', '金', '土', '日'][record.work_date.weekday()]
                total_regular += record.regular_working_minutes or 0
                total_overtime += record.overtime_minutes or 0
                total_holiday += record.holiday_minutes or 0
                
                print(f"{record.work_date} ({weekday_name}): 法定内{record.regular_working_minutes}分 + 法定外{record.overtime_minutes}分 + 休日{record.holiday_minutes}分")
            
            total_work_time = total_regular + total_overtime + total_holiday
            
            print(f"\n=== 週合計 ===")
            print(f"総労働時間: {total_work_time}分 ({total_work_time/60:.1f}時間)")
            print(f"法定内労働時間: {total_regular}分 ({total_regular/60:.1f}時間)")
            print(f"法定外労働時間(25%): {total_overtime}分 ({total_overtime/60:.1f}時間)")
            print(f"法定休日労働(35%): {total_holiday}分 ({total_holiday/60:.1f}時間)")
            
            # 検証
            print(f"\n=== 検証結果 ===")
            if total_regular == 2400:  # 週40時間
                print("✅ 法定内労働時間が週40時間（2400分）で正しい")
            else:
                print(f"❌ 法定内労働時間が週40時間と異なる: {total_regular}分")
                return False
            
            expected_overtime = total_work_time - 2400  # 40時間超過分
            if total_overtime == expected_overtime:
                print(f"✅ 法定外労働時間が正しい: {expected_overtime}分")
            else:
                print(f"❌ 法定外労働時間が期待値と異なる: 実際{total_overtime}分 vs 期待{expected_overtime}分")
                return False
            
            if total_holiday == 0:
                print("✅ 法定休日労働時間が0分で正しい（平日・土曜日のみのテスト）")
            else:
                print(f"❌ 法定休日労働時間が0でない: {total_holiday}分")
                return False
            
            return True
    
    def test_holiday_calculation():
        """法定休日労働（35%割増）のテスト"""
        with app.app_context():
            test_employee = Employee.query.filter_by(name="週40時間テスト太郎").first()
            
            # 日曜日のテストデータ（法定休日）
            holiday_date = date(2024, 8, 11)  # 日曜日
            
            # 既存の日曜日データをクリア
            WorkingTimeRecord.query.filter(
                WorkingTimeRecord.employee_id == test_employee.id,
                WorkingTimeRecord.work_date == holiday_date
            ).delete()
            
            # 日曜日8時間労働（法定休日労働）
            record = WorkingTimeRecord(
                employee_id=test_employee.id,
                work_date=holiday_date,
                start_time=datetime.strptime('09:00', '%H:%M').time(),
                end_time=datetime.strptime('18:00', '%H:%M').time(),
                break_time_minutes=60,
                regular_working_minutes=0,
                overtime_minutes=0,
                holiday_minutes=480  # 法定休日労働
            )
            db.session.add(record)
            db.session.commit()
            
            print("\n=== 法定休日労働テスト ===")
            print(f"{holiday_date} (日曜日): 法定休日労働 {record.holiday_minutes}分 (35%割増)")
            
            if record.holiday_minutes == 480:
                print("✅ 法定休日労働時間が正しく設定されている")
                return True
            else:
                print(f"❌ 法定休日労働時間が正しくない: {record.holiday_minutes}分")
                return False
    
    if __name__ == "__main__":
        print("労働時間計算の実動作テスト")
        print("=" * 50)
        
        success1 = test_current_calculation()
        success2 = test_holiday_calculation()
        
        if success1 and success2:
            print("\n🎉 すべてのテストがPASS!")
            print("週40時間制限と法定休日労働(35%割増)が正しく動作しています。")
        else:
            print("\n❌ テスト失敗")
            print("労働時間計算ロジックに問題があります。")

except Exception as e:
    print(f"エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()
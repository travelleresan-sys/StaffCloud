#!/usr/bin/env python3
"""
土曜日の扱い確認スクリプト

検証結果での土曜日が法定休日・法定外休日のどちらで計算されているか確認
"""

import sys
import os
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Employee, WorkingTimeRecord, LegalHolidaySettings
from app import calculate_weekly_overtime

def check_saturday_settings():
    """現在の法定休日設定で土曜日がどう設定されているか確認"""
    print("=== 土曜日の法定休日設定確認 ===")
    
    with app.app_context():
        holiday_settings = LegalHolidaySettings.query.first()
        
        if holiday_settings:
            print(f"土曜日が法定休日: {holiday_settings.saturday_legal_holiday}")
            print(f"日曜日が法定休日: {holiday_settings.sunday_legal_holiday}")
            print(f"週起算日: {holiday_settings.week_start_day} (0=月曜日)")
        else:
            print("法定休日設定が見つかりません")
            print("デフォルト設定: 土曜日=法定外休日, 日曜日=法定休日")
        
        return holiday_settings

def test_saturday_calculation():
    """土曜日を含む労働時間計算のテスト"""
    print("\n=== 土曜日を含む労働時間計算テスト ===")
    
    with app.app_context():
        # テスト従業員を作成
        test_employee = Employee.query.filter_by(name="土曜日テスト太郎").first()
        if not test_employee:
            test_employee = Employee(
                name="土曜日テスト太郎",
                join_date=date(2024, 1, 1),
                status="在籍中",
                standard_working_hours=8
            )
            db.session.add(test_employee)
            db.session.commit()
        
        # 既存データをクリア
        WorkingTimeRecord.query.filter_by(employee_id=test_employee.id).delete()
        db.session.commit()
        
        # 月〜土の6日間勤務（各日8時間）
        test_dates = [
            (date(2024, 8, 26), '月曜日'),  # 月曜日
            (date(2024, 8, 27), '火曜日'),  # 火曜日
            (date(2024, 8, 28), '水曜日'),  # 水曜日
            (date(2024, 8, 29), '木曜日'),  # 木曜日
            (date(2024, 8, 30), '金曜日'),  # 金曜日
            (date(2024, 8, 31), '土曜日'),  # 土曜日
        ]
        
        print(f"\n勤務データ作成（各日8時間）:")
        for work_date, day_name in test_dates:
            print(f"  {work_date} ({day_name}): 8時間")
            
            record = WorkingTimeRecord(
                employee_id=test_employee.id,
                work_date=work_date,
                start_time=datetime.strptime('09:00', '%H:%M').time(),
                end_time=datetime.strptime('18:00', '%H:%M').time(),
                break_time_minutes=60,
                regular_working_minutes=480,  # 8時間
                overtime_minutes=0,
                holiday_minutes=0
            )
            db.session.add(record)
        
        db.session.commit()
        
        print(f"週40時間計算実行前の状態:")
        records = WorkingTimeRecord.query.filter_by(employee_id=test_employee.id).order_by(WorkingTimeRecord.work_date).all()
        for record in records:
            day_name = ['月', '火', '水', '木', '金', '土', '日'][record.work_date.weekday()]
            print(f"  {record.work_date} ({day_name}): 法定内{record.regular_working_minutes}分 + 法定外{record.overtime_minutes}分 + 休日{record.holiday_minutes}分")
        
        # 週40時間計算実行
        print(f"\n週40時間制限計算実行...")
        calculate_weekly_overtime(test_employee.id, 2024, 8)
        db.session.commit()
        
        # 結果確認
        print(f"\n週40時間計算実行後の結果:")
        records = WorkingTimeRecord.query.filter_by(employee_id=test_employee.id).order_by(WorkingTimeRecord.work_date).all()
        
        total_regular = 0
        total_overtime = 0
        total_holiday = 0
        
        for record in records:
            day_name = ['月', '火', '水', '木', '金', '土', '日'][record.work_date.weekday()]
            total_regular += record.regular_working_minutes or 0
            total_overtime += record.overtime_minutes or 0
            total_holiday += record.holiday_minutes or 0
            
            print(f"  {record.work_date} ({day_name}): 法定内{record.regular_working_minutes}分 + 法定外{record.overtime_minutes}分 + 休日{record.holiday_minutes}分")
        
        print(f"\n=== 集計結果 ===")
        print(f"総労働時間: {total_regular + total_overtime + total_holiday}分 ({(total_regular + total_overtime + total_holiday)/60:.1f}時間)")
        print(f"法定内労働時間: {total_regular}分 ({total_regular/60:.1f}時間)")
        print(f"法定外労働時間(25%): {total_overtime}分 ({total_overtime/60:.1f}時間)")
        print(f"法定休日労働(35%): {total_holiday}分 ({total_holiday/60:.1f}時間)")
        
        # 土曜日のレコードを特定して分析
        saturday_record = None
        for record in records:
            if record.work_date.weekday() == 5:  # 土曜日
                saturday_record = record
                break
        
        if saturday_record:
            print(f"\n=== 土曜日の分類分析 ===")
            print(f"土曜日 ({saturday_record.work_date}):")
            if saturday_record.holiday_minutes > 0:
                print("  → 法定休日労働(35%割増)として分類")
            elif saturday_record.overtime_minutes > 0:
                print("  → 法定外労働時間(25%割増)として分類")
            elif saturday_record.regular_working_minutes > 0:
                print("  → 法定内労働時間として分類")
            else:
                print("  → 労働時間なし")
        
        return total_regular, total_overtime, total_holiday

def main():
    """土曜日の扱い確認"""
    print("土曜日の扱い確認")
    print("=" * 50)
    
    try:
        # 法定休日設定確認
        holiday_settings = check_saturday_settings()
        
        # 土曜日を含む計算テスト
        regular, overtime, holiday = test_saturday_calculation()
        
        print(f"\n" + "=" * 50)
        print("📊 検証結果での土曜日の扱い:")
        
        if holiday > 0:
            print("✅ 土曜日は法定休日労働(35%割増)として計算されています")
        elif regular == 2400 and overtime == 480:  # 40時間法定内 + 8時間法定外
            print("✅ 土曜日は週40時間超過による法定外労働時間(25%割増)として計算されています")
        elif regular == 2880 and overtime == 0:  # 48時間全て法定内
            print("❌ 土曜日が法定内労働時間として計算されており、週40時間制限が適用されていません")
        else:
            print(f"⚠️  予期しない分類: 法定内{regular}分, 法定外{overtime}分, 休日{holiday}分")
            
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
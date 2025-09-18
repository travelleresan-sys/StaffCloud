#!/usr/bin/env python3
"""
労働時間計算ロジックのテストスクリプト

労働基準法に準拠した以下の計算を検証：
1. 週40時間以内の法定内労働時間
2. 週40時間超過または日8時間超過の法定外労働時間（25%割増）
3. 法定休日の全労働時間（35%割増）
"""

import sys
import os
from datetime import date, datetime, timedelta

# アプリケーションのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Employee, WorkingTimeRecord, LegalHolidaySettings
from app import calculate_weekly_overtime

def create_test_data():
    """テスト用データの作成"""
    with app.app_context():
        # テスト用従業員を作成
        test_employee = Employee(
            name="テスト太郎",
            join_date=date(2024, 1, 1),
            status="在籍中",
            standard_working_hours=8  # 所定労働時間8時間
        )
        
        db.session.add(test_employee)
        db.session.commit()
        
        # 法定休日設定（日曜日のみ法定休日）
        holiday_settings = LegalHolidaySettings.query.first()
        if not holiday_settings:
            holiday_settings = LegalHolidaySettings(
                sunday_legal_holiday=True,
                saturday_legal_holiday=False,
                monday_legal_holiday=False,
                tuesday_legal_holiday=False,
                wednesday_legal_holiday=False,
                thursday_legal_holiday=False,
                friday_legal_holiday=False,
                overtime_rate=0.25,  # 25%割増
                holiday_rate=0.35    # 35%割増
            )
            db.session.add(holiday_settings)
            db.session.commit()
        
        return test_employee

def test_case_1_normal_week():
    """テストケース1: 週40時間以内の通常勤務"""
    print("\n=== テストケース1: 週40時間以内の通常勤務 ===")
    
    with app.app_context():
        employee = create_test_data()
        year, month = 2024, 8
        
        # 2024年8月第1週のデータを作成（月〜金：8時間ずつ）
        test_dates = [
            (date(2024, 8, 5), 480),   # 月曜日 8時間
            (date(2024, 8, 6), 480),   # 火曜日 8時間
            (date(2024, 8, 7), 480),   # 水曜日 8時間
            (date(2024, 8, 8), 480),   # 木曜日 8時間
            (date(2024, 8, 9), 480),   # 金曜日 8時間
        ]
        
        # 勤怠レコードを作成
        for work_date, minutes in test_dates:
            record = WorkingTimeRecord(
                employee_id=employee.id,
                work_date=work_date,
                start_time=datetime.strptime('09:00', '%H:%M').time(),
                end_time=datetime.strptime('18:00', '%H:%M').time(),
                break_time_minutes=60,
                regular_working_minutes=minutes,
                overtime_minutes=0,
                holiday_minutes=0
            )
            db.session.add(record)
        
        db.session.commit()
        
        # 週40時間計算を実行
        calculate_weekly_overtime(employee.id, year, month)
        db.session.commit()
        
        # 結果を確認
        records = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == employee.id,
            WorkingTimeRecord.work_date.between(date(2024, 8, 5), date(2024, 8, 9))
        ).all()
        
        total_regular = sum(r.regular_working_minutes for r in records)
        total_overtime = sum(r.overtime_minutes for r in records)
        
        print(f"合計法定内労働時間: {total_regular}分 ({total_regular/60:.1f}時間)")
        print(f"合計法定外労働時間: {total_overtime}分 ({total_overtime/60:.1f}時間)")
        
        # 期待値: 週40時間以内なので全て法定内労働時間
        assert total_regular == 2400, f"法定内労働時間が期待値と異なります: {total_regular}分"
        assert total_overtime == 0, f"法定外労働時間が期待値と異なります: {total_overtime}分"
        
        print("✅ テストケース1 PASS")

def test_case_2_weekly_overtime():
    """テストケース2: 週40時間超過の場合"""
    print("\n=== テストケース2: 週40時間超過の場合 ===")
    
    with app.app_context():
        employee = create_test_data()
        year, month = 2024, 8
        
        # 既存データをクリア
        WorkingTimeRecord.query.filter_by(employee_id=employee.id).delete()
        
        # 2024年8月第2週のデータを作成（月〜金：9時間ずつ、土：5時間）
        test_dates = [
            (date(2024, 8, 12), 540),  # 月曜日 9時間
            (date(2024, 8, 13), 540),  # 火曜日 9時間
            (date(2024, 8, 14), 540),  # 水曜日 9時間
            (date(2024, 8, 15), 540),  # 木曜日 9時間
            (date(2024, 8, 16), 540),  # 金曜日 9時間
            (date(2024, 8, 17), 300),  # 土曜日 5時間
        ]
        
        # 勤怠レコードを作成（初期は日単位の計算のみ）
        for work_date, minutes in test_dates:
            if minutes > 480:  # 8時間超過
                regular = 480
                overtime = minutes - 480
            else:
                regular = minutes
                overtime = 0
                
            record = WorkingTimeRecord(
                employee_id=employee.id,
                work_date=work_date,
                start_time=datetime.strptime('09:00', '%H:%M').time(),
                end_time=datetime.strptime(f'{9 + minutes//60}:{minutes%60:02d}', '%H:%M').time(),
                break_time_minutes=60,
                regular_working_minutes=regular,
                overtime_minutes=overtime,
                holiday_minutes=0
            )
            db.session.add(record)
        
        db.session.commit()
        
        # 週40時間計算を実行
        calculate_weekly_overtime(employee.id, year, month)
        db.session.commit()
        
        # 結果を確認
        records = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == employee.id,
            WorkingTimeRecord.work_date.between(date(2024, 8, 12), date(2024, 8, 17))
        ).all()
        
        total_regular = sum(r.regular_working_minutes for r in records)
        total_overtime = sum(r.overtime_minutes for r in records)
        total_time = total_regular + total_overtime
        
        print(f"総労働時間: {total_time}分 ({total_time/60:.1f}時間)")
        print(f"法定内労働時間: {total_regular}分 ({total_regular/60:.1f}時間)")
        print(f"法定外労働時間: {total_overtime}分 ({total_overtime/60:.1f}時間)")
        
        # 期待値: 週40時間(2400分)以内が法定内、超過分が法定外
        expected_regular = 2400  # 40時間
        expected_overtime = total_time - expected_regular
        
        assert total_regular == expected_regular, f"法定内労働時間が期待値と異なります: {total_regular}分 (期待値: {expected_regular}分)"
        assert total_overtime == expected_overtime, f"法定外労働時間が期待値と異なります: {total_overtime}分 (期待値: {expected_overtime}分)"
        
        print("✅ テストケース2 PASS")

def test_case_3_holiday_work():
    """テストケース3: 法定休日労働（35%割増）"""
    print("\n=== テストケース3: 法定休日労働（35%割増）===")
    
    with app.app_context():
        employee = create_test_data()
        year, month = 2024, 8
        
        # 既存データをクリア
        WorkingTimeRecord.query.filter_by(employee_id=employee.id).delete()
        
        # 2024年8月第3週のデータ（平日＋日曜日労働）
        test_dates = [
            (date(2024, 8, 19), 480, False),  # 月曜日 8時間（平日）
            (date(2024, 8, 20), 480, False),  # 火曜日 8時間（平日）
            (date(2024, 8, 21), 480, False),  # 水曜日 8時間（平日）
            (date(2024, 8, 22), 480, False),  # 木曜日 8時間（平日）
            (date(2024, 8, 23), 480, False),  # 金曜日 8時間（平日）
            (date(2024, 8, 25), 480, True),   # 日曜日 8時間（法定休日）
        ]
        
        # 勤怠レコードを作成
        for work_date, minutes, is_holiday in test_dates:
            if is_holiday:
                # 法定休日労働（35%割増）
                record = WorkingTimeRecord(
                    employee_id=employee.id,
                    work_date=work_date,
                    start_time=datetime.strptime('09:00', '%H:%M').time(),
                    end_time=datetime.strptime('18:00', '%H:%M').time(),
                    break_time_minutes=60,
                    regular_working_minutes=0,
                    overtime_minutes=0,
                    holiday_minutes=minutes  # 法定休日労働
                )
            else:
                # 平日労働
                record = WorkingTimeRecord(
                    employee_id=employee.id,
                    work_date=work_date,
                    start_time=datetime.strptime('09:00', '%H:%M').time(),
                    end_time=datetime.strptime('18:00', '%H:%M').time(),
                    break_time_minutes=60,
                    regular_working_minutes=minutes,
                    overtime_minutes=0,
                    holiday_minutes=0
                )
            db.session.add(record)
        
        db.session.commit()
        
        # 週40時間計算を実行（法定休日は除外されるため、平日のみで計算）
        calculate_weekly_overtime(employee.id, year, month)
        db.session.commit()
        
        # 結果を確認
        records = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == employee.id,
            WorkingTimeRecord.work_date.between(date(2024, 8, 19), date(2024, 8, 25))
        ).all()
        
        total_regular = sum(r.regular_working_minutes for r in records)
        total_overtime = sum(r.overtime_minutes for r in records)
        total_holiday = sum(r.holiday_minutes for r in records)
        
        print(f"法定内労働時間: {total_regular}分 ({total_regular/60:.1f}時間)")
        print(f"法定外労働時間: {total_overtime}分 ({total_overtime/60:.1f}時間)")
        print(f"法定休日労働時間: {total_holiday}分 ({total_holiday/60:.1f}時間)")
        
        # 期待値: 平日40時間は法定内、法定休日8時間は別計算
        assert total_regular == 2400, f"法定内労働時間が期待値と異なります: {total_regular}分"
        assert total_overtime == 0, f"法定外労働時間が期待値と異なります: {total_overtime}分"
        assert total_holiday == 480, f"法定休日労働時間が期待値と異なります: {total_holiday}分"
        
        print("✅ テストケース3 PASS")

def run_all_tests():
    """全テストケースを実行"""
    print("労働時間計算ロジック テスト開始")
    print("=" * 50)
    
    try:
        test_case_1_normal_week()
        test_case_2_weekly_overtime()  
        test_case_3_holiday_work()
        
        print("\n" + "=" * 50)
        print("🎉 全テストケース PASS!")
        print("労働基準法準拠の労働時間計算が正常に実装されています。")
        
    except Exception as e:
        print(f"\n❌ テスト失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
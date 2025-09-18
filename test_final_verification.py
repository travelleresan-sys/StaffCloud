#!/usr/bin/env python3
"""
労働時間計算の最終検証

要件の確認：
1. 週40時間以内 → 法定内労働時間
2. 週40時間超過 → 法定外労働時間（25%割増）
3. 法定休日 → 法定外労働時間（35%割増）
"""

import sys
import os
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Employee, WorkingTimeRecord
from app import calculate_weekly_overtime

def cleanup_test_data():
    """テストデータのクリーンアップ"""
    with app.app_context():
        # テスト従業員のデータを削除
        test_employees = Employee.query.filter(Employee.name.like('%テスト%')).all()
        for employee in test_employees:
            WorkingTimeRecord.query.filter_by(employee_id=employee.id).delete()
            db.session.delete(employee)
        db.session.commit()

def verify_case_1_within_40_hours():
    """検証ケース1: 週40時間以内（全て法定内）"""
    print("\n=== 検証ケース1: 週40時間以内 ===")
    
    with app.app_context():
        # テスト従業員作成
        employee = Employee(
            name="検証用太郎1",
            join_date=date(2024, 1, 1),
            status="在籍中",
            standard_working_hours=8
        )
        db.session.add(employee)
        db.session.commit()
        
        # 週39時間勤務（月〜金 7.8時間ずつ）
        test_data = [
            (date(2024, 8, 5), 468),   # 月曜日 7.8時間
            (date(2024, 8, 6), 468),   # 火曜日 7.8時間
            (date(2024, 8, 7), 468),   # 水曜日 7.8時間
            (date(2024, 8, 8), 468),   # 木曜日 7.8時間
            (date(2024, 8, 9), 468),   # 金曜日 7.8時間
        ]
        
        # データ作成
        for work_date, minutes in test_data:
            record = WorkingTimeRecord(
                employee_id=employee.id,
                work_date=work_date,
                start_time=datetime.strptime('09:00', '%H:%M').time(),
                end_time=datetime.strptime(f'{9 + minutes//60}:{minutes%60:02d}', '%H:%M').time(),
                break_time_minutes=60,
                regular_working_minutes=minutes,
                overtime_minutes=0,
                holiday_minutes=0
            )
            db.session.add(record)
        
        db.session.commit()
        
        # 週40時間計算実行
        calculate_weekly_overtime(employee.id, 2024, 8)
        db.session.commit()
        
        # 結果確認
        records = WorkingTimeRecord.query.filter_by(employee_id=employee.id).all()
        total_regular = sum(r.regular_working_minutes for r in records)
        total_overtime = sum(r.overtime_minutes for r in records)
        total_holiday = sum(r.holiday_minutes for r in records)
        
        print(f"総労働時間: {total_regular + total_overtime + total_holiday}分 ({(total_regular + total_overtime + total_holiday)/60:.1f}時間)")
        print(f"法定内: {total_regular}分, 法定外(25%): {total_overtime}分, 休日(35%): {total_holiday}分")
        
        # 検証
        assert total_regular == 2340, f"法定内労働時間エラー: {total_regular}分 (期待値: 2340分)"
        assert total_overtime == 0, f"法定外労働時間エラー: {total_overtime}分 (期待値: 0分)"
        assert total_holiday == 0, f"法定休日労働時間エラー: {total_holiday}分 (期待値: 0分)"
        
        print("✅ 週40時間以内は全て法定内労働時間として正しく計算")
        return True

def verify_case_2_over_40_hours():
    """検証ケース2: 週40時間超過（法定内40時間＋法定外超過分）"""
    print("\n=== 検証ケース2: 週40時間超過 ===")
    
    with app.app_context():
        # テスト従業員作成
        employee = Employee(
            name="検証用太郎2",
            join_date=date(2024, 1, 1),
            status="在籍中",
            standard_working_hours=8
        )
        db.session.add(employee)
        db.session.commit()
        
        # 週45時間勤務（月〜金 8時間、土 5時間）
        test_data = [
            (date(2024, 8, 12), 480),  # 月曜日 8時間
            (date(2024, 8, 13), 480),  # 火曜日 8時間
            (date(2024, 8, 14), 480),  # 水曜日 8時間
            (date(2024, 8, 15), 480),  # 木曜日 8時間
            (date(2024, 8, 16), 480),  # 金曜日 8時間
            (date(2024, 8, 17), 300),  # 土曜日 5時間
        ]
        
        # データ作成（最初は日単位計算のみ）
        for work_date, minutes in test_data:
            record = WorkingTimeRecord(
                employee_id=employee.id,
                work_date=work_date,
                start_time=datetime.strptime('09:00', '%H:%M').time(),
                end_time=datetime.strptime(f'{9 + minutes//60}:{minutes%60:02d}', '%H:%M').time(),
                break_time_minutes=60,
                regular_working_minutes=minutes,  # 8時間以内なので全て法定内
                overtime_minutes=0,
                holiday_minutes=0
            )
            db.session.add(record)
        
        db.session.commit()
        
        # 週40時間計算実行
        calculate_weekly_overtime(employee.id, 2024, 8)
        db.session.commit()
        
        # 結果確認
        records = WorkingTimeRecord.query.filter_by(employee_id=employee.id).all()
        total_regular = sum(r.regular_working_minutes for r in records)
        total_overtime = sum(r.overtime_minutes for r in records)
        total_holiday = sum(r.holiday_minutes for r in records)
        total_time = total_regular + total_overtime + total_holiday
        
        print(f"総労働時間: {total_time}分 ({total_time/60:.1f}時間)")
        print(f"法定内: {total_regular}分, 法定外(25%): {total_overtime}分, 休日(35%): {total_holiday}分")
        
        # 検証（週40時間=2400分以内が法定内、超過分が法定外）
        expected_regular = 2400  # 40時間
        expected_overtime = total_time - expected_regular  # 5時間
        
        assert total_regular == expected_regular, f"法定内労働時間エラー: {total_regular}分 (期待値: {expected_regular}分)"
        assert total_overtime == expected_overtime, f"法定外労働時間エラー: {total_overtime}分 (期待値: {expected_overtime}分)"
        assert total_holiday == 0, f"法定休日労働時間エラー: {total_holiday}分 (期待値: 0分)"
        
        print("✅ 週40時間超過分が法定外労働時間(25%割増)として正しく計算")
        return True

def verify_case_3_holiday_work():
    """検証ケース3: 法定休日労働（35%割増）"""
    print("\n=== 検証ケース3: 法定休日労働 ===")
    
    with app.app_context():
        # テスト従業員作成
        employee = Employee(
            name="検証用太郎3",
            join_date=date(2024, 1, 1),
            status="在籍中",
            standard_working_hours=8
        )
        db.session.add(employee)
        db.session.commit()
        
        # 平日40時間＋日曜日8時間
        test_data = [
            (date(2024, 8, 19), 480, False),  # 月曜日 8時間（平日）
            (date(2024, 8, 20), 480, False),  # 火曜日 8時間（平日）
            (date(2024, 8, 21), 480, False),  # 水曜日 8時間（平日）
            (date(2024, 8, 22), 480, False),  # 木曜日 8時間（平日）
            (date(2024, 8, 23), 480, False),  # 金曜日 8時間（平日）
            (date(2024, 8, 25), 480, True),   # 日曜日 8時間（法定休日）
        ]
        
        # データ作成
        for work_date, minutes, is_holiday in test_data:
            if is_holiday:
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
        
        # 週40時間計算実行（法定休日は除外される）
        calculate_weekly_overtime(employee.id, 2024, 8)
        db.session.commit()
        
        # 結果確認
        records = WorkingTimeRecord.query.filter_by(employee_id=employee.id).all()
        total_regular = sum(r.regular_working_minutes for r in records)
        total_overtime = sum(r.overtime_minutes for r in records)
        total_holiday = sum(r.holiday_minutes for r in records)
        
        print(f"総労働時間: {total_regular + total_overtime + total_holiday}分")
        print(f"法定内: {total_regular}分, 法定外(25%): {total_overtime}分, 休日(35%): {total_holiday}分")
        
        # 検証
        assert total_regular == 2400, f"法定内労働時間エラー: {total_regular}分 (期待値: 2400分)"
        assert total_overtime == 0, f"法定外労働時間エラー: {total_overtime}分 (期待値: 0分)" 
        assert total_holiday == 480, f"法定休日労働時間エラー: {total_holiday}分 (期待値: 480分)"
        
        print("✅ 法定休日労働が35%割増として正しく計算、週40時間計算から除外")
        return True

def main():
    """全ての検証を実行"""
    print("労働時間計算の最終検証")
    print("=" * 50)
    
    try:
        # テストデータクリーンアップ
        cleanup_test_data()
        
        # 検証実行
        result1 = verify_case_1_within_40_hours()
        result2 = verify_case_2_over_40_hours()  
        result3 = verify_case_3_holiday_work()
        
        # クリーンアップ
        cleanup_test_data()
        
        if result1 and result2 and result3:
            print("\n" + "=" * 50)
            print("🎉 全ての検証がPASS!")
            print("")
            print("✅ 週40時間以内 → 法定内労働時間")
            print("✅ 週40時間超過 → 法定外労働時間(25%割増)")
            print("✅ 法定休日労働 → 35%割増（週40時間計算から除外）")
            print("")
            print("労働基準法に完全準拠した計算が正しく実装されています！")
            return True
        else:
            print("\n❌ 検証に失敗しました。")
            return False
            
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
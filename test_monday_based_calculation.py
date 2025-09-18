#!/usr/bin/env python3
"""
月曜日起算週40時間制限の動作テスト
"""

import sys
import os
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Employee, WorkingTimeRecord

def create_test_employee():
    """テスト用従業員を作成"""
    with app.app_context():
        # 既存のテスト従業員をクリーンアップ
        test_employee = Employee.query.filter_by(name="月曜起算テスト太郎").first()
        if test_employee:
            # 既存の労働時間レコードも削除
            WorkingTimeRecord.query.filter_by(employee_id=test_employee.id).delete()
            db.session.delete(test_employee)
        
        # 新しいテスト従業員を作成
        test_employee = Employee(
            name="月曜起算テスト太郎",
            join_date=date(2024, 1, 1),
            status="在籍中",
            standard_working_hours=8
        )
        db.session.add(test_employee)
        db.session.commit()
        
        return test_employee

def create_test_data():
    """テストデータを作成"""
    with app.app_context():
        # 既存のテスト従業員をクリーンアップ
        test_employee = Employee.query.filter_by(name="月曜起算テスト太郎").first()
        if test_employee:
            # 既存の労働時間レコードも削除
            WorkingTimeRecord.query.filter_by(employee_id=test_employee.id).delete()
            db.session.delete(test_employee)
        
        # 新しいテスト従業員を作成
        test_employee = Employee(
            name="月曜起算テスト太郎",
            join_date=date(2024, 1, 1),
            status="在籍中",
            standard_working_hours=8
        )
        db.session.add(test_employee)
        db.session.flush()  # IDを取得するためにflush
        
        # 2024年9月第1週のテストデータ（月曜日起算）
        # 月曜日(9/2)から日曜日(9/8)まで
        test_dates = [
            (date(2024, 9, 2), 9, 0, 18, 30, 60),    # 月曜日 9:00-18:30 休憩60分 = 8.5時間
            (date(2024, 9, 3), 9, 0, 19, 0, 60),     # 火曜日 9:00-19:00 休憩60分 = 9時間
            (date(2024, 9, 4), 9, 0, 19, 30, 60),    # 水曜日 9:00-19:30 休憩60分 = 9.5時間
            (date(2024, 9, 5), 9, 0, 20, 0, 60),     # 木曜日 9:00-20:00 休憩60分 = 10時間
            (date(2024, 9, 6), 9, 0, 20, 30, 60),    # 金曜日 9:00-20:30 休憩60分 = 10.5時間
            (date(2024, 9, 7), 10, 0, 15, 0, 60),    # 土曜日 10:00-15:00 休憩60分 = 4時間
        ]
        # 総労働時間: 51.5時間 = 3090分
        # 期待結果: 法定内40時間(2400分) + 法定外11.5時間(690分)
        
        for work_date, start_h, start_m, end_h, end_m, break_mins in test_dates:
            # 労働時間計算
            start_minutes = start_h * 60 + start_m
            end_minutes = end_h * 60 + end_m
            total_minutes = end_minutes - start_minutes - break_mins
            
            # 初期値として全て法定内労働時間として設定
            # 実際の振り分けはJavaScriptで行われる
            record = WorkingTimeRecord(
                employee_id=test_employee.id,
                work_date=work_date,
                start_time=datetime.strptime(f'{start_h:02d}:{start_m:02d}', '%H:%M').time(),
                end_time=datetime.strptime(f'{end_h:02d}:{end_m:02d}', '%H:%M').time(),
                break_time_minutes=break_mins,
                regular_working_minutes=total_minutes,
                overtime_minutes=0,
                holiday_minutes=0
            )
            db.session.add(record)
        
        db.session.commit()
        
        print(f"テスト従業員作成: {test_employee.name} (ID: {test_employee.id})")
        print(f"テストデータ作成完了: 2024年9月第1週")
        print(f"総労働時間: 51.5時間")
        print(f"期待結果: 法定内40時間 + 法定外11.5時間")
        print(f"\nWEBブラウザでhttp://127.0.0.1:5001/working_time_inputにアクセスして")
        print(f"従業員「月曜起算テスト太郎」、2024年9月を選択して動作確認してください")
        
        return test_employee.id

if __name__ == "__main__":
    create_test_data()
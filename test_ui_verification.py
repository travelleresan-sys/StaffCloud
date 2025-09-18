#!/usr/bin/env python3
"""
実際のFlaskアプリのUIに7.5時間データを入力して表示を確認
"""

import sys
import os
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Employee, WorkingTimeRecord

def clear_test_data():
    """テストデータをクリア"""
    print("既存のテストデータをクリア中...")
    with app.app_context():
        # UI入力テスト用のレコードを削除
        test_employee = Employee.query.filter_by(name="UI入力テスト太郎").first()
        if test_employee:
            # 2024年9月のレコードを削除
            records = WorkingTimeRecord.query.filter(
                WorkingTimeRecord.employee_id == test_employee.id,
                db.extract('year', WorkingTimeRecord.work_date) == 2024,
                db.extract('month', WorkingTimeRecord.work_date) == 9
            ).all()
            
            for record in records:
                db.session.delete(record)
            
            db.session.commit()
            print(f"削除したレコード数: {len(records)}")

def create_test_data():
    """7.5時間勤務のテストデータを作成"""
    print("7.5時間勤務のテストデータを作成中...")
    
    with app.app_context():
        # テスト従業員を取得または作成
        test_employee = Employee.query.filter_by(name="UI入力テスト太郎").first()
        if not test_employee:
            test_employee = Employee(
                name="UI入力テスト太郎",
                employee_id="TEST001",
                email="ui-test@example.com"
            )
            db.session.add(test_employee)
            db.session.commit()
        
        # 月〜土曜日のテストデータ (2024年9月2日〜7日)
        test_dates = [
            (date(2024, 9, 2), 0),  # 月曜日
            (date(2024, 9, 3), 1),  # 火曜日
            (date(2024, 9, 4), 2),  # 水曜日
            (date(2024, 9, 5), 3),  # 木曜日
            (date(2024, 9, 6), 4),  # 金曜日
            (date(2024, 9, 7), 5),  # 土曜日
        ]
        
        for work_date, weekday in test_dates:
            # 既存レコードがあれば更新、なければ作成
            record = WorkingTimeRecord.query.filter_by(
                employee_id=test_employee.id,
                work_date=work_date
            ).first()
            
            if not record:
                record = WorkingTimeRecord(
                    employee_id=test_employee.id,
                    work_date=work_date
                )
            
            # 7.5時間勤務: 9:00-18:00, 休憩90分 = 実働7.5時間(450分)
            record.start_time = datetime.strptime("09:00", "%H:%M").time()
            record.end_time = datetime.strptime("18:00", "%H:%M").time()
            record.break_time_minutes = 90
            
            # 初期値: 全て法定内労働時間として設定
            record.regular_working_minutes = 450
            record.overtime_minutes = 0
            record.holiday_minutes = 0
            
            db.session.add(record)
        
        db.session.commit()
        print("テストデータの作成完了")
        
        # 週40時間制限計算を実行
        print("週40時間制限計算を実行中...")
        from app import calculate_weekly_overtime
        calculate_weekly_overtime(test_employee.id, 2024, 9)
        
        print("週40時間制限計算完了")

def verify_results():
    """結果を確認"""
    print("\n=== 結果確認 ===")
    
    with app.app_context():
        test_employee = Employee.query.filter_by(name="UI入力テスト太郎").first()
        if not test_employee:
            print("テスト従業員が見つかりません")
            return False
        
        records = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == test_employee.id,
            db.extract('year', WorkingTimeRecord.work_date) == 2024,
            db.extract('month', WorkingTimeRecord.work_date) == 9
        ).order_by(WorkingTimeRecord.work_date).all()
        
        if not records:
            print("テストレコードが見つかりません")
            return False
        
        print(f"従業員: {test_employee.name}")
        print(f"レコード数: {len(records)}件")
        
        total_regular = 0
        total_overtime = 0
        total_holiday = 0
        saturday_data = None
        
        for record in records:
            day_name = ['月', '火', '水', '木', '金', '土', '日'][record.work_date.weekday()]
            regular = record.regular_working_minutes or 0
            overtime = record.overtime_minutes or 0
            holiday = record.holiday_minutes or 0
            
            total_regular += regular
            total_overtime += overtime
            total_holiday += holiday
            
            # 土曜日のデータを保存
            if record.work_date.weekday() == 5:
                saturday_data = {
                    'regular': regular,
                    'overtime': overtime,
                    'holiday': holiday
                }
            
            print(f"  {record.work_date} ({day_name}): "
                  f"法定内 {regular//60}:{regular%60:02d} + "
                  f"法定外 {overtime//60}:{overtime%60:02d} + "
                  f"休日 {holiday//60}:{holiday%60:02d}")
        
        print(f"\n週合計:")
        print(f"  法定内労働時間: {total_regular//60}:{total_regular%60:02d} ({total_regular}分)")
        print(f"  法定外労働時間: {total_overtime//60}:{total_overtime%60:02d} ({total_overtime}分)")
        print(f"  法定休日労働: {total_holiday//60}:{total_holiday%60:02d} ({total_holiday}分)")
        
        # 期待される結果と比較
        expected_regular = 40 * 60  # 2400分
        expected_overtime = 5 * 60  # 300分
        
        print(f"\n期待される結果:")
        print(f"  法定内労働時間: {expected_regular//60}:{expected_regular%60:02d} ({expected_regular}分)")
        print(f"  法定外労働時間: {expected_overtime//60}:{expected_overtime%60:02d} ({expected_overtime}分)")
        
        # 土曜日の詳細確認
        if saturday_data:
            print(f"\n土曜日の詳細:")
            print(f"  法定内: {saturday_data['regular']//60}:{saturday_data['regular']%60:02d}")
            print(f"  法定外: {saturday_data['overtime']//60}:{saturday_data['overtime']%60:02d}")
            print(f"  休日: {saturday_data['holiday']//60}:{saturday_data['holiday']%60:02d}")
            
            # 土曜日の期待値: 法定内2.5時間(150分) + 法定外5時間(300分)
            saturday_success = (saturday_data['regular'] == 150 and 
                              saturday_data['overtime'] == 300 and 
                              saturday_data['holiday'] == 0)
            
            if saturday_success:
                print("  ✅ 土曜日の計算が正しいです")
            else:
                print("  ❌ 土曜日の計算に問題があります")
                print(f"     期待値: 法定内150分, 法定外300分, 休日0分")
        
        success = (total_regular == expected_regular and 
                  total_overtime == expected_overtime and 
                  total_holiday == 0)
        
        if success:
            print("\n✅ 週40時間制限が正しく適用されています！")
        else:
            print("\n❌ 計算結果が期待値と異なります")
        
        return success

def main():
    """メイン実行"""
    print("📋 実際のFlaskアプリでの7.5時間勤務テスト開始")
    print("=" * 50)
    
    try:
        # テストデータクリア
        clear_test_data()
        
        # テストデータ作成
        create_test_data()
        
        # 結果確認
        success = verify_results()
        
        if success:
            print(f"\n🎉 テスト成功: 月〜土曜日7.5時間勤務の週40時間制限が正しく動作しています")
            print(f"   土曜日は法定内2.5時間 + 法定外5.0時間に調整されました")
        else:
            print(f"\n⚠️  テスト失敗: 計算結果を確認してください")
        
        return success
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
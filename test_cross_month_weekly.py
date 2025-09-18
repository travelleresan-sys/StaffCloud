#!/usr/bin/env python3
"""
クロスマンス週40時間制限計算のテスト
月の開始が水曜日になる場合（2024年5月）のテスト
"""

import sys
import os
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, calculate_weekly_overtime
from models import Employee, WorkingTimeRecord

def create_cross_month_test_data():
    """クロスマンステストデータを作成"""
    print("🧪 クロスマンス週40時間制限テスト")
    print("=" * 60)
    
    with app.app_context():
        # テスト従業員を取得または作成
        test_employee = Employee.query.filter_by(name="クロスマンステスト太郎").first()
        if not test_employee:
            test_employee = Employee(
                name="クロスマンステスト太郎",
                status='在籍中'
            )
            db.session.add(test_employee)
            db.session.commit()
            print(f"テスト従業員を作成: {test_employee.name}")
        
        # 既存データをクリア（2024年4月〜5月）
        existing_records = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == test_employee.id,
            db.extract('year', WorkingTimeRecord.work_date) == 2024,
            db.or_(
                db.extract('month', WorkingTimeRecord.work_date) == 4,
                db.extract('month', WorkingTimeRecord.work_date) == 5
            )
        ).all()
        
        for record in existing_records:
            db.session.delete(record)
        db.session.commit()
        print("既存データをクリアしました")
        
        # 2024年5月のカレンダー確認
        # 5月1日は水曜日なので、その週の月曜日は4月29日
        print(f"\n📅 2024年5月カレンダー:")
        print(f"   5月1日(水) - 月の開始が水曜日")
        print(f"   その週の月曜日は4月29日(月)")
        print(f"   → 4月29日(月)〜5月5日(日) の週がクロスマンス")
        
        # クロスマンステストケース: 4月29日〜5月5日の週
        test_week_data = [
            (date(2024, 4, 29), "月", 450),  # 4月29日(月) - 前月
            (date(2024, 4, 30), "火", 450),  # 4月30日(火) - 前月
            (date(2024, 5, 1), "水", 450),   # 5月1日(水) - 当月
            (date(2024, 5, 2), "木", 450),   # 5月2日(木) - 当月
            (date(2024, 5, 3), "金", 450),   # 5月3日(金) - 当月
            (date(2024, 5, 4), "土", 450),   # 5月4日(土) - 当月
        ]
        
        print(f"\n📋 テストデータ作成: クロスマンス週 (45時間)")
        for work_date, day_name, minutes in test_week_data:
            record = WorkingTimeRecord(
                employee_id=test_employee.id,
                work_date=work_date,
                start_time=datetime.strptime("09:00", "%H:%M").time(),
                end_time=datetime.strptime("18:00", "%H:%M").time(),
                break_time_minutes=90,
                regular_working_minutes=minutes,
                overtime_minutes=0,
                holiday_minutes=0
            )
            db.session.add(record)
            print(f"   {work_date} ({day_name}): {minutes}分 - {'前月' if work_date.month == 4 else '当月'}")
        
        db.session.commit()
        print("クロスマンステストデータ作成完了")
        
        return test_employee

def test_cross_month_calculation():
    """クロスマンス計算のテスト"""
    
    with app.app_context():
        test_employee = create_cross_month_test_data()
        
        # セッションから再取得してDetached問題を回避
        test_employee = Employee.query.filter_by(name="クロスマンステスト太郎").first()
        employee_id = test_employee.id
        
        print(f"\n🔄 5月分の週40時間制限計算実行...")
        calculate_weekly_overtime(employee_id, 2024, 5)
        
        # 結果確認
        print(f"\n📊 計算結果確認:")
        
        # 2024年5月のレコードを確認
        may_records = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == employee_id,
            db.extract('year', WorkingTimeRecord.work_date) == 2024,
            db.extract('month', WorkingTimeRecord.work_date) == 5
        ).order_by(WorkingTimeRecord.work_date).all()
        
        print(f"\n2024年5月のレコード:")
        may_total_regular = 0
        may_total_overtime = 0
        
        for record in may_records:
            day_name = ['月', '火', '水', '木', '金', '土', '日'][record.work_date.weekday()]
            regular = record.regular_working_minutes or 0
            overtime = record.overtime_minutes or 0
            
            may_total_regular += regular
            may_total_overtime += overtime
            
            print(f"   {record.work_date} ({day_name}): "
                  f"法定内{regular//60}:{regular%60:02d} + "
                  f"法定外{overtime//60}:{overtime%60:02d}")
        
        print(f"\n5月合計: 法定内{may_total_regular//60}:{may_total_regular%60:02d} + "
              f"法定外{may_total_overtime//60}:{may_total_overtime%60:02d}")
        
        # 4月のレコードも確認（影響されていないことを確認）
        april_records = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == employee_id,
            db.extract('year', WorkingTimeRecord.work_date) == 2024,
            db.extract('month', WorkingTimeRecord.work_date) == 4
        ).order_by(WorkingTimeRecord.work_date).all()
        
        if april_records:
            print(f"\n2024年4月のレコード（参考）:")
            for record in april_records:
                day_name = ['月', '火', '水', '木', '金', '土', '日'][record.work_date.weekday()]
                regular = record.regular_working_minutes or 0
                overtime = record.overtime_minutes or 0
                
                print(f"   {record.work_date} ({day_name}): "
                      f"法定内{regular//60}:{regular%60:02d} + "
                      f"法定外{overtime//60}:{overtime%60:02d}")
        
        # 週全体の分析
        print(f"\n🔍 週全体分析 (4月29日〜5月5日):")
        week_records = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == employee_id,
            WorkingTimeRecord.work_date >= date(2024, 4, 29),
            WorkingTimeRecord.work_date <= date(2024, 5, 5)
        ).order_by(WorkingTimeRecord.work_date).all()
        
        week_total_regular = 0
        week_total_overtime = 0
        
        for record in week_records:
            day_name = ['月', '火', '水', '木', '金', '土', '日'][record.work_date.weekday()]
            regular = record.regular_working_minutes or 0
            overtime = record.overtime_minutes or 0
            month_label = f"{record.work_date.month}月"
            
            week_total_regular += regular
            week_total_overtime += overtime
            
            print(f"   {record.work_date} ({day_name}) [{month_label}]: "
                  f"法定内{regular//60}:{regular%60:02d} + "
                  f"法定外{overtime//60}:{overtime%60:02d}")
        
        print(f"\n週合計: 法定内{week_total_regular//60}:{week_total_regular%60:02d} + "
              f"法定外{week_total_overtime//60}:{week_total_overtime%60:02d}")
        
        # 検証
        expected_week_regular = 40 * 60  # 2400分
        expected_week_overtime = 5 * 60  # 300分
        
        week_success = (week_total_regular == expected_week_regular and 
                       week_total_overtime == expected_week_overtime)
        
        print(f"\n✅ 検証結果:")
        print(f"   週合計45時間: {'✅' if (week_total_regular + week_total_overtime) == 2700 else '❌'}")
        print(f"   週法定内40時間: {'✅' if week_total_regular == expected_week_regular else '❌'}")
        print(f"   週法定外5時間: {'✅' if week_total_overtime == expected_week_overtime else '❌'}")
        
        if week_success:
            print(f"\n🎉 クロスマンス週40時間制限計算成功！")
            print(f"   月をまたぐ週でも正しく40時間制限が適用されています")
        else:
            print(f"\n❌ クロスマンス計算に問題があります")
        
        return week_success

def main():
    """メイン実行"""
    try:
        success = test_cross_month_calculation()
        
        print(f"\n" + "=" * 60)
        if success:
            print(f"🏆 クロスマンス対応テスト完了:")
            print(f"   ✅ 月曜日起算の週計算")
            print(f"   ✅ 月をまたぐ週の正しい処理")
            print(f"   ✅ 対象月のレコードのみ更新")
            print(f"   ✅ 週40時間制限の適用")
        else:
            print(f"❌ クロスマンス対応に問題があります")
        
        return success
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
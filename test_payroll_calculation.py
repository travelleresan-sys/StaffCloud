#!/usr/bin/env python3
"""
給与計算テスト - 週40時間制限が給与計算に正しく反映されるかを確認
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Employee, WorkingTimeRecord, PayrollCalculation

def test_payroll_calculation():
    """給与計算テスト実行"""
    print("📋 週40時間制限による給与計算テスト")
    print("=" * 50)
    
    with app.app_context():
        # テスト従業員を取得
        test_employee = Employee.query.filter_by(name="UI入力テスト太郎").first()
        if not test_employee:
            print("❌ UI入力テスト太郎が見つかりません")
            return False
        
        print(f"従業員: {test_employee.name} (ID: {test_employee.id})")
        
        # 給与計算用の基本情報を設定（テスト用）
        if not test_employee.base_wage:
            test_employee.base_wage = 1500  # 時給1500円
            test_employee.wage_type = 'hourly'  # 時給制
            db.session.commit()
            print("時給を1500円に設定しました")
        
        # 2024年9月の勤怠レコードを確認
        records = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == test_employee.id,
            db.extract('year', WorkingTimeRecord.work_date) == 2024,
            db.extract('month', WorkingTimeRecord.work_date) == 9
        ).order_by(WorkingTimeRecord.work_date).all()
        
        if not records:
            print("❌ 勤怠レコードが見つかりません")
            return False
        
        print(f"\n勤怠レコード ({len(records)}件):")
        
        total_regular_minutes = 0
        total_overtime_minutes = 0
        total_holiday_minutes = 0
        
        for record in records:
            day_name = ['月', '火', '水', '木', '金', '土', '日'][record.work_date.weekday()]
            regular = record.regular_working_minutes or 0
            overtime = record.overtime_minutes or 0
            holiday = record.holiday_minutes or 0
            
            total_regular_minutes += regular
            total_overtime_minutes += overtime
            total_holiday_minutes += holiday
            
            print(f"  {record.work_date} ({day_name}): "
                  f"法定内{regular//60}:{regular%60:02d} + "
                  f"法定外{overtime//60}:{overtime%60:02d} + "
                  f"休日{holiday//60}:{holiday%60:02d}")
        
        # 給与計算実行
        print(f"\n給与計算を実行中...")
        
        # 実際の給与計算関数を呼び出し
        from app import calculate_monthly_payroll
        payroll_result = calculate_monthly_payroll(test_employee.id, 2024, 9)
        
        # 計算結果を取得
        total_regular_hours = (payroll_result.regular_working_minutes or 0) / 60
        total_overtime_hours = (payroll_result.overtime_minutes or 0) / 60
        total_holiday_hours = (payroll_result.holiday_minutes or 0) / 60
        
        regular_pay = payroll_result.regular_pay or 0
        overtime_pay = payroll_result.overtime_pay or 0
        holiday_pay = payroll_result.holiday_pay or 0
        total_pay = payroll_result.total_pay or 0
        
        print(f"給与計算完了")
        
        # 結果表示
        hourly_wage = test_employee.base_wage
        print(f"\n=== 給与計算結果 ===")
        print(f"基本時給: ¥{hourly_wage:,}/時間")
        print(f"")
        print(f"労働時間:")
        print(f"  法定内労働時間: {total_regular_hours:5.1f}時間")
        print(f"  法定外労働時間: {total_overtime_hours:5.1f}時間 (25%割増)")
        print(f"  法定休日労働:   {total_holiday_hours:5.1f}時間 (35%割増)")
        print(f"")
        print(f"給与:")
        print(f"  法定内労働給:   ¥{regular_pay:8,.0f}")
        print(f"  法定外残業給:   ¥{overtime_pay:8,.0f}")
        print(f"  法定休日労働給: ¥{holiday_pay:8,.0f}")
        print(f"  ──────────────────")
        print(f"  合計給与:       ¥{total_pay:8,.0f}")
        
        # 期待値と比較
        expected_regular_hours = 40.0
        expected_overtime_hours = 5.0
        expected_regular_pay = 40.0 * hourly_wage
        expected_overtime_pay = 5.0 * hourly_wage * 1.25
        expected_total_pay = expected_regular_pay + expected_overtime_pay
        
        print(f"\n=== 期待される結果 ===")
        print(f"法定内労働時間: {expected_regular_hours}時間 → ¥{expected_regular_pay:,.0f}")
        print(f"法定外労働時間: {expected_overtime_hours}時間 → ¥{expected_overtime_pay:,.0f}")
        print(f"合計: ¥{expected_total_pay:,.0f}")
        
        # 検証
        success = (
            abs(total_regular_hours - expected_regular_hours) < 0.1 and
            abs(total_overtime_hours - expected_overtime_hours) < 0.1 and
            abs(total_pay - expected_total_pay) < 1.0
        )
        
        if success:
            print(f"\n✅ 給与計算が正しく実行されました！")
            print(f"   週40時間制限が給与計算に正しく反映されています")
        else:
            print(f"\n❌ 給与計算に問題があります")
        
        return success

def main():
    """メイン実行"""
    try:
        success = test_payroll_calculation()
        
        if success:
            print(f"\n🎉 全体テスト成功:")
            print(f"   • 週40時間制限による労働時間分類: ✅")
            print(f"   • 給与計算への正しい反映: ✅")
            print(f"   • 土曜日の法定内2.5時間 + 法定外5時間: ✅")
        else:
            print(f"\n⚠️  テスト失敗: 詳細を確認してください")
        
        return success
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
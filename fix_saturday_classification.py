#!/usr/bin/env python3
"""
土曜日の分類を法定休日から法定外休日（平日扱い）に修正
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, calculate_weekly_overtime
from models import Employee, WorkingTimeRecord

def fix_saturday_classification():
    """土曜日の分類を修正"""
    print("🔧 土曜日の法定休日分類を修正中...")
    
    with app.app_context():
        test_employee = Employee.query.filter_by(name="UI入力テスト太郎").first()
        if not test_employee:
            print("❌ テスト従業員が見つかりません")
            return False
        
        # 2024年9月の土曜日レコードを取得
        saturday_record = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == test_employee.id,
            WorkingTimeRecord.work_date == date(2024, 9, 7)  # 土曜日
        ).first()
        
        if not saturday_record:
            print("❌ 土曜日のレコードが見つかりません")
            return False
        
        print(f"修正前の土曜日レコード:")
        print(f"  法定内: {(saturday_record.regular_working_minutes or 0)//60}:{(saturday_record.regular_working_minutes or 0)%60:02d}")
        print(f"  法定外: {(saturday_record.overtime_minutes or 0)//60}:{(saturday_record.overtime_minutes or 0)%60:02d}")
        print(f"  休日: {(saturday_record.holiday_minutes or 0)//60}:{(saturday_record.holiday_minutes or 0)%60:02d}")
        
        # 土曜日を平日労働として再設定
        saturday_record.regular_working_minutes = 450  # 7.5時間全て法定内労働時間として設定
        saturday_record.overtime_minutes = 0
        saturday_record.holiday_minutes = 0  # 法定休日労働をクリア
        
        db.session.commit()
        print("✅ 土曜日を平日労働として再設定しました")
        
        # 週40時間制限計算を再実行
        print("🔄 週40時間制限計算を再実行中...")
        calculate_weekly_overtime(test_employee.id, 2024, 9)
        
        # 結果を確認
        updated_saturday = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == test_employee.id,
            WorkingTimeRecord.work_date == date(2024, 9, 7)  # 土曜日
        ).first()
        
        print(f"修正後の土曜日レコード:")
        print(f"  法定内: {(updated_saturday.regular_working_minutes or 0)//60}:{(updated_saturday.regular_working_minutes or 0)%60:02d}")
        print(f"  法定外: {(updated_saturday.overtime_minutes or 0)//60}:{(updated_saturday.overtime_minutes or 0)%60:02d}")
        print(f"  休日: {(updated_saturday.holiday_minutes or 0)//60}:{(updated_saturday.holiday_minutes or 0)%60:02d}")
        
        # 期待される結果: 法定内2.5時間、法定外5時間
        expected_regular = 150  # 2.5時間
        expected_overtime = 300  # 5時間
        actual_regular = updated_saturday.regular_working_minutes or 0
        actual_overtime = updated_saturday.overtime_minutes or 0
        actual_holiday = updated_saturday.holiday_minutes or 0
        
        success = (
            actual_regular == expected_regular and
            actual_overtime == expected_overtime and
            actual_holiday == 0
        )
        
        if success:
            print("✅ 土曜日の分類が正しく修正されました！")
            print(f"   法定内2.5時間 + 法定外5時間 = 7.5時間")
        else:
            print("❌ 土曜日の分類修正に問題があります")
            print(f"   期待値: 法定内{expected_regular}分, 法定外{expected_overtime}分, 休日0分")
            print(f"   実際値: 法定内{actual_regular}分, 法定外{actual_overtime}分, 休日{actual_holiday}分")
        
        return success

def main():
    """メイン実行"""
    try:
        success = fix_saturday_classification()
        
        if success:
            print(f"\n🎉 土曜日の分類修正完了")
            print(f"   土曜日は平日労働として正しく計算されています")
        else:
            print(f"\n⚠️  土曜日の分類修正に失敗しました")
        
        return success
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
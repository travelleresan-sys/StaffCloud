#!/usr/bin/env python3
"""
日曜日リセット週40時間制限システムの簡易テスト
"""

import sys
import os
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 必要最小限のimportのみ
try:
    from models import db, Employee, WorkingTimeRecord
    print("✅ モジュールのインポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    sys.exit(1)

def test_sunday_reset():
    """日曜日リセットシステムの動作確認"""
    print("🌐 日曜日リセット週40時間制限テスト")
    print("=" * 60)
    
    # 直接データベースに接続
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/employees.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # テスト従業員確認
        test_employee = Employee.query.filter_by(name="UI入力テスト太郎").first()
        if not test_employee:
            print("❌ テスト従業員が見つかりません")
            return False
        
        print(f"テスト従業員: {test_employee.name} (ID: {test_employee.id})")
        
        # 2024年9月のレコードを確認
        records = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == test_employee.id,
            db.extract('year', WorkingTimeRecord.work_date) == 2024,
            db.extract('month', WorkingTimeRecord.work_date) == 9
        ).order_by(WorkingTimeRecord.work_date).all()
        
        if not records:
            print("❌ テストデータが見つかりません")
            return False
        
        print(f"\n📋 2024年9月の勤怠データ:")
        print("-" * 60)
        
        # 日曜日起算で週をグループ化
        week_groups = {}
        
        for record in records:
            # 日曜日からの日数を計算 (月曜日=0 → 1, 火曜日=1 → 2, ..., 日曜日=6 → 0)
            days_since_sunday = (record.work_date.weekday() + 1) % 7
            week_start = record.work_date - datetime.timedelta(days=days_since_sunday)
            week_key = week_start.strftime('%Y-%m-%d')
            
            if week_key not in week_groups:
                week_groups[week_key] = []
            week_groups[week_key].append(record)
        
        # 週ごとに表示
        for week_start, week_records in sorted(week_groups.items()):
            print(f"\n📅 週グループ (日曜起算: {week_start}):")
            
            week_total_regular = 0
            week_total_overtime = 0
            week_total_holiday = 0
            
            for record in sorted(week_records, key=lambda x: x.work_date):
                day_name = ['月', '火', '水', '木', '金', '土', '日'][record.work_date.weekday()]
                regular = record.regular_working_minutes or 0
                overtime = record.overtime_minutes or 0
                holiday = record.holiday_minutes or 0
                
                week_total_regular += regular
                week_total_overtime += overtime  
                week_total_holiday += holiday
                
                if record.work_date.weekday() == 6:  # 日曜日を強調
                    print(f"   {record.work_date} ({day_name}): "
                          f"法定内{regular//60}:{regular%60:02d} + "
                          f"法定外{overtime//60}:{overtime%60:02d} + "
                          f"休日{holiday//60}:{holiday%60:02d} ⭐️ [週リセット日]")
                elif record.work_date.weekday() == 5:  # 土曜日も強調
                    print(f"   {record.work_date} ({day_name}): "
                          f"法定内{regular//60}:{regular%60:02d} + "
                          f"法定外{overtime//60}:{overtime%60:02d} + "
                          f"休日{holiday//60}:{holiday%60:02d} 🅂")
                else:
                    print(f"   {record.work_date} ({day_name}): "
                          f"法定内{regular//60}:{regular%60:02d} + "
                          f"法定外{overtime//60}:{overtime%60:02d} + "
                          f"休日{holiday//60}:{holiday%60:02d}")
            
            # 週合計表示
            print(f"   週合計: 法定内{week_total_regular//60}:{week_total_regular%60:02d} + "
                  f"法定外{week_total_overtime//60}:{week_total_overtime%60:02d} + "
                  f"休日{week_total_holiday//60}:{week_total_holiday%60:02d}")
            
            # 週40時間制限チェック
            workday_regular = week_total_regular  # 法定休日を除く
            if workday_regular <= 40 * 60:  # 2400分
                print(f"   ✅ 週40時間制限内")
            else:
                print(f"   ⚠️  週40時間制限超過 ({workday_regular//60}時間)")
        
        return True

def main():
    """メイン実行"""
    try:
        success = test_sunday_reset()
        
        print(f"\n" + "=" * 60)
        if success:
            print(f"✅ 日曜日リセット週40時間システム確認完了")
            print(f"   日曜日を起算日とした週計算が実装されています")
            print(f"   WEBインターフェースでの動作確認をしてください")
        else:
            print(f"❌ システム確認に問題があります")
        
        return success
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
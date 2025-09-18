#!/usr/bin/env python3
"""
給与計算機能の動作テスト
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, calculate_monthly_payroll
    from models import Employee, WorkingTimeRecord, PayrollCalculation
    print("✅ 全てのモジュールインポート成功")
except Exception as e:
    print(f"❌ インポートエラー: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def test_payroll_calculation():
    """給与計算の基本テスト"""
    print("🧮 給与計算機能テスト")
    print("=" * 50)
    
    with app.app_context():
        # テスト従業員を取得
        test_employee = Employee.query.filter_by(name="UI入力テスト太郎").first()
        if not test_employee:
            print("❌ テスト従業員が見つかりません")
            return False
            
        print(f"テスト従業員: {test_employee.name} (ID: {test_employee.id})")
        
        # 2024年9月の勤怠データがあるか確認
        records = WorkingTimeRecord.query.filter(
            WorkingTimeRecord.employee_id == test_employee.id,
            db.extract('year', WorkingTimeRecord.work_date) == 2024,
            db.extract('month', WorkingTimeRecord.work_date) == 9
        ).all()
        
        if not records:
            print("❌ 勤怠データが見つかりません")
            return False
        
        print(f"勤怠レコード数: {len(records)}件")
        
        try:
            print("\n💰 給与計算実行中...")
            calculate_monthly_payroll(test_employee.id, 2024, 9)
            print("✅ 給与計算成功")
            
            # 結果確認
            payroll = PayrollCalculation.query.filter(
                PayrollCalculation.employee_id == test_employee.id,
                PayrollCalculation.calculation_year == 2024,
                PayrollCalculation.calculation_month == 9
            ).first()
            
            if payroll:
                print(f"\n📊 給与計算結果:")
                print(f"   基本給: ¥{payroll.base_salary:,}")
                print(f"   法定外残業手当: ¥{payroll.overtime_pay:,}")
                print(f"   法定外休日労働手当: ¥{payroll.holiday_pay:,}")
                print(f"   総支給額: ¥{payroll.gross_salary:,}")
            else:
                print("⚠️  給与計算結果が保存されていません")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ 給与計算エラー: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """メイン実行"""
    try:
        success = test_payroll_calculation()
        
        print(f"\n" + "=" * 50)
        if success:
            print(f"✅ 給与計算機能テスト成功")
            print(f"   WEBインターフェースでも正常に動作するはずです")
        else:
            print(f"❌ 給与計算機能に問題があります")
        
        return success
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
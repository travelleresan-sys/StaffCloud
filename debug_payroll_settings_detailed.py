#!/usr/bin/env python3
"""
給与設定の詳細デバッグ - 基本給表示問題の調査
"""

import sqlite3
import sys
from datetime import date

def debug_payroll_settings():
    """給与設定の詳細調査"""
    print("🔍 給与設定詳細デバッグ")
    print("=" * 60)
    
    try:
        # データベースに接続
        conn = sqlite3.connect('instance/employees.db')
        cursor = conn.cursor()
        
        # 1. EmployeePayrollSettings テーブルの確認
        print("1️⃣ EmployeePayrollSettings テーブル確認")
        cursor.execute("""
            SELECT id, employee_id, base_salary, wage_type, effective_from, effective_until
            FROM employee_payroll_settings 
            WHERE employee_id = 4
            ORDER BY effective_from DESC
        """)
        payroll_settings = cursor.fetchall()
        
        if payroll_settings:
            print(f"   見つかった設定: {len(payroll_settings)}件")
            for setting in payroll_settings:
                print(f"   ID: {setting[0]}, Employee: {setting[1]}, Base: {setting[2]}, Type: {setting[3]}")
                print(f"   From: {setting[4]}, Until: {setting[5]}")
        else:
            print("   ❌ 給与設定が見つかりません")
        
        # 2. Employee テーブルの base_wage 確認
        print(f"\n2️⃣ Employee テーブル base_wage 確認")
        cursor.execute("SELECT id, name, base_wage, wage_type FROM employee WHERE id = 4")
        employee = cursor.fetchone()
        
        if employee:
            print(f"   従業員: {employee[1]}")
            print(f"   base_wage: {employee[2]}")
            print(f"   wage_type: {employee[3]}")
        else:
            print("   ❌ 従業員が見つかりません")
        
        # 3. PayrollCalculation テーブル確認
        print(f"\n3️⃣ PayrollCalculation テーブル確認")
        cursor.execute("""
            SELECT id, base_salary, wage_type, year, month, calculated_at
            FROM payroll_calculation 
            WHERE employee_id = 4 
            ORDER BY calculated_at DESC 
            LIMIT 3
        """)
        calculations = cursor.fetchall()
        
        if calculations:
            print(f"   計算結果: {len(calculations)}件")
            for calc in calculations:
                print(f"   ID: {calc[0]}, Base: {calc[1]}, Type: {calc[2]}, {calc[3]}/{calc[4]}")
        else:
            print("   ❌ 給与計算結果が見つかりません")
        
        # 4. 現在日付での有効な給与設定検索
        print(f"\n4️⃣ 現在有効な給与設定の検索ロジック確認")
        today = date.today()
        target_date = date(2024, 9, 1)  # テスト対象月
        
        print(f"   今日の日付: {today}")
        print(f"   対象月: {target_date}")
        
        # Flaskアプリと同じロジックで検索
        cursor.execute("""
            SELECT id, employee_id, base_salary, wage_type, effective_from, effective_until
            FROM employee_payroll_settings 
            WHERE employee_id = 4
              AND effective_from <= ?
              AND (effective_until IS NULL OR effective_until >= ?)
            ORDER BY effective_from DESC
        """, (target_date, target_date))
        
        active_settings = cursor.fetchall()
        
        if active_settings:
            print(f"   有効な設定: {len(active_settings)}件")
            for setting in active_settings:
                print(f"   ✅ ID: {setting[0]}, Base: {setting[2]}, From: {setting[4]}, Until: {setting[5]}")
        else:
            print("   ❌ 有効な給与設定が見つかりません")
            print("   これが基本給表示されない原因の可能性があります")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ データベースエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """メイン実行"""
    success = debug_payroll_settings()
    
    print(f"\n" + "=" * 60)
    if success:
        print("✅ デバッグ情報の取得が完了しました")
        print("   結果を確認して問題を特定してください")
    else:
        print("❌ デバッグに失敗しました")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Test script to verify working time data flow from input to payroll dashboard
"""

import sqlite3
from datetime import date

def test_working_time_data():
    """Test the working time data aggregation for payroll dashboard"""
    
    # Connect to database
    conn = sqlite3.connect('instance/employees.db')
    cursor = conn.cursor()
    
    # Test parameters
    employee_id = 2  # 佐藤花子
    year = 2023
    month = 1
    
    print(f"🔍 Testing payroll dashboard data for employee ID {employee_id} ({year}年{month}月)")
    print("="*80)
    
    # Get employee name
    cursor.execute("SELECT name FROM employee WHERE id = ?", (employee_id,))
    employee_name = cursor.fetchone()
    if employee_name:
        print(f"👤 従業員名: {employee_name[0]}")
    else:
        print(f"❌ Employee ID {employee_id} not found")
        return
    
    # Get all working time records for the month
    cursor.execute("""
        SELECT 
            work_date,
            regular_working_minutes,
            legal_overtime_minutes,
            overtime_minutes, 
            legal_holiday_minutes,
            holiday_minutes,
            night_working_minutes
        FROM working_time_record 
        WHERE employee_id = ? 
        AND strftime('%Y', work_date) = ? 
        AND strftime('%m', work_date) = ?
        ORDER BY work_date
    """, (employee_id, str(year), f"{month:02d}"))
    
    records = cursor.fetchall()
    
    if not records:
        print(f"❌ No working time records found for {year}年{month}月")
        return
    
    print(f"📋 Found {len(records)} working time records")
    print()
    
    # Initialize totals
    total_regular = 0
    total_legal_overtime = 0
    total_overtime = 0
    total_legal_holiday = 0
    total_holiday = 0
    total_night = 0
    
    # Display data and calculate totals
    print("📅 Daily breakdown:")
    print("Date     | Regular | Legal OT | Overtime | Legal Hol | Holiday | Night   | Daily Total")
    print("-" * 80)
    
    for record in records:
        work_date, regular, legal_overtime, overtime, legal_holiday, holiday, night = record
        
        # Handle None values
        regular = regular or 0
        legal_overtime = legal_overtime or 0
        overtime = overtime or 0
        legal_holiday = legal_holiday or 0
        holiday = holiday or 0
        night = night or 0
        
        # Calculate daily total
        daily_total = regular + legal_overtime + overtime + legal_holiday + holiday
        
        # Add to totals
        total_regular += regular
        total_legal_overtime += legal_overtime
        total_overtime += overtime
        total_legal_holiday += legal_holiday
        total_holiday += holiday
        total_night += night
        
        # Convert minutes to hours:minutes format
        regular_hm = f"{regular//60:2d}:{regular%60:02d}"
        legal_overtime_hm = f"{legal_overtime//60:2d}:{legal_overtime%60:02d}"
        overtime_hm = f"{overtime//60:2d}:{overtime%60:02d}"
        legal_holiday_hm = f"{legal_holiday//60:2d}:{legal_holiday%60:02d}"
        holiday_hm = f"{holiday//60:2d}:{holiday%60:02d}"
        night_hm = f"{night//60:2d}:{night%60:02d}"
        daily_total_hm = f"{daily_total//60:2d}:{daily_total%60:02d}"
        
        print(f"{work_date} | {regular_hm:>7} | {legal_overtime_hm:>8} | {overtime_hm:>8} | {legal_holiday_hm:>9} | {holiday_hm:>7} | {night_hm:>7} | {daily_total_hm:>11}")
    
    print("-" * 80)
    
    # Calculate grand total
    grand_total = total_regular + total_legal_overtime + total_overtime + total_legal_holiday + total_holiday
    
    # Display totals
    print("📊 Monthly totals:")
    print(f"  法定内労働:     {total_regular//60:3d}:{total_regular%60:02d} ({total_regular:4d} minutes)")
    print(f"  法定内残業:     {total_legal_overtime//60:3d}:{total_legal_overtime%60:02d} ({total_legal_overtime:4d} minutes)")
    print(f"  法定外残業:     {total_overtime//60:3d}:{total_overtime%60:02d} ({total_overtime:4d} minutes)")
    print(f"  法定休日労働:   {total_legal_holiday//60:3d}:{total_legal_holiday%60:02d} ({total_legal_holiday:4d} minutes)")
    print(f"  法定外休日労働: {total_holiday//60:3d}:{total_holiday%60:02d} ({total_holiday:4d} minutes)")
    print(f"  深夜労働:       {total_night//60:3d}:{total_night%60:02d} ({total_night:4d} minutes)")
    print(f"  総労働時間:     {grand_total//60:3d}:{grand_total%60:02d} ({grand_total:4d} minutes)")
    print()
    
    # Verify against expected values from previous analysis
    print("✅ Data verification:")
    if total_regular == 10950:
        print("  ✓ 法定内労働時間 matches expected value (10,950 minutes)")
    else:
        print(f"  ❌ 法定内労働時間 mismatch: got {total_regular}, expected 10950")
    
    if total_overtime == 1200:
        print("  ✓ 法定外残業時間 matches expected value (1,200 minutes)")
    else:
        print(f"  ❌ 法定外残業時間 mismatch: got {total_overtime}, expected 1200")
    
    if total_legal_holiday == 1800:
        print("  ✓ 法定休日労働時間 matches expected value (1,800 minutes)")
    else:
        print(f"  ❌ 法定休日労働時間 mismatch: got {total_legal_holiday}, expected 1800")
    
    print()
    print("🔄 This data should now be properly displayed in the payroll dashboard with all 6 labor time categories:")
    print("   1. 法定内 (Regular Working)")
    print("   2. 法定内残業 (Legal Overtime)")  
    print("   3. 法定外残業 (Overtime)")
    print("   4. 法定休日 (Legal Holiday)")
    print("   5. 法定外休日 (Holiday)")
    print("   6. 深夜 (Night Work)")
    
    conn.close()

if __name__ == "__main__":
    test_working_time_data()
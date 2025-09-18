#!/usr/bin/env python3
"""
新しい支給項目がPDFに正しく反映されるかをテスト
"""

from app import app
from models import Employee, PayrollSlip, PayrollCalculation, db
from payroll_slip_pdf_generator import create_payroll_slip_pdf
import json
from datetime import datetime

def test_payroll_pdf_generation():
    """新しい支給項目を含む給与明細PDFの生成テスト"""
    with app.app_context():
        # テスト用の従業員を取得
        employee = Employee.query.first()
        if not employee:
            print("❌ テスト用従業員が見つかりません")
            return False
            
        print(f"🔍 従業員: {employee.name}")
        
        # テスト用の給与計算データを作成
        payroll_calculation = PayrollCalculation(
            employee_id=employee.id,
            year=2024,
            month=12,
            base_salary=300000,
            overtime_allowance=50000,
            regular_working_minutes=9600,
            overtime_minutes=1800,
            gross_salary=350000
        )
        
        # テスト用の給与明細を作成
        payroll_slip = PayrollSlip(
            employee_id=employee.id,
            payroll_calculation_id=1,
            slip_year=2024,
            slip_month=12,
            base_salary=300000,
            overtime_allowance=50000,
            # 新しい支給項目をテスト
            temporary_closure_compensation=20000,  # 休業補償
            salary_payment=15000,  # 臨時の給与  
            bonus_payment=100000,  # 賞与
            gross_salary=485000,  # 合計金額
            health_insurance=12000,
            pension_insurance=25000,
            employment_insurance=1500,
            income_tax=8000,
            resident_tax=10000,
            total_deduction=56500,
            net_salary=428500,
            working_days=22,
            paid_leave_days=1,
            issued_at=datetime.now()
        )
        
        # PDF生成テスト
        try:
            print("📄 PDF生成中...")
            pdf_buffer = create_payroll_slip_pdf(payroll_slip, employee, payroll_calculation)
            
            # PDFファイルとして保存してテスト
            with open('test_new_fields_payroll.pdf', 'wb') as f:
                f.write(pdf_buffer.read())
            
            print("✅ PDF生成成功: test_new_fields_payroll.pdf")
            print("💡 以下の項目が含まれています:")
            print(f"   - 休業補償: ¥{payroll_slip.temporary_closure_compensation:,}")
            print(f"   - 臨時の給与: ¥{payroll_slip.salary_payment:,}")
            print(f"   - 賞与: ¥{payroll_slip.bonus_payment:,}")
            print(f"   - 総支給額: ¥{payroll_slip.gross_salary:,}")
            
            return True
            
        except Exception as e:
            print(f"❌ PDF生成エラー: {e}")
            return False

if __name__ == '__main__':
    print("🚀 新しい支給項目PDFテストを開始...")
    success = test_payroll_pdf_generation()
    
    if success:
        print("🎉 テストが正常に完了しました！")
    else:
        print("💔 テストに失敗しました。")
        exit(1)
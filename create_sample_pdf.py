#!/usr/bin/env python3
from app import app, Employee, db
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os

def create_sample_pdf():
    # PDF作成
    pdf_path = 'static/uploads/sample_residence_card.pdf'
    c = canvas.Canvas(pdf_path, pagesize=A4)
    
    # タイトル
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50 * mm, 250 * mm, "Sample Residence Card")
    
    # 説明文
    c.setFont("Helvetica", 12)
    c.drawString(50 * mm, 230 * mm, "This is a sample residence card PDF file.")
    c.drawString(50 * mm, 220 * mm, "In actual use, this would contain")
    c.drawString(50 * mm, 210 * mm, "the scanned residence card information.")
    
    # 枠線
    c.rect(40 * mm, 190 * mm, 120 * mm, 70 * mm)
    
    # 保存
    c.save()
    print(f"✓ Sample PDF created: {pdf_path}")
    
    return pdf_path

def update_second_employee_with_pdf():
    with app.app_context():
        # 2番目の従業員にPDFファイルを設定
        employees = Employee.query.all()
        if len(employees) > 1:
            second_employee = employees[1]
            second_employee.residence_card_filename = 'sample_residence_card.pdf'
            
            try:
                db.session.commit()
                print(f"✓ Updated {second_employee.name} with PDF residence card")
            except Exception as e:
                print(f"✗ Error: {str(e)}")
                db.session.rollback()
        else:
            print("✗ Need at least 2 employees for PDF test")

if __name__ == "__main__":
    create_sample_pdf()
    update_second_employee_with_pdf()
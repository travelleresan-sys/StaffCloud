#!/usr/bin/env python3
"""PDF生成テスト用スクリプト"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_calendar_pdf
from models import db, CompanyCalendar
from flask import Flask
from datetime import datetime, date

def test_pdf_generation():
    """PDF生成をテストする"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/esan/employee-db/instance/employees.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        db.init_app(app)
        
        try:
            # テスト用のイベントを追加
            current_year = datetime.now().year
            
            # 既存のテストイベントを削除
            CompanyCalendar.query.filter(CompanyCalendar.title.like('PDFテスト%')).delete()
            
            # 新しいテストイベントを追加（異なる種類）
            test_holiday = CompanyCalendar(
                title='PDFテスト祝日',
                event_date=date(current_year, 12, 29),
                event_type='holiday',
                description='PDF生成テスト用の祝日イベントです。赤背景で表示されるはずです。'
            )
            db.session.add(test_holiday)
            
            test_company_holiday = CompanyCalendar(
                title='PDFテスト会社休日',
                event_date=date(current_year, 12, 28),
                event_type='company_holiday',
                description='PDF生成テスト用の会社休日です。赤背景で表示されるはずです。'
            )
            db.session.add(test_company_holiday)
            
            test_vacation = CompanyCalendar(
                title='PDFテスト有給消化日',
                event_date=date(current_year, 12, 27),
                event_type='vacation',
                description='PDF生成テスト用の有給消化日です。緑背景で表示されるはずです。'
            )
            db.session.add(test_vacation)
            
            test_event = CompanyCalendar(
                title='PDFテスト通常イベント長いタイトルのテスト',
                event_date=date(current_year, 12, 26),
                event_type='event',
                description='PDF生成テスト用の通常イベントです。黄色背景で表示されるはずです。'
            )
            db.session.add(test_event)
            
            db.session.commit()
            print("テストイベントを追加しました")
            
            # PDFを生成
            print("PDF生成を開始...")
            pdf_buffer = create_calendar_pdf()
            
            # PDFファイルを保存
            pdf_filename = f'test_calendar_{current_year}.pdf'
            with open(pdf_filename, 'wb') as f:
                f.write(pdf_buffer.read())
            
            print(f"PDFファイルが生成されました: {pdf_filename}")
            print("ファイルを開いて日本語が正しく表示されるか確認してください。")
            
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_pdf_generation()
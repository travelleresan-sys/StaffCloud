#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, generate_working_conditions_change_pdf
from models import CompanySettings, Employee, User
from datetime import datetime

def test_working_conditions_change_pdf():
    """労働条件変更通知書PDF作成のテスト"""
    with app.app_context():
        try:
            print("🔧 労働条件変更通知書PDF生成テスト開始")
            
            # 会社設定の確認/作成
            company = CompanySettings.query.first()
            if not company:
                print("📝 会社設定を作成します...")
                company = CompanySettings(
                    company_name="テスト株式会社",
                    representative_name="山田 太郎",
                    company_address="東京都渋谷区テスト町1-2-3",
                    company_phone="03-1234-5678",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.session.add(company)
                db.session.commit()
                print("✅ 会社設定を作成しました")
            
            # テスト用労働条件変更データ
            change_data = {
                'employee': None,  # 新規または既存従業員
                'employee_name': '佐藤 花子',
                'company': company,
                'change_date': '2024年4月1日',
                'change_reason': '昇進・昇格による労働条件の変更',
                'changes': {
                    'position': {
                        'old_value': '営業職',
                        'new_value': '営業主任',
                        'label': '職種・役職'
                    },
                    'department': {
                        'old_value': '営業部',
                        'new_value': '営業1部',
                        'label': '所属部署'
                    },
                    'salary': {
                        'old_value': '250,000円',
                        'new_value': '300,000円',
                        'label': '基本給'
                    }
                },
                'created_by': 'admin',
                'created_date': datetime.now().strftime('%Y年%m月%d日')
            }
            
            print("📄 労働条件変更通知書PDF生成中...")
            pdf_buffer = generate_working_conditions_change_pdf(change_data)
            
            # PDFファイルとして保存
            filename = f'test_working_conditions_change_{change_data["employee_name"].replace(" ", "_")}.pdf'
            with open(filename, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            
            print(f"✅ 労働条件変更通知書PDF生成完了: {filename}")
            print(f"📊 ファイルサイズ: {len(pdf_buffer.getvalue())} bytes")
            
            return True
            
        except Exception as e:
            print(f"❌ エラー発生: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_working_conditions_change_pdf()
    exit(0 if success else 1)
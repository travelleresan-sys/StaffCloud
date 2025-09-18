#!/usr/bin/env python3
from app import app, Employee, db

def fix_residence_files():
    with app.app_context():
        # 田中太郎を画像ファイルに設定
        tanaka = Employee.query.filter_by(name='田中 太郎').first()
        if tanaka:
            tanaka.residence_card_filename = 'sample_residence_card.jpg'
            print(f"田中太郎のファイルを画像に変更: {tanaka.residence_card_filename}")
        
        # 佐藤花子をPDFファイルに設定（既にPDFだが確認）
        sato = Employee.query.filter_by(name='佐藤 花子').first() 
        if sato:
            sato.residence_card_filename = 'sample_residence_card.pdf'
            print(f"佐藤花子のファイルをPDFに設定: {sato.residence_card_filename}")
        
        try:
            db.session.commit()
            print("✓ データベース更新完了")
        except Exception as e:
            print(f"✗ エラー: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    fix_residence_files()
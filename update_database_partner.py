#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import BusinessPartner

def update_database():
    """データベースを更新し、サンプル取引先を追加"""
    
    with app.app_context():
        # データベーステーブルを作成
        db.create_all()
        print("データベーステーブルが作成/更新されました。")
        
        # サンプル取引先データ
        sample_partners = [
            {
                'partner_code': 'CUST001',
                'partner_name': '株式会社A商事',
                'partner_type': '顧客',
                'contact_person': '田中太郎',
                'phone': '03-1234-5678',
                'email': 'tanaka@a-shoji.co.jp'
            },
            {
                'partner_code': 'CUST002',
                'partner_name': 'B工業株式会社',
                'partner_type': '顧客',
                'contact_person': '佐藤花子',
                'phone': '06-2345-6789',
                'email': 'sato@b-kogyo.co.jp'
            },
            {
                'partner_code': 'SUPP001',
                'partner_name': 'C商店',
                'partner_type': '仕入先',
                'contact_person': '鈴木一郎',
                'phone': '052-3456-7890',
                'email': 'suzuki@c-shop.com'
            },
            {
                'partner_code': 'SUPP002',
                'partner_name': 'オフィス用品販売株式会社',
                'partner_type': '仕入先',
                'contact_person': '高橋次郎',
                'phone': '092-4567-8901',
                'email': 'takahashi@office-supply.co.jp'
            },
            {
                'partner_code': 'OTHER001',
                'partner_name': '〇〇銀行',
                'partner_type': 'その他',
                'contact_person': '営業担当',
                'phone': '03-5678-9012',
                'email': 'eigyo@bank.co.jp'
            }
        ]
        
        # サンプル取引先を追加
        for partner_data in sample_partners:
            existing = BusinessPartner.query.filter_by(
                partner_code=partner_data['partner_code']
            ).first()
            
            if not existing:
                partner = BusinessPartner(**partner_data)
                db.session.add(partner)
                print(f"追加: {partner_data['partner_code']} - {partner_data['partner_name']}")
            else:
                print(f"既存: {partner_data['partner_code']} - {partner_data['partner_name']}")
        
        try:
            db.session.commit()
            print("取引先データの追加が完了しました。")
        except Exception as e:
            db.session.rollback()
            print(f"エラー: {e}")

if __name__ == '__main__':
    update_database()
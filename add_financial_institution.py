#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import BusinessPartner

def add_financial_institution():
    """金融機関のサンプルデータを追加"""
    
    # 金融機関のサンプルデータ
    financial_institutions = [
        {
            'partner_code': 'BANK001',
            'partner_name': 'みずほ銀行',
            'partner_type': '金融機関',
            'postal_code': '100-8176',
            'address': '東京都千代田区大手町1-5-5',
            'phone': '03-3596-1111',
            'fax': '03-3596-1112',
            'contact_person': '法人営業部',
            'notes': 'メインバンク'
        },
        {
            'partner_code': 'BANK002',
            'partner_name': '三菱UFJ銀行',
            'partner_type': '金融機関',
            'postal_code': '100-8388',
            'address': '東京都千代田区丸の内2-7-1',
            'phone': '03-3240-1111',
            'fax': '03-3240-1112',
            'contact_person': '中小企業部',
            'notes': 'サブバンク'
        },
        {
            'partner_code': 'CREDIT001',
            'partner_name': '日本政策金融公庫',
            'partner_type': '金融機関',
            'postal_code': '100-0004',
            'address': '東京都千代田区大手町1-9-4',
            'phone': '03-3270-1369',
            'fax': '03-3270-1370',
            'contact_person': '中小企業事業本部',
            'notes': '融資先'
        }
    ]
    
    with app.app_context():
        for institution_data in financial_institutions:
            # 既存の取引先があるかチェック
            existing = BusinessPartner.query.filter_by(
                partner_code=institution_data['partner_code']
            ).first()
            
            if not existing:
                institution = BusinessPartner(**institution_data)
                db.session.add(institution)
                print(f"追加: {institution_data['partner_code']} - {institution_data['partner_name']}")
            else:
                print(f"既存: {institution_data['partner_code']} - {institution_data['partner_name']}")
        
        try:
            db.session.commit()
            print("金融機関データの追加が完了しました。")
        except Exception as e:
            db.session.rollback()
            print(f"エラー: {e}")

if __name__ == '__main__':
    add_financial_institution()
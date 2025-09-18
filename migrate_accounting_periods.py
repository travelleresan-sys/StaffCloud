#!/usr/bin/env python3
"""
会計年度管理テーブルのマイグレーション
新しいAccountingPeriodとOpeningBalanceテーブルを作成します
"""

from app import app, db
from models import AccountingPeriod, OpeningBalance, CompanySettings
from datetime import date

def migrate_accounting_periods():
    """会計年度管理テーブルの作成とサンプルデータ投入"""
    
    with app.app_context():
        try:
            # テーブル作成
            db.create_all()
            print("✓ データベーステーブルを作成しました")
            
            # 企業設定の会計年度設定をデフォルト値で更新
            company_settings = CompanySettings.query.first()
            if company_settings:
                if company_settings.fiscal_year_start_month is None:
                    company_settings.fiscal_year_start_month = 4
                if company_settings.fiscal_year_start_day is None:
                    company_settings.fiscal_year_start_day = 1
                
                db.session.commit()
                print("✓ 企業設定に会計年度設定を追加しました")
            
            # サンプル会計年度を作成（2024年度）
            existing_period = AccountingPeriod.query.filter_by(fiscal_year=2024).first()
            if not existing_period:
                sample_period = AccountingPeriod(
                    fiscal_year=2024,
                    start_date=date(2024, 4, 1),
                    end_date=date(2025, 3, 31),
                    is_closed=False
                )
                db.session.add(sample_period)
                print("✓ 2024年度のサンプル会計期間を作成しました")
            
            # 2025年度も作成
            existing_period_2025 = AccountingPeriod.query.filter_by(fiscal_year=2025).first()
            if not existing_period_2025:
                sample_period_2025 = AccountingPeriod(
                    fiscal_year=2025,
                    start_date=date(2025, 4, 1),
                    end_date=date(2026, 3, 31),
                    is_closed=False
                )
                db.session.add(sample_period_2025)
                print("✓ 2025年度のサンプル会計期間を作成しました")
            
            db.session.commit()
            print("✓ マイグレーションが完了しました")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ マイグレーションでエラーが発生しました: {e}")
            raise

if __name__ == "__main__":
    migrate_accounting_periods()
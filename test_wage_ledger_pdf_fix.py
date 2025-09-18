#!/usr/bin/env python3
"""
賃金台帳PDF生成の修正テスト
employee_numberエラーの修正確認
"""

from models import db, Employee
from wage_register_manager import WageRegisterManager
from wage_ledger_pdf_generator import WageLedgerPDFGenerator
from app import app

def test_wage_ledger_pdf_fix():
    """修正されたemployee_numberエラーをテスト"""
    
    with app.app_context():
        print("=" * 60)
        print("賃金台帳PDF生成修正テスト")
        print("=" * 60)
        
        # 1. 田中太郎の情報を取得
        tanaka = Employee.query.filter_by(name='田中 太郎').first()
        if not tanaka:
            print("❌ 田中太郎が見つかりません")
            return False
        
        print(f"✅ 対象従業員: {tanaka.name} (ID: {tanaka.id})")
        
        # 2. 従業員データを準備（修正後のコード）
        employee_data = {
            'id': tanaka.id,
            'name': tanaka.name,
            'employee_number': f'EMP{tanaka.id:03d}'  # IDベースで従業員番号を生成
        }
        
        print(f"✅ 従業員番号生成: {employee_data['employee_number']}")
        
        # 3. 2023年の賃金データを取得
        wage_manager = WageRegisterManager()
        wage_data = wage_manager.get_wage_register_data(tanaka.id, 2023)
        
        if not wage_data:
            print("❌ 2023年の賃金データが見つかりません")
            return False
        
        print("✅ 2023年賃金データ取得成功")
        
        # 4. PDF生成テスト
        generator = WageLedgerPDFGenerator()
        output_path = 'test_wage_ledger_fix.pdf'
        
        print("\n📄 PDF生成テスト中...")
        
        try:
            success = generator.generate_wage_ledger_pdf(employee_data, wage_data, 2023, output_path)
            
            if success:
                print(f"✅ PDF生成成功: {output_path}")
                
                # ファイルサイズ確認
                import os
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"   ファイルサイズ: {file_size:,} bytes")
                
                return True
            else:
                print("❌ PDF生成失敗")
                return False
                
        except Exception as e:
            print(f"❌ PDF生成エラー: {e}")
            return False

if __name__ == '__main__':
    result = test_wage_ledger_pdf_fix()
    
    print("\n" + "=" * 60)
    print("テスト結果")
    print("=" * 60)
    
    if result:
        print("✅ employee_numberエラーの修正完了")
        print("   - IDベースでemployee_numberを生成")
        print("   - 賃金台帳PDF生成が正常に動作")
    else:
        print("❌ テスト失敗")
    
    import sys
    sys.exit(0 if result else 1)
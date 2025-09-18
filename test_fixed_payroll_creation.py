#!/usr/bin/env python3
"""
修正後の給与明細書作成機能テスト
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_fixed_payroll_creation():
    """修正後の給与明細書作成機能テスト"""
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🔧 修正後の給与明細書作成機能テスト")
    print("=" * 60)
    
    try:
        # ログイン
        login_data = {
            'email': 'accounting@test.com',
            'password': 'accounting123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        if login_response.status_code not in [200, 302]:
            print(f"❌ ログイン失敗: {login_response.status_code}")
            return False
        print("✅ ログイン成功")
        
        # 給与明細作成画面アクセス
        slip_url = f"{base_url}/create_payroll_slip/4/2024/9"
        slip_response = session.get(slip_url)
        
        if slip_response.status_code != 200:
            print(f"❌ 給与明細作成画面アクセス失敗: {slip_response.status_code}")
            return False
        print("✅ 給与明細作成画面アクセス成功")
        
        # 複数の異なるテストケースでテスト
        test_cases = [
            {
                'name': 'ゼロ値テスト',
                'data': {
                    'other_allowance': '0',
                    'income_tax': '0',
                    'resident_tax': '0',
                    'other_deduction': '0',
                    'remarks': 'ゼロ値テスト'
                }
            },
            {
                'name': '通常値テスト',
                'data': {
                    'other_allowance': '5000',
                    'income_tax': '8000',
                    'resident_tax': '12000',
                    'other_deduction': '2000',
                    'remarks': '通常値テスト用給与明細書'
                }
            },
            {
                'name': '高額値テスト',
                'data': {
                    'other_allowance': '50000',
                    'income_tax': '25000',
                    'resident_tax': '18000',
                    'other_deduction': '10000',
                    'remarks': '高額値テスト（役員等）'
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}️⃣ {test_case['name']}")
            
            # フォームデータ準備
            soup = BeautifulSoup(slip_response.text, 'html.parser')
            form_data = test_case['data'].copy()
            
            csrf_token = soup.find('input', {'name': 'csrf_token'})
            if csrf_token:
                form_data['csrf_token'] = csrf_token.get('value')
            
            # POST送信
            create_response = session.post(slip_url, data=form_data)
            
            print(f"   ステータス: {create_response.status_code}")
            content_type = create_response.headers.get('Content-Type', '')
            print(f"   Content-Type: {content_type}")
            
            if 'application/pdf' in content_type:
                pdf_size = len(create_response.content)
                print(f"   ✅ PDF生成成功: {pdf_size} bytes")
                
                # テストケースごとにPDF保存
                filename = f"test_fixed_payroll_{i}.pdf"
                with open(filename, 'wb') as f:
                    f.write(create_response.content)
                print(f"   ✅ PDFファイル '{filename}' を保存")
                
            elif 'text/html' in content_type:
                soup = BeautifulSoup(create_response.text, 'html.parser')
                alerts = soup.find_all('div', class_=['alert', 'alert-danger', 'alert-warning'])
                if alerts:
                    print("   ❌ エラーメッセージ:")
                    for alert in alerts:
                        message = alert.get_text().strip()
                        print(f"     - {message}")
                    return False
                else:
                    print("   ❌ 予期しないHTML応答（エラーメッセージなし）")
                    return False
            else:
                print(f"   ❌ 予期しない Content-Type: {content_type}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    success = test_fixed_payroll_creation()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 修正後の給与明細書作成機能テスト完全成功！")
        print("✅ NoneType演算エラーが修正されました")
        print("✅ 全てのテストケースでPDF生成成功")
        print("✅ 様々な金額パターンでの動作確認済み")
    else:
        print("❌ まだ問題が残っています")
        print("   追加の修正が必要です")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
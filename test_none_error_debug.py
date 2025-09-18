#!/usr/bin/env python3
"""
NoneType演算エラーの詳細デバッグ
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_none_error_debug():
    """NoneType演算エラーの詳細デバッグ"""
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🔍 NoneType演算エラー詳細デバッグ")
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
        
        # フォームデータ準備（最小限）
        soup = BeautifulSoup(slip_response.text, 'html.parser')
        form_data = {}
        
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        if csrf_token:
            form_data['csrf_token'] = csrf_token.get('value')
        
        # 最小限の値でテスト
        form_data.update({
            'other_allowance': '0',
            'income_tax': '0',
            'resident_tax': '0',
            'other_deduction': '0',
            'remarks': ''
        })
        
        print("最小限データでテスト中...")
        create_response = session.post(slip_url, data=form_data)
        
        print(f"レスポンス詳細:")
        print(f"  ステータスコード: {create_response.status_code}")
        print(f"  Content-Type: {create_response.headers.get('Content-Type', 'N/A')}")
        
        if 'text/html' in create_response.headers.get('Content-Type', ''):
            soup = BeautifulSoup(create_response.text, 'html.parser')
            alerts = soup.find_all('div', class_=['alert', 'alert-danger', 'alert-warning', 'alert-success'])
            if alerts:
                print("エラーメッセージ:")
                for alert in alerts:
                    message = alert.get_text().strip()
                    print(f"  - {message}")
                    
                    # NoneType関連のエラーを詳しく解析
                    if 'NoneType' in message:
                        print(f"🔴 NoneTypeエラー検出: {message}")
                        return {'error': message, 'type': 'NoneType'}
        
        elif 'application/pdf' in create_response.headers.get('Content-Type', ''):
            print("✅ PDF生成成功")
            return {'success': True}
        
        return {'unknown': True}
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return {'exception': str(e)}

def main():
    """メイン実行"""
    result = test_none_error_debug()
    
    print(f"\n" + "=" * 60)
    if isinstance(result, dict):
        if 'error' in result:
            print("🔴 NoneTypeエラーが確認されました")
            print(f"エラー内容: {result['error']}")
        elif 'success' in result:
            print("✅ エラーは発生していません")
        else:
            print("⚠️  予期しない結果")
    
    return result

if __name__ == "__main__":
    result = main()
    sys.exit(0)
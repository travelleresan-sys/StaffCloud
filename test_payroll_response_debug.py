#!/usr/bin/env python3
"""
給与明細書作成レスポンスの詳細デバッグ
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_response_debug():
    """給与明細書作成レスポンスの詳細デバッグ"""
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🔍 給与明細書作成レスポンス詳細デバッグ")
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
        
        # 給与明細作成画面アクセス
        slip_url = f"{base_url}/create_payroll_slip/4/2024/9"
        slip_response = session.get(slip_url)
        
        if slip_response.status_code != 200:
            print(f"❌ 給与明細作成画面アクセス失敗: {slip_response.status_code}")
            return False
        
        # フォームデータ準備
        soup = BeautifulSoup(slip_response.text, 'html.parser')
        form_data = {}
        
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        if csrf_token:
            form_data['csrf_token'] = csrf_token.get('value')
        
        form_data.update({
            'other_allowance': '0',
            'income_tax': '5000',
            'resident_tax': '8000',
            'other_deduction': '0',
            'remarks': 'デバッグテスト'
        })
        
        # POST送信
        print("フォーム送信中...")
        create_response = session.post(slip_url, data=form_data)
        
        print(f"レスポンス詳細:")
        print(f"  ステータスコード: {create_response.status_code}")
        print(f"  Content-Type: {create_response.headers.get('Content-Type', 'N/A')}")
        print(f"  Content-Length: {create_response.headers.get('Content-Length', 'N/A')}")
        print(f"  Content-Disposition: {create_response.headers.get('Content-Disposition', 'N/A')}")
        
        # レスポンス内容の確認
        content_type = create_response.headers.get('Content-Type', '')
        
        if 'text/html' in content_type:
            print("\nHTML レスポンス内容:")
            soup = BeautifulSoup(create_response.text, 'html.parser')
            
            # フラッシュメッセージの確認
            alerts = soup.find_all('div', class_=['alert', 'alert-danger', 'alert-warning', 'alert-success'])
            if alerts:
                print("フラッシュメッセージ:")
                for alert in alerts:
                    print(f"  - {alert.get_text().strip()}")
            
            # タイトルの確認
            title = soup.find('title')
            if title:
                print(f"ページタイトル: {title.get_text()}")
            
            # エラー情報の確認
            error_divs = soup.find_all('div', class_='error')
            if error_divs:
                print("エラー情報:")
                for error in error_divs:
                    print(f"  - {error.get_text().strip()}")
            
            # 詳細なHTML構造（最初の1000文字）
            print(f"\nHTML内容（最初の1000文字）:")
            print(create_response.text[:1000])
            
        elif 'application/pdf' in content_type:
            print("✅ PDFレスポンス受信!")
            pdf_size = len(create_response.content)
            print(f"PDFサイズ: {pdf_size} bytes")
            
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    success = test_response_debug()
    
    print(f"\n" + "=" * 60)
    if success:
        print("✅ レスポンス詳細デバッグ完了")
    else:
        print("❌ レスポンス詳細デバッグ失敗")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
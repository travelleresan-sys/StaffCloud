#!/usr/bin/env python3
"""
給与明細作成機能のテスト
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_payroll_slip_creation():
    """給与明細作成機能をテスト"""
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    print("📋 給与明細作成機能テスト")
    print("=" * 60)
    
    try:
        # ログイン
        print("1️⃣ ログイン処理")
        login_data = {
            'email': 'accounting@test.com',
            'password': 'accounting123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        if login_response.status_code not in [200, 302]:
            print(f"❌ ログイン失敗: {login_response.status_code}")
            return False
        
        print("✅ ログイン成功")
        
        # 給与明細作成画面にアクセス
        print("\n2️⃣ 給与明細作成画面アクセス")
        slip_url = f"{base_url}/create_payroll_slip/4/2024/9"  # 月曜起算テスト太郎、2024年9月
        
        slip_response = session.get(slip_url)
        
        if slip_response.status_code == 200:
            print("✅ 給与明細作成画面にアクセス成功")
            
            # HTML解析
            soup = BeautifulSoup(slip_response.text, 'html.parser')
            
            # 従業員名の確認
            if "月曜起算テスト太郎" in slip_response.text:
                print("✅ 従業員名が正しく表示されている")
            else:
                print("❌ 従業員名が表示されていない")
                return False
            
            # 給与データの確認
            if "277,966" in slip_response.text or "250,000" in slip_response.text:
                print("✅ 給与データが表示されている")
            else:
                print("❌ 給与データが表示されていない")
            
            # フォームの存在確認
            form = soup.find('form')
            if form:
                print("✅ 給与明細作成フォームが存在")
                
                # 3️⃣ 給与明細作成（POST）
                print("\n3️⃣ 給与明細作成実行")
                
                # フォームデータを準備
                form_data = {}
                
                # CSRFトークンがある場合は含める
                csrf_token = soup.find('input', {'name': 'csrf_token'})
                if csrf_token:
                    form_data['csrf_token'] = csrf_token.get('value')
                
                # 給与明細作成実行
                create_response = session.post(slip_url, data=form_data)
                
                if create_response.status_code == 200:
                    print("✅ 給与明細作成成功")
                    
                    # 作成結果の確認
                    if "給与明細書" in create_response.text:
                        print("✅ 給与明細書が生成されている")
                    else:
                        print("⚠️  給与明細書の表示を確認してください")
                    
                    return True
                    
                elif create_response.status_code == 500:
                    print("❌ 給与明細作成でサーバーエラー")
                    print("   サーバーログを確認してください")
                    return False
                else:
                    print(f"❌ 予期しないステータスコード: {create_response.status_code}")
                    return False
            else:
                print("❌ 給与明細作成フォームが見つからない")
                return False
            
        elif slip_response.status_code == 404:
            print("❌ 給与明細作成画面が見つかりません（404）")
            print("   URLまたはルーティングを確認してください")
            return False
        elif slip_response.status_code == 500:
            print("❌ 給与明細作成画面でサーバーエラー")
            print("   サーバーログを確認してください")
            return False
        else:
            print(f"❌ 予期しないステータスコード: {slip_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ サーバーに接続できません")
        return False
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    success = test_payroll_slip_creation()
    
    print(f"\n" + "=" * 60)
    if success:
        print("✅ 給与明細作成機能テストが完了しました")
    else:
        print("❌ 給与明細作成機能に問題があります")
        print("   修正が必要です")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
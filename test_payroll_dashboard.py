#!/usr/bin/env python3
"""
給与計算ダッシュボードのエラー調査とテスト
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_payroll_dashboard():
    """給与計算ダッシュボードの動作テスト"""
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🔍 給与計算ダッシュボードエラー調査")
    print("=" * 60)
    
    try:
        # ログイン処理
        login_response = session.get(f"{base_url}/login")
        if login_response.status_code != 200:
            print(f"❌ ログインページアクセス失敗: {login_response.status_code}")
            return False
            
        login_data = {
            'email': 'accounting@test.com',
            'password': 'accounting123'
        }
        
        post_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        if post_response.status_code not in [302, 200]:
            print(f"❌ ログイン失敗: {post_response.status_code}")
            return False
        
        print("✅ ログイン成功")
        
        # 給与計算ダッシュボードにアクセス
        dashboard_response = session.get(f"{base_url}/payroll_dashboard")
        
        if dashboard_response.status_code == 200:
            print("✅ 給与計算ダッシュボードにアクセス成功")
            
            # HTMLを解析
            soup = BeautifulSoup(dashboard_response.text, 'html.parser')
            
            # 従業員選択フォームの確認
            employee_select = soup.find('select', {'name': 'employee_id'})
            if employee_select:
                print("✅ 従業員選択フォームが存在")
                options = employee_select.find_all('option')
                print(f"   従業員選択肢数: {len(options) - 1}件")  # -1は「選択してください」オプション
                
                # 月曜起算テスト太郎が選択肢にあるか確認
                test_employee_found = False
                for option in options:
                    if "月曜起算テスト太郎" in option.text:
                        test_employee_found = True
                        test_employee_id = option.get('value')
                        print(f"✅ テスト従業員が見つかりました: ID={test_employee_id}")
                        break
                
                if not test_employee_found:
                    print("⚠️  テスト従業員が見つかりません")
                    return True  # ダッシュボード自体は正常
            else:
                print("❌ 従業員選択フォームが見つからない")
                return False
                
            # フォーム送信テスト
            if test_employee_found:
                print("\n📊 フォーム送信テスト")
                form_data = {
                    'employee_id': test_employee_id,
                    'year': '2024',
                    'month': '9'
                }
                
                form_response = session.post(f"{base_url}/payroll_dashboard", data=form_data)
                
                if form_response.status_code == 200:
                    print("✅ フォーム送信成功")
                    
                    # エラーメッセージの確認
                    form_soup = BeautifulSoup(form_response.text, 'html.parser')
                    
                    # エラー表示の確認
                    error_messages = form_soup.find_all('div', class_='alert-danger')
                    if error_messages:
                        print("❌ エラーメッセージが検出されました:")
                        for error in error_messages:
                            print(f"   {error.get_text().strip()}")
                        return False
                    
                    # 給与計算結果表示エリアの確認
                    payroll_data_section = form_soup.find('div', id='payroll-results')
                    if payroll_data_section or "給与計算結果" in form_response.text:
                        print("✅ 給与計算結果表示エリアが表示されている")
                    else:
                        print("⚠️  給与計算結果表示エリアが見つからない")
                    
                    # JavaScript エラーの可能性を調査
                    if "error" in form_response.text.lower() or "exception" in form_response.text.lower():
                        print("❌ レスポンス内にエラーの兆候が見つかりました")
                        print("   サーバーログを確認してください")
                        return False
                    
                    return True
                else:
                    print(f"❌ フォーム送信失敗: HTTP {form_response.status_code}")
                    return False
            
            return True
            
        else:
            print(f"❌ 給与計算ダッシュボードアクセス失敗: HTTP {dashboard_response.status_code}")
            print("Response:", dashboard_response.text[:500])
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ サーバーに接続できません")
        print("   Flaskアプリケーションが起動していることを確認してください")
        return False
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    success = test_payroll_dashboard()
    
    print(f"\n" + "=" * 60)
    if success:
        print(f"✅ 給与計算ダッシュボード基本機能テスト完了")
        print(f"   詳細なエラーが発生した場合は、ブラウザで直接確認してください")
        print(f"   URL: http://127.0.0.1:5001/payroll_dashboard")
        print(f"   ログイン: accounting@test.com / accounting123")
    else:
        print(f"❌ テストでエラーが検出されました")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
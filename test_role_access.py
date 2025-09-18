#!/usr/bin/env python3
"""
ロールベースのアクセス制御をテストするスクリプト
"""

import requests
import sys
from requests.sessions import Session

def test_login_and_access(base_url="http://127.0.0.1:5000"):
    """各ロールでのログインとアクセス制御をテスト"""
    
    # テストユーザーの定義
    test_users = {
        'general_affairs': {
            'email': 'general_affairs@example.com',
            'password': 'generalaffairs123',
            'expected_features': ['/general_affairs_36agreement', '/organization_chart', '/company_calendar', '/calendar_view'],
            'blocked_features': ['/performance_evaluation', '/admin_requests']
        },
        'hr_affairs': {
            'email': 'hr_affairs@example.com', 
            'password': 'hraffairs123',
            'expected_features': ['/performance_evaluation', '/admin_requests', '/leave_management'],
            'blocked_features': ['/organization_chart', '/company_calendar', '/general_affairs_36agreement']
        }
    }
    
    print("🧪 ロールベースアクセス制御のテストを開始...")
    
    for role_name, user_data in test_users.items():
        print(f"\n📋 {role_name} ロールのテスト:")
        
        # セッションを作成
        session = Session()
        
        try:
            # ログイン
            login_data = {
                'email': user_data['email'],
                'password': user_data['password']
            }
            
            login_response = session.post(f"{base_url}/admin_login", data=login_data, allow_redirects=False)
            
            if login_response.status_code == 302:  # リダイレクト = ログイン成功
                print(f"   ✅ ログイン成功: {user_data['email']}")
                
                # アクセス許可されるべき機能をテスト
                print("   📝 アクセス許可機能のテスト:")
                for feature_url in user_data['expected_features']:
                    try:
                        response = session.get(f"{base_url}{feature_url}", allow_redirects=False)
                        if response.status_code == 200:
                            print(f"      ✅ {feature_url} - アクセス成功")
                        elif response.status_code == 302:
                            # リダイレクトの場合、エラーページへのリダイレクトかチェック
                            location = response.headers.get('Location', '')
                            if 'dashboard' in location or feature_url in location:
                                print(f"      ✅ {feature_url} - アクセス成功（リダイレクト）")
                            else:
                                print(f"      ⚠️  {feature_url} - 予期しないリダイレクト: {location}")
                        else:
                            print(f"      ❌ {feature_url} - アクセス失敗 (HTTP {response.status_code})")
                    except Exception as e:
                        print(f"      ❌ {feature_url} - エラー: {e}")
                
                # アクセス禁止されるべき機能をテスト  
                print("   🚫 アクセス禁止機能のテスト:")
                for blocked_url in user_data['blocked_features']:
                    try:
                        response = session.get(f"{base_url}{blocked_url}", allow_redirects=False)
                        if response.status_code == 302:
                            location = response.headers.get('Location', '')
                            if 'dashboard' in location:
                                print(f"      ✅ {blocked_url} - 正しくブロック（ダッシュボードにリダイレクト）")
                            else:
                                print(f"      ⚠️  {blocked_url} - 別の場所にリダイレクト: {location}")
                        elif response.status_code == 403:
                            print(f"      ✅ {blocked_url} - 正しくブロック（403 Forbidden）")
                        else:
                            print(f"      ❌ {blocked_url} - ブロックされていません (HTTP {response.status_code})")
                    except Exception as e:
                        print(f"      ❌ {blocked_url} - エラー: {e}")
                        
            else:
                print(f"   ❌ ログイン失敗: {user_data['email']} (HTTP {login_response.status_code})")
                
        except Exception as e:
            print(f"   ❌ テストエラー: {e}")
        finally:
            session.close()
    
    print("\n✨ テスト完了!")

if __name__ == '__main__':
    try:
        test_login_and_access()
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        sys.exit(1)
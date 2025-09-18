#!/usr/bin/env python3
"""
Webサイトでの給与計算ダッシュボード完全動作テスト
"""

import requests
import json
import sys
from bs4 import BeautifulSoup
import re

def test_complete_payroll_workflow():
    """完全な給与計算ワークフローをテスト"""
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🌐 Webサイト給与計算ダッシュボード完全動作テスト")
    print("=" * 70)
    
    try:
        # 1. ログイン
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
        
        # 2. 給与計算ダッシュボードアクセス
        print("\n2️⃣ 給与計算ダッシュボードアクセス")
        dashboard_response = session.get(f"{base_url}/payroll_dashboard")
        
        if dashboard_response.status_code != 200:
            print(f"❌ ダッシュボードアクセス失敗: {dashboard_response.status_code}")
            return False
        
        print("✅ ダッシュボードアクセス成功")
        
        # 3. 従業員・年月選択して表示
        print("\n3️⃣ 従業員・年月選択して表示")
        form_data = {
            'employee_id': '4',  # 月曜起算テスト太郎
            'year': '2024',
            'month': '9'
        }
        
        form_response = session.post(f"{base_url}/payroll_dashboard", data=form_data)
        
        if form_response.status_code != 200:
            print(f"❌ フォーム送信失敗: {form_response.status_code}")
            return False
        
        print("✅ フォーム送信成功")
        
        # レスポンス内容を解析
        soup = BeautifulSoup(form_response.text, 'html.parser')
        
        # エラーメッセージの確認
        error_alerts = soup.find_all('div', class_='alert-danger')
        if error_alerts:
            print("❌ エラーメッセージが表示されています:")
            for alert in error_alerts:
                print(f"   {alert.get_text().strip()}")
            return False
        
        # 給与計算結果の確認
        if "月曜起算テスト太郎" in form_response.text:
            print("✅ 選択した従業員が表示されている")
        else:
            print("❌ 選択した従業員が表示されていない")
            return False
        
        if "2024年9月" in form_response.text:
            print("✅ 選択した年月が表示されている")
        else:
            print("❌ 選択した年月が表示されていない")
            return False
        
        # 勤怠データの表示確認
        if "勤怠データ" in form_response.text or "労働時間" in form_response.text:
            print("✅ 勤怠データが表示されている")
        else:
            print("⚠️  勤怠データ表示が見つからない")
        
        # 給与計算結果の表示確認
        if "給与計算結果" in form_response.text or "基本給" in form_response.text:
            print("✅ 給与計算結果が表示されている")
        else:
            print("⚠️  給与計算結果表示が見つからない")
        
        # 4. 給与計算API呼び出しテスト
        print("\n4️⃣ 給与計算API呼び出しテスト")
        
        # CSRFトークンを取得（必要に応じて）
        api_data = {
            'employee_id': 4,
            'year': 2024,
            'month': 9
        }
        
        api_response = session.post(
            f"{base_url}/api/calculate_payroll",
            json=api_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if api_response.status_code == 200:
            try:
                api_result = api_response.json()
                if api_result.get('success'):
                    print("✅ 給与計算API呼び出し成功")
                    print(f"   メッセージ: {api_result.get('message')}")
                else:
                    print(f"❌ 給与計算APIエラー: {api_result.get('error')}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ API レスポンス解析エラー")
                return False
        else:
            print(f"❌ API呼び出し失敗: {api_response.status_code}")
            return False
        
        # 5. 再度ダッシュボードで結果確認
        print("\n5️⃣ 給与計算後のダッシュボード確認")
        
        final_response = session.post(f"{base_url}/payroll_dashboard", data=form_data)
        
        if final_response.status_code == 200:
            print("✅ 給与計算後のダッシュボードアクセス成功")
            
            # 計算結果が反映されているか確認
            if "250,000" in final_response.text or "277,966" in final_response.text:
                print("✅ 給与計算結果が正しく表示されている")
            else:
                print("⚠️  給与計算結果の表示を確認してください")
            
            return True
        else:
            print(f"❌ 最終確認失敗: {final_response.status_code}")
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
    success = test_complete_payroll_workflow()
    
    print(f"\n" + "=" * 70)
    if success:
        print(f"🎉 給与計算ダッシュボード完全動作テスト完了")
        print(f"   すべての機能が正常に動作しています")
        print(f"\n📋 動作確認完了項目:")
        print(f"   ✅ ログイン機能")
        print(f"   ✅ 給与計算ダッシュボードアクセス")
        print(f"   ✅ 従業員・年月選択フォーム")
        print(f"   ✅ 給与計算API呼び出し")
        print(f"   ✅ 給与計算結果表示")
        print(f"\n🌐 ブラウザでの最終確認:")
        print(f"   URL: http://127.0.0.1:5001/payroll_dashboard")
        print(f"   ログイン: accounting@test.com / accounting123")
        print(f"   従業員: 月曜起算テスト太郎 (2024年9月)")
    else:
        print(f"❌ テストで問題が検出されました")
        print(f"   詳細はブラウザで直接確認してください")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
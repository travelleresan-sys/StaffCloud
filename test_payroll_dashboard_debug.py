#!/usr/bin/env python3
"""
給与計算ダッシュボードのデバッグ - 基本給表示問題
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_payroll_dashboard_debug():
    """給与計算ダッシュボードのデバッグテスト"""
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🔍 給与計算ダッシュボード基本給表示デバッグ")
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
        
        # 給与計算ダッシュボードでフォーム送信
        print("\n2️⃣ 給与計算ダッシュボード確認")
        form_data = {
            'employee_id': '4',  # 月曜起算テスト太郎
            'year': '2024',
            'month': '9'
        }
        
        response = session.post(f"{base_url}/payroll_dashboard", data=form_data)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 基本給の表示を詳細確認
            print("3️⃣ 基本給表示の詳細確認")
            
            # 給与設定セクション全体を抽出
            salary_settings_card = soup.find('div', class_='card')
            if salary_settings_card:
                settings_text = salary_settings_card.get_text()
                print(f"   給与設定カード内容: {settings_text[:200]}...")
            
            # 基本給ラベル周辺を確認
            base_salary_labels = soup.find_all('label', string='基本給')
            for i, label in enumerate(base_salary_labels):
                parent = label.parent
                if parent:
                    sibling = parent.find_next_sibling()
                    if sibling:
                        print(f"   基本給 {i+1}: {sibling.get_text().strip()}")
            
            # 「給与設定が登録されていません」メッセージ確認
            not_registered_msg = soup.find('p', string='給与設定が登録されていません')
            if not_registered_msg:
                print("   ❌ 「給与設定が登録されていません」が表示されています")
                # 周辺のHTML構造を確認
                parent = not_registered_msg.parent
                print(f"   メッセージの親要素: {parent.name if parent else 'None'}")
                if parent:
                    print(f"   親要素のクラス: {parent.get('class', [])}")
            else:
                print("   ✅ 「給与設定が登録されていません」は表示されていません")
            
            # 金額表示の検索
            print("\n4️⃣ 金額表示確認")
            amounts = ['250,000', '¥250,000', '250000']
            for amount in amounts:
                if amount in response.text:
                    print(f"   ✅ {amount} が見つかりました")
                    # 該当箇所を抽出
                    soup_str = str(soup)
                    start = soup_str.find(amount)
                    if start != -1:
                        context = soup_str[max(0, start-100):start+100]
                        print(f"   コンテキスト: ...{context}...")
                else:
                    print(f"   ❌ {amount} が見つかりません")
            
            # HTML構造の確認
            print("\n5️⃣ 給与設定セクションのHTML構造")
            settings_sections = soup.find_all('div', class_='card-body')
            for i, section in enumerate(settings_sections):
                if '給与設定' in section.get_text() or '基本給' in section.get_text():
                    print(f"   セクション {i+1}:")
                    print(f"   {section.prettify()[:300]}...")
            
            return True
            
        else:
            print(f"❌ ダッシュボードアクセス失敗: {response.status_code}")
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
    success = test_payroll_dashboard_debug()
    
    print(f"\n" + "=" * 60)
    if success:
        print("✅ デバッグテストが完了しました")
    else:
        print("❌ デバッグテストに失敗しました")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
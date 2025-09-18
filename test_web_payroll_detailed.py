#!/usr/bin/env python3
"""
Webサイトでの給与計算ダッシュボード詳細テスト
"""

import requests
import sys
from bs4 import BeautifulSoup
import re

def test_payroll_dashboard_detailed():
    """給与計算ダッシュボードの詳細テスト"""
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    print("🌐 給与計算ダッシュボード詳細テスト")
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
        
        # 給与計算ダッシュボードにフォーム送信
        print("\n2️⃣ 給与計算ダッシュボードフォーム送信")
        form_data = {
            'employee_id': '4',  # 月曜起算テスト太郎
            'year': '2024',
            'month': '9'
        }
        
        response = session.post(f"{base_url}/payroll_dashboard", data=form_data)
        
        if response.status_code == 200:
            print("✅ フォーム送信成功")
            
            # HTML解析
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 給与設定セクションの確認
            print("\n3️⃣ 給与設定セクションの確認")
            
            # 「給与設定が登録されていません」メッセージの確認
            not_registered_msg = soup.find('p', string=re.compile('給与設定が登録されていません'))
            if not_registered_msg:
                print("❌ 「給与設定が登録されていません」メッセージが表示されています")
                print("   これは問題です - 設定は存在するはずです")
                
                # 周辺のHTMLを確認
                parent = not_registered_msg.parent
                print(f"   親要素: {parent}")
                
                return False
            else:
                print("✅ 「給与設定が登録されていません」メッセージは表示されていません")
            
            # 基本給の表示確認
            base_salary_elements = soup.find_all(string=re.compile('250,000|基本給'))
            if base_salary_elements:
                print("✅ 基本給関連の表示が見つかりました:")
                for element in base_salary_elements[:3]:  # 最初の3つだけ表示
                    print(f"   - {element.strip()}")
            else:
                print("❌ 基本給の表示が見つかりません")
            
            # 給与計算結果の確認
            print("\n4️⃣ 給与計算結果の確認")
            
            # 総支給額の確認
            gross_salary_elements = soup.find_all(string=re.compile('277,966|総支給額'))
            if gross_salary_elements:
                print("✅ 総支給額関連の表示が見つかりました:")
                for element in gross_salary_elements[:3]:
                    print(f"   - {element.strip()}")
            else:
                print("⚠️  総支給額の表示が見つかりません")
            
            # エラーメッセージの確認
            print("\n5️⃣ エラーメッセージの確認")
            error_messages = soup.find_all('div', class_=['alert-danger', 'alert-warning'])
            if error_messages:
                print("⚠️  警告/エラーメッセージが見つかりました:")
                for msg in error_messages:
                    print(f"   - {msg.get_text().strip()}")
            else:
                print("✅ エラーメッセージは表示されていません")
            
            # HTML内のJavaScriptエラーの確認
            print("\n6️⃣ JavaScript関連の確認")
            if 'recalculatePayroll' in response.text:
                print("✅ 給与再計算の JavaScript 関数が存在")
            else:
                print("❌ 給与再計算の JavaScript 関数が見つからない")
            
            # レスポンス内容の一部を表示（デバッグ用）
            print(f"\n📄 レスポンス概要:")
            print(f"   ステータスコード: {response.status_code}")
            print(f"   レスポンスサイズ: {len(response.text)} 文字")
            print(f"   「月曜起算テスト太郎」含有: {'月曜起算テスト太郎' in response.text}")
            print(f"   「250,000」含有: {'250,000' in response.text}")
            print(f"   「payroll_data」含有: {'payroll_data' in response.text}")
            
            return True
            
        elif response.status_code == 500:
            print(f"❌ サーバーエラー: {response.status_code}")
            print("   サーバーログを確認してください")
            return False
        else:
            print(f"❌ 予期しないステータスコード: {response.status_code}")
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
    success = test_payroll_dashboard_detailed()
    
    print(f"\n" + "=" * 60)
    if success:
        print("✅ 詳細テストが完了しました")
        print("   ブラウザでの確認も推奨します")
    else:
        print("❌ 問題が検出されました")
        print("   修正が必要です")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
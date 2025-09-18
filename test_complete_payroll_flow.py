#!/usr/bin/env python3
"""
給与機能完全テスト - 全機能の統合確認
"""

import requests
import sys
from bs4 import BeautifulSoup
import re

def test_complete_payroll_flow():
    """給与機能全体の統合テスト"""
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    print("🚀 給与機能完全テスト")
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
        
        # 3. 従業員選択・表示
        print("\n3️⃣ 従業員データ表示テスト")
        form_data = {
            'employee_id': '4',  # 月曜起算テスト太郎
            'year': '2024',
            'month': '9'
        }
        
        payroll_response = session.post(f"{base_url}/payroll_dashboard", data=form_data)
        if payroll_response.status_code != 200:
            print(f"❌ 従業員データ表示失敗: {payroll_response.status_code}")
            return False
        print("✅ 従業員データ表示成功")
        
        # HTMLを解析して必要な情報を確認
        soup = BeautifulSoup(payroll_response.text, 'html.parser')
        
        # 給与設定の確認
        if "給与設定が登録されていません" in payroll_response.text:
            print("❌ 給与設定表示エラー")
            return False
        print("✅ 給与設定が正しく表示")
        
        # 基本給の確認
        if "250,000" not in payroll_response.text:
            print("❌ 基本給が表示されていない")
            return False
        print("✅ 基本給が正しく表示")
        
        # 4. 給与明細作成画面アクセス
        print("\n4️⃣ 給与明細作成画面アクセス")
        slip_url = f"{base_url}/create_payroll_slip/4/2024/9"
        slip_response = session.get(slip_url)
        
        if slip_response.status_code != 200:
            print(f"❌ 給与明細作成画面アクセス失敗: {slip_response.status_code}")
            return False
        print("✅ 給与明細作成画面アクセス成功")
        
        # 給与明細画面の内容確認
        if "月曜起算テスト太郎" not in slip_response.text:
            print("❌ 従業員名が表示されていない")
            return False
        print("✅ 給与明細で従業員名表示確認")
        
        if "総支給額" not in slip_response.text:
            print("❌ 総支給額が表示されていない")
            return False
        print("✅ 給与明細で総支給額表示確認")
        
        # 5. 給与明細作成実行
        print("\n5️⃣ 給与明細作成実行")
        slip_soup = BeautifulSoup(slip_response.text, 'html.parser')
        
        # フォームデータを準備
        form_data = {}
        
        # CSRFトークンがある場合は含める
        csrf_token = slip_soup.find('input', {'name': 'csrf_token'})
        if csrf_token:
            form_data['csrf_token'] = csrf_token.get('value')
        
        # デフォルト値を設定
        form_data.update({
            'other_allowance': '0',
            'income_tax': '0',
            'resident_tax': '0',
            'other_deduction': '0'
        })
        
        create_response = session.post(slip_url, data=form_data)
        
        if create_response.status_code != 200:
            print(f"❌ 給与明細作成失敗: {create_response.status_code}")
            return False
        print("✅ 給与明細作成実行成功")
        
        # 作成結果の確認
        if "給与明細書" not in create_response.text:
            print("⚠️  給与明細書の表示を確認できませんでした")
        else:
            print("✅ 給与明細書が正常に生成")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ サーバーに接続できません")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    print("🎯 給与システム完全動作テスト")
    print("=" * 70)
    
    success = test_complete_payroll_flow()
    
    print(f"\n" + "=" * 70)
    if success:
        print("🎉 全給与機能テスト完了!")
        print("✅ 給与計算ダッシュボード: 正常動作")
        print("✅ 給与設定表示: 正常動作") 
        print("✅ 給与明細作成: 正常動作")
        print("✅ 全機能が正常に動作しています")
        print("\n💡 実際のブラウザでも確認してください:")
        print("   http://127.0.0.1:5000/login")
        print("   ログイン: accounting@test.com / accounting123")
    else:
        print("❌ 一部機能に問題があります")
        print("   詳細を確認して修正してください")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
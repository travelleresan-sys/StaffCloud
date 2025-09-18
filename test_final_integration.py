#!/usr/bin/env python3
"""
最終統合テスト - 全給与機能の動作確認
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_final_integration():
    """全給与機能の最終統合テスト"""
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🚀 給与システム最終統合テスト")
    print("=" * 70)
    
    try:
        # 1. ログイン
        print("1️⃣ ログイン機能テスト")
        login_data = {
            'email': 'accounting@test.com',
            'password': 'accounting123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        if login_response.status_code not in [200, 302]:
            print(f"❌ ログイン失敗: {login_response.status_code}")
            return False
        print("✅ ログイン成功")
        
        # 2. 給与計算ダッシュボード機能
        print("\n2️⃣ 給与計算ダッシュボード機能テスト")
        
        # ダッシュボードアクセス
        dashboard_response = session.get(f"{base_url}/payroll_dashboard")
        if dashboard_response.status_code != 200:
            print(f"❌ ダッシュボードアクセス失敗")
            return False
        print("✅ ダッシュボードアクセス成功")
        
        # 従業員選択・表示
        form_data = {
            'employee_id': '4',
            'year': '2024',
            'month': '9'
        }
        
        payroll_response = session.post(f"{base_url}/payroll_dashboard", data=form_data)
        if payroll_response.status_code != 200:
            print(f"❌ 従業員データ表示失敗")
            return False
            
        # 給与設定表示確認
        if "給与設定が登録されていません" in payroll_response.text:
            print("❌ 給与設定表示エラー")
            return False
        
        if "250,000" not in payroll_response.text:
            print("❌ 基本給表示エラー")
            return False
            
        print("✅ 給与設定・基本給表示正常")
        
        # 3. 給与明細作成機能
        print("\n3️⃣ 給与明細書作成機能テスト")
        
        slip_url = f"{base_url}/create_payroll_slip/4/2024/9"
        slip_response = session.get(slip_url)
        
        if slip_response.status_code != 200:
            print(f"❌ 給与明細作成画面アクセス失敗")
            return False
        print("✅ 給与明細作成画面アクセス成功")
        
        # フォームデータ準備・送信
        soup = BeautifulSoup(slip_response.text, 'html.parser')
        form_data = {}
        
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        if csrf_token:
            form_data['csrf_token'] = csrf_token.get('value')
        
        form_data.update({
            'other_allowance': '5000',  # その他手当
            'income_tax': '8000',       # 所得税
            'resident_tax': '12000',    # 住民税
            'other_deduction': '2000',  # その他控除
            'remarks': '最終統合テスト用給与明細書'
        })
        
        create_response = session.post(slip_url, data=form_data)
        
        # 4. PDF生成・ダウンロード機能
        print("\n4️⃣ PDF生成・ダウンロード機能テスト")
        
        if create_response.status_code != 200:
            print(f"❌ 給与明細作成失敗: {create_response.status_code}")
            return False
        
        content_type = create_response.headers.get('Content-Type', '')
        if 'application/pdf' not in content_type:
            print(f"❌ PDF生成失敗: Content-Type = {content_type}")
            return False
        
        pdf_size = len(create_response.content)
        if pdf_size < 1000:
            print(f"❌ PDF生成不完全: サイズ {pdf_size} bytes")
            return False
        
        print(f"✅ PDF生成成功: {pdf_size} bytes")
        
        # ファイル名確認
        disposition = create_response.headers.get('Content-Disposition', '')
        if 'payroll_slip_emp4_2024_09.pdf' not in disposition:
            print(f"❌ PDFファイル名エラー: {disposition}")
            return False
        
        print("✅ PDFファイル名正常")
        
        # 最終PDFファイル保存
        with open('final_integration_test.pdf', 'wb') as f:
            f.write(create_response.content)
        print("✅ 最終テスト用PDFファイル 'final_integration_test.pdf' を保存")
        
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
    success = test_final_integration()
    
    print(f"\n" + "=" * 70)
    if success:
        print("🎉 給与システム最終統合テスト完全成功！")
        print()
        print("✅ 実装完了した機能:")
        print("   1. 給与設定の基本給表示機能")
        print("   2. 給与明細書作成時のデータ保存機能")  
        print("   3. 給与明細書のPDF自動生成・ダウンロード機能")
        print("   4. 全機能の統合動作")
        print()
        print("🚀 システムの特徴:")
        print("   • 給与計算ダッシュボードで従業員の給与設定が正しく表示")
        print("   • 給与明細書作成ボタンでデータ保存とPDF生成を同時実行")
        print("   • 日本語対応PDF生成（ReportLabベース）")
        print("   • ファイル名のUnicode問題を解決")
        print("   • エラーハンドリングによる安定動作")
        print()
        print("💡 使用方法:")
        print("   1. ブラウザで http://127.0.0.1:5001/login にアクセス")
        print("   2. 経理ユーザーでログイン: accounting@test.com / accounting123")
        print("   3. 給与計算ダッシュボードで従業員・年月を選択")
        print("   4. 給与明細書作成ボタンをクリック")
        print("   5. 自動でPDFがダウンロード開始")
    else:
        print("❌ 最終統合テストで問題が発生しました")
        print("   再度確認・修正が必要です")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
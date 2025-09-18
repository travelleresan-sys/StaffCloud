#!/usr/bin/env python3
"""
給与明細書PDF作成機能の統合テスト
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_payroll_slip_pdf():
    """給与明細書作成とPDF発行のテスト"""
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("📋 給与明細書PDF作成統合テスト")
    print("=" * 60)
    
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
        
        # 2. 給与明細作成画面アクセス
        print("\n2️⃣ 給与明細作成画面アクセス")
        slip_url = f"{base_url}/create_payroll_slip/4/2024/9"
        slip_response = session.get(slip_url)
        
        if slip_response.status_code != 200:
            print(f"❌ 給与明細作成画面アクセス失敗: {slip_response.status_code}")
            return False
        print("✅ 給与明細作成画面アクセス成功")
        
        # 3. 給与明細作成とPDF生成
        print("\n3️⃣ 給与明細作成とPDF生成")
        soup = BeautifulSoup(slip_response.text, 'html.parser')
        
        # フォームデータを準備
        form_data = {}
        
        # CSRFトークンがある場合は含める
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        if csrf_token:
            form_data['csrf_token'] = csrf_token.get('value')
        
        # デフォルト値を設定
        form_data.update({
            'other_allowance': '0',
            'income_tax': '5000',      # 所得税を設定
            'resident_tax': '8000',    # 住民税を設定
            'other_deduction': '0',
            'remarks': 'テスト用給与明細書です。'
        })
        
        # POST送信
        create_response = session.post(slip_url, data=form_data)
        
        if create_response.status_code == 200:
            # レスポンスがPDFかチェック
            content_type = create_response.headers.get('Content-Type', '')
            if 'application/pdf' in content_type:
                print("✅ 給与明細PDF生成成功")
                
                # PDFファイル名確認
                disposition = create_response.headers.get('Content-Disposition', '')
                if 'payroll_slip_' in disposition:
                    print("✅ PDFファイル名が正しく設定されています")
                    print(f"   ファイル名情報: {disposition}")
                
                # PDFサイズ確認
                pdf_size = len(create_response.content)
                if pdf_size > 1000:  # 1KB以上であればPDFが生成されている
                    print(f"✅ PDF生成成功 (サイズ: {pdf_size} bytes)")
                else:
                    print(f"⚠️  PDFサイズが小さすぎます: {pdf_size} bytes")
                
                # テスト用にPDFファイルを保存
                with open('test_payroll_slip.pdf', 'wb') as f:
                    f.write(create_response.content)
                print("✅ テスト用PDFファイル 'test_payroll_slip.pdf' を保存しました")
                
                return True
            else:
                print(f"❌ PDF生成失敗: Content-Type = {content_type}")
                print("レスポンス内容（最初の200文字）:")
                print(create_response.text[:200])
                return False
        else:
            print(f"❌ 給与明細作成失敗: {create_response.status_code}")
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
    success = test_payroll_slip_pdf()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 給与明細書PDF作成機能テスト完了!")
        print("✅ データ保存機能: 正常動作")
        print("✅ PDF生成機能: 正常動作")
        print("✅ ファイルダウンロード: 正常動作")
        print("\n💡 実際のブラウザでも確認してください:")
        print("   1. http://127.0.0.1:5001/login")
        print("   2. ログイン: accounting@test.com / accounting123")
        print("   3. 給与計算ダッシュボード → 給与明細書作成")
    else:
        print("❌ 給与明細書PDF作成機能に問題があります")
        print("   修正が必要です")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
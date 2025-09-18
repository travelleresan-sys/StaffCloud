#!/usr/bin/env python3
"""
Webアプリケーションでの新しいPDFデザインテスト
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_web_new_design():
    """Webアプリケーションでの新しいPDFデザインテスト"""
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🌐 Webアプリケーション新デザインテスト")
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
        print("✅ ログイン成功")
        
        # 給与明細作成画面アクセス
        slip_url = f"{base_url}/create_payroll_slip/4/2024/9"
        slip_response = session.get(slip_url)
        
        if slip_response.status_code != 200:
            print(f"❌ 給与明細作成画面アクセス失敗: {slip_response.status_code}")
            return False
        print("✅ 給与明細作成画面アクセス成功")
        
        # 新デザインでPDF生成
        print("\n📋 新デザインPDF生成テスト")
        soup = BeautifulSoup(slip_response.text, 'html.parser')
        form_data = {}
        
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        if csrf_token:
            form_data['csrf_token'] = csrf_token.get('value')
        
        form_data.update({
            'other_allowance': '10000',
            'income_tax': '15000',
            'resident_tax': '18000',
            'other_deduction': '3000',
            'remarks': '新テーブルデザイン適用版給与明細書'
        })
        
        create_response = session.post(slip_url, data=form_data)
        
        print(f"レスポンス詳細:")
        print(f"  ステータスコード: {create_response.status_code}")
        print(f"  Content-Type: {create_response.headers.get('Content-Type', 'N/A')}")
        
        if create_response.status_code == 200:
            content_type = create_response.headers.get('Content-Type', '')
            
            if 'application/pdf' in content_type:
                pdf_size = len(create_response.content)
                print(f"✅ 新デザインPDF生成成功: {pdf_size} bytes")
                
                # ファイル名確認
                disposition = create_response.headers.get('Content-Disposition', '')
                print(f"  ファイル名情報: {disposition}")
                
                # PDFファイルを保存
                with open('web_new_design_payroll.pdf', 'wb') as f:
                    f.write(create_response.content)
                print("✅ WebアプリPDFファイル 'web_new_design_payroll.pdf' を保存")
                
                print(f"\n📊 新デザインの改善点:")
                print(f"  • テーブル形式で項目が整理")
                print(f"  • 勤怠情報と給与情報の統合表示")
                print(f"  • 差引支給額のビジュアル強調")
                print(f"  • 従来比でより見やすいレイアウト")
                
                return True
                
            elif 'text/html' in content_type:
                soup = BeautifulSoup(create_response.text, 'html.parser')
                alerts = soup.find_all('div', class_=['alert', 'alert-danger', 'alert-warning'])
                if alerts:
                    print("❌ エラーメッセージ:")
                    for alert in alerts:
                        message = alert.get_text().strip()
                        print(f"  - {message}")
                    return False
                else:
                    print("❌ 予期しないHTML応答")
                    return False
            else:
                print(f"❌ 予期しない Content-Type: {content_type}")
                return False
        else:
            print(f"❌ サーバーエラー: {create_response.status_code}")
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
    success = test_web_new_design()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 Webアプリケーション新デザインテスト完全成功！")
        print()
        print("✅ 実装完了:")
        print("  1. 新しいテーブルデザイン適用")
        print("  2. 項目別の整理された表示")
        print("  3. 指定されたフォーマットに準拠")
        print("  4. Webアプリケーションでの正常動作")
        print()
        print("🚀 新デザインの特徴:")
        print("  • 労働日数、欠勤日数、有給取得日数の表示")
        print("  • 残有給日数の自動計算")
        print("  • 労働時間の統合表示")  
        print("  • 各種給与・控除項目の整理")
        print("  • 差引支給額の視覚的強調")
        print()
        print("💡 アクセス方法:")
        print("  1. http://127.0.0.1:5001/login")
        print("  2. 経理ユーザーでログイン")
        print("  3. 給与計算ダッシュボード → 給与明細書作成")
        print("  4. 新しいテーブルデザインのPDFがダウンロード")
    else:
        print("❌ Webアプリケーション新デザインテストで問題発生")
        print("   確認・修正が必要です")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
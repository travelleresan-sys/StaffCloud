#!/usr/bin/env python3
"""
給与計算ダッシュボードのレスポンス詳細調査
"""

import requests
import sys

def debug_payroll_response():
    """給与計算ダッシュボードのレスポンス詳細調査"""
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🔍 給与計算ダッシュボードレスポンス詳細調査")
    print("=" * 60)
    
    try:
        # ログイン処理
        login_data = {
            'email': 'accounting@test.com',
            'password': 'accounting123'
        }
        
        session.post(f"{base_url}/login", data=login_data)
        
        # フォーム送信
        form_data = {
            'employee_id': '4',  # 月曜起算テスト太郎
            'year': '2024',
            'month': '9'
        }
        
        response = session.post(f"{base_url}/payroll_dashboard", data=form_data)
        
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンスサイズ: {len(response.text)} 文字")
        
        # エラーメッセージの検索
        error_keywords = ['error', 'exception', 'traceback', 'Error:', 'Exception:', 'Traceback']
        
        content_lower = response.text.lower()
        found_errors = []
        
        for keyword in error_keywords:
            if keyword.lower() in content_lower:
                found_errors.append(keyword)
        
        if found_errors:
            print(f"\n❌ 検出されたエラーキーワード: {', '.join(found_errors)}")
            
            # エラーの詳細を抽出
            lines = response.text.split('\n')
            error_lines = []
            
            for i, line in enumerate(lines):
                for keyword in error_keywords:
                    if keyword.lower() in line.lower():
                        # 前後の行も含めて表示
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        error_context = lines[start:end]
                        error_lines.extend(error_context)
                        break
            
            if error_lines:
                print("\n❌ エラーの詳細:")
                for line in error_lines[:20]:  # 最大20行まで表示
                    print(f"   {line.strip()}")
                    
                # エラーがHTMLコメントや非表示部分にある場合
                if "<!--" in response.text and "-->" in response.text:
                    print("\n⚠️  HTMLコメント内にエラー情報がある可能性があります")
        else:
            print("✅ 明らかなエラーメッセージは見つかりませんでした")
        
        # 給与データが表示されているか確認
        if "payroll_data" in response.text or "給与計算結果" in response.text:
            print("✅ 給与データ関連のコンテンツが含まれています")
        else:
            print("⚠️  給与データ関連のコンテンツが見つかりません")
        
        # JavaScriptエラーの可能性を調査
        if "console.error" in response.text or "throw" in response.text:
            print("⚠️  JavaScriptエラーの可能性があります")
        
        # 部分的なHTMLを表示（デバッグ用）
        if len(response.text) > 1000:
            print(f"\n📄 レスポンス一部（最初の500文字）:")
            print(response.text[:500])
            print(f"\n📄 レスポンス一部（最後の500文字）:")
            print(response.text[-500:])
        else:
            print(f"\n📄 完全なレスポンス:")
            print(response.text)
            
        return response.text
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_payroll_response()
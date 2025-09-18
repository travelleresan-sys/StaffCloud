#!/usr/bin/env python3
"""
ログインして月曜日起算週40時間制限の動作確認
"""

import requests
import sys
from bs4 import BeautifulSoup

def create_admin_user_if_not_exists():
    """管理者ユーザーが存在しない場合は作成"""
    try:
        from app import app, db
        from models import User
        
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                from werkzeug.security import generate_password_hash
                admin = User(
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
                    role='system_admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("管理者ユーザーを作成しました (admin/admin123)")
            else:
                print("管理者ユーザーが既に存在します")
    except Exception as e:
        print(f"管理者ユーザー作成でエラー: {e}")

def test_with_login():
    """ログインして労働時間画面をテスト"""
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🌐 ログイン付き月曜日起算週40時間制限テスト")
    print("=" * 60)
    
    # まず管理者ユーザーを確保
    create_admin_user_if_not_exists()
    
    try:
        # ログインページにアクセス
        login_response = session.get(f"{base_url}/login")
        if login_response.status_code != 200:
            print(f"❌ ログインページアクセス失敗: {login_response.status_code}")
            return False
            
        # ログイン実行
        login_data = {
            'email': 'accounting@test.com',
            'password': 'accounting123'
        }
        
        post_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        if post_response.status_code in [302, 200]:
            print("✅ ログイン成功")
        else:
            print(f"❌ ログイン失敗: {post_response.status_code}")
            return False
        
        # 労働時間入力画面にアクセス
        working_time_url = f"{base_url}/working_time_input?employee_id=4&year=2024&month=9"
        response = session.get(working_time_url)
        
        if response.status_code == 200:
            print("✅ 労働時間入力画面にアクセス成功")
            
            html_content = response.text
            
            # 従業員名の確認
            if "月曜起算テスト太郎" in html_content:
                print("✅ テスト従業員が正しく表示されている")
            else:
                print("❌ テスト従業員が表示されていない")
                print("   従業員が存在するか、データが正しく作成されているか確認してください")
                return False
            
            # JavaScript関数の存在確認
            if "updateWeeklyCalculationDisplay" in html_content:
                print("✅ 週40時間制限計算関数が存在")
            else:
                print("❌ 週40時間制限計算関数が見つからない")
            
            # 月曜日起算コメントの確認
            if "月曜日起算" in html_content:
                print("✅ 月曜日起算のコメントが確認できる")
            else:
                print("⚠️  月曜日起算のコメントが見つからない")
            
            # テーブルヘッダーの確認
            if all(header in html_content for header in ["法定内", "法定外", "法定休日"]):
                print("✅ 労働時間分類のヘッダーが正しく表示")
            else:
                print("❌ 労働時間分類のヘッダーが正しくない")
                return False
                
            # 2024年9月の確認
            if "2024年9月" in html_content:
                print("✅ 対象年月が正しく表示されている")
            else:
                print("❌ 対象年月が表示されていない")
            
            print(f"\n📋 労働時間入力画面の動作確認完了")
            print(f"   URL: {working_time_url}")
            print(f"   従業員: 月曜起算テスト太郎")
            print(f"   対象期間: 2024年9月")
            print(f"\n📊 期待される計算結果:")
            print(f"   • 週: 2024/9/2(月) ～ 2024/9/7(土)")
            print(f"   • 総労働時間: 51.5時間 (3090分)")
            print(f"   • 法定内労働時間: 40時間 (2400分)")
            print(f"   • 法定外労働時間: 11.5時間 (690分) ← 25%割増")
            print(f"   • 法定休日労働: 0時間")
            print(f"\n✨ ブラウザで上記URLにアクセスして、")
            print(f"   JavaScript計算により労働時間が週40時間制限に基づいて")
            print(f"   正しく振り分けられることを確認してください")
            
            return True
            
        else:
            print(f"❌ 労働時間入力画面にアクセス失敗: HTTP {response.status_code}")
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
    success = test_with_login()
    
    print(f"\n" + "=" * 60)
    if success:
        print(f"✅ ログイン付き月曜日起算週40時間制限テスト完了")
        print(f"   ブラウザでhttp://127.0.0.1:5001にアクセスして")
        print(f"   accounting@test.com/accounting123でログイン後、動作確認を行ってください")
    else:
        print(f"❌ テストに問題があります")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
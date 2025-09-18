#!/usr/bin/env python3
"""
WEB画面での月曜日起算週40時間制限の動作確認
"""

import requests
import sys
import re

def test_web_interface():
    """WEB画面での労働時間計算テスト"""
    base_url = "http://127.0.0.1:5001"
    
    print("🌐 WEB画面での月曜日起算週40時間制限テスト")
    print("=" * 60)
    
    try:
        # 労働時間入力画面にアクセス
        response = requests.get(f"{base_url}/working_time_input?employee_id=4&year=2024&month=9")
        
        if response.status_code == 200:
            print("✅ 労働時間入力画面にアクセス成功")
            
            # HTMLから労働時間表示部分を検証
            html_content = response.text
            
            # JavaScript関数の存在確認
            if "updateWeeklyCalculationDisplay" in html_content:
                print("✅ 週40時間制限計算関数が存在")
            else:
                print("❌ 週40時間制限計算関数が見つからない")
                return False
            
            # 月曜日起算コメントの確認
            if "月曜日起算" in html_content:
                print("✅ 月曜日起算のコメントが確認できる")
            else:
                print("⚠️  月曜日起算のコメントが見つからない")
            
            # テーブルヘッダーの確認
            if "法定内" in html_content and "法定外" in html_content and "法定休日" in html_content:
                print("✅ 労働時間分類のヘッダーが正しく表示")
            else:
                print("❌ 労働時間分類のヘッダーが正しくない")
                return False
            
            # 従業員名の確認
            if "月曜起算テスト太郎" in html_content:
                print("✅ テスト従業員が正しく選択されている")
            else:
                print("❌ テスト従業員が選択されていない")
                return False
            
            print(f"\n📋 労働時間入力画面の動作確認完了")
            print(f"   URL: {base_url}/working_time_input?employee_id=4&year=2024&month=9")
            print(f"   従業員: 月曜起算テスト太郎")
            print(f"   対象期間: 2024年9月")
            print(f"\n📊 期待される計算結果:")
            print(f"   • 総労働時間: 51.5時間 (3090分)")
            print(f"   • 法定内労働時間: 40時間 (2400分)")
            print(f"   • 法定外労働時間: 11.5時間 (690分) ← 25%割増")
            print(f"   • 法定休日労働: 0時間")
            print(f"\n✨ ブラウザで上記URLにアクセスして、")
            print(f"   月曜日（9/2）から土曜日（9/7）の労働時間が")
            print(f"   週40時間制限に基づいて正しく振り分けられることを確認してください")
            
            return True
            
        else:
            print(f"❌ 労働時間入力画面にアクセス失敗: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ サーバーに接続できません")
        print("   Flaskアプリケーションが起動していることを確認してください")
        print(f"   python -m flask --app app run --port 5001")
        return False
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def main():
    """メイン実行"""
    success = test_web_interface()
    
    print(f"\n" + "=" * 60)
    if success:
        print(f"✅ WEB画面での月曜日起算週40時間制限テスト完了")
        print(f"   ブラウザでの動作確認を行ってください")
    else:
        print(f"❌ テストに問題があります")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
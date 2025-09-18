#!/usr/bin/env python3
"""
flask runコマンドの連続テスト

ポート競合エラーが発生しないか複数回テスト
"""

import subprocess
import time
import os
import signal
import sys

def test_flask_run():
    """flask runの連続テスト"""
    print("flask run 連続テスト開始")
    print("=" * 50)
    
    test_count = 5
    success_count = 0
    
    for i in range(1, test_count + 1):
        print(f"\nテスト {i}/{test_count}: flask run 起動テスト")
        
        try:
            # 仮想環境でflask runを起動
            env = os.environ.copy()
            env['VIRTUAL_ENV'] = '/home/esan/employee-db/venv'
            env['PATH'] = '/home/esan/employee-db/venv/bin:' + env['PATH']
            
            # バックグラウンドでflask runを起動
            process = subprocess.Popen(
                ['flask', 'run'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd='/home/esan/employee-db'
            )
            
            print("  Flaskプロセス起動中...")
            time.sleep(3)  # 起動待機
            
            # プロセスが正常に起動しているかチェック
            if process.poll() is None:
                print("  ✅ 正常に起動しました")
                success_count += 1
                
                # ポート確認
                result = subprocess.run(['lsof', '-ti:5000'], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  📋 ポート5000使用中 (PID: {result.stdout.strip()})")
                else:
                    print("  ⚠️  ポート5000が検出されませんでした")
                
            else:
                # エラーメッセージを取得
                stdout, stderr = process.communicate()
                print(f"  ❌ 起動に失敗しました")
                print(f"  エラー: {stderr.decode()}")
            
            # プロセスを停止
            if process.poll() is None:
                print("  🔄 プロセス停止中...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                print("  ✅ プロセスを停止しました")
            
            # クリーンアップ待機
            time.sleep(2)
            
        except Exception as e:
            print(f"  ❌ テスト{i}でエラー: {e}")
        
        # 残存プロセスのクリーンアップ
        try:
            subprocess.run(['pkill', '-f', 'flask run'], stderr=subprocess.DEVNULL)
        except:
            pass
    
    print(f"\n" + "=" * 50)
    print(f"テスト結果: {success_count}/{test_count} 成功")
    
    if success_count == test_count:
        print("🎉 全テストが成功しました！ポート競合問題は解決されています。")
    else:
        print("⚠️  一部のテストが失敗しました。追加の修正が必要です。")
    
    return success_count == test_count

if __name__ == "__main__":
    success = test_flask_run()
    sys.exit(0 if success else 1)
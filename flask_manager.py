#!/usr/bin/env python3
"""
Flask プロセス管理システム
ポート競合を根本的に解決するためのプロセス管理ツール
"""

import os
import sys
import signal
import time
import socket
import subprocess
import psutil
from pathlib import Path

class FlaskManager:
    def __init__(self, app_name="StaffCloud", default_port=5000):
        self.app_name = app_name
        self.default_port = default_port
        self.pid_file = Path(f"./{app_name.lower()}_flask.pid")
        self.log_file = Path(f"./{app_name.lower()}_flask.log")
        
    def is_port_free(self, port):
        """指定ポートが利用可能かチェック"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return True
        except OSError:
            return False
    
    def find_free_port(self, start_port=None):
        """利用可能な最初のポートを検索"""
        port = start_port or self.default_port
        while port < 65535:
            if self.is_port_free(port):
                return port
            port += 1
        raise RuntimeError("利用可能なポートが見つかりません")
    
    def get_running_pid(self):
        """実行中のFlaskプロセスのPIDを取得"""
        if not self.pid_file.exists():
            return None
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # プロセスが実際に存在するかチェック
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                # Flaskプロセスかどうか確認
                if any('flask' in arg.lower() or 'app.py' in arg for arg in proc.cmdline()):
                    return pid
            
            # PIDファイルが古い場合は削除
            self.pid_file.unlink()
            return None
            
        except (ValueError, FileNotFoundError, psutil.NoSuchProcess):
            if self.pid_file.exists():
                self.pid_file.unlink()
            return None
    
    def stop_flask(self):
        """Flaskプロセスを安全に停止"""
        pid = self.get_running_pid()
        if pid:
            try:
                print(f"Stopping {self.app_name} Flask process (PID: {pid})")
                os.kill(pid, signal.SIGTERM)
                
                # プロセス終了を待機
                for _ in range(10):  # 最大10秒待機
                    if not psutil.pid_exists(pid):
                        break
                    time.sleep(1)
                
                # まだ生きている場合は強制終了
                if psutil.pid_exists(pid):
                    print(f"Force stopping process {pid}")
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(2)
                
                # PIDファイル削除
                if self.pid_file.exists():
                    self.pid_file.unlink()
                    
                print("Flask process stopped successfully")
                return True
                
            except ProcessLookupError:
                print("Process already stopped")
                if self.pid_file.exists():
                    self.pid_file.unlink()
                return True
            except Exception as e:
                print(f"Error stopping process: {e}")
                return False
        else:
            print("No Flask process running")
            return True
    
    def cleanup_orphaned_processes(self):
        """孤立したFlaskプロセスをクリーンアップ"""
        cleaned = 0
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('flask run' in ' '.join(cmdline).lower() or 
                                 'app.py' in arg for arg in cmdline):
                    # 現在管理中のプロセス以外を終了
                    current_pid = self.get_running_pid()
                    if proc.info['pid'] != current_pid:
                        print(f"Cleaning up orphaned Flask process: {proc.info['pid']}")
                        proc.terminate()
                        cleaned += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if cleaned > 0:
            time.sleep(3)  # プロセス終了を待機
            print(f"Cleaned up {cleaned} orphaned processes")
        
        return cleaned
    
    def start_flask(self, host='0.0.0.0', port=None, debug=False):
        """Flaskを安全に起動"""
        # 既存プロセスチェック・停止
        self.stop_flask()
        
        # 孤立プロセスクリーンアップ
        self.cleanup_orphaned_processes()
        
        # ポート決定
        if port is None:
            port = self.find_free_port()
        elif not self.is_port_free(port):
            print(f"Port {port} is in use, finding alternative...")
            port = self.find_free_port(port + 1)
        
        print(f"\n{'='*50}")
        print(f"🚀 Starting {self.app_name}")
        print(f"Port: {port}")
        print(f"🌐 Access URLs:")
        print(f"   - Local:   http://127.0.0.1:{port}/")
        print(f"   - Network: http://{self.get_local_ip()}:{port}/")
        print(f"{'='*50}\n")
        
        # Flask起動
        env = os.environ.copy()
        env['FLASK_APP'] = 'app.py'
        env['FLASK_ENV'] = 'development' if debug else 'production'
        
        try:
            process = subprocess.Popen([
                sys.executable, '-m', 'flask', 'run',
                '--host', host,
                '--port', str(port)
            ], env=env, cwd=os.getcwd())
            
            # PIDファイル作成
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            print(f"Flask started successfully (PID: {process.pid})")
            print("Press Ctrl+C to stop the server\n")
            
            # プロセス監視
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\nShutting down...")
                self.stop_flask()
                
        except Exception as e:
            print(f"Failed to start Flask: {e}")
            return False
        
        return True
    
    def get_local_ip(self):
        """ローカルIPアドレス取得"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    def status(self):
        """現在のステータス表示"""
        pid = self.get_running_pid()
        if pid:
            try:
                proc = psutil.Process(pid)
                print(f"✅ {self.app_name} is running")
                print(f"   PID: {pid}")
                print(f"   Status: {proc.status()}")
                print(f"   Memory: {proc.memory_info().rss / 1024 / 1024:.1f}MB")
                
                # ポート情報取得
                for conn in proc.connections():
                    if conn.status == 'LISTEN':
                        print(f"   Port: {conn.laddr.port}")
                        break
                        
            except psutil.NoSuchProcess:
                print(f"❌ {self.app_name} process not found")
                if self.pid_file.exists():
                    self.pid_file.unlink()
        else:
            print(f"❌ {self.app_name} is not running")

def main():
    if len(sys.argv) < 2:
        print("Usage: python flask_manager.py [start|stop|restart|status|cleanup]")
        sys.exit(1)
    
    manager = FlaskManager()
    command = sys.argv[1]
    
    if command == 'start':
        port = int(sys.argv[2]) if len(sys.argv) > 2 else None
        manager.start_flask(port=port)
    elif command == 'stop':
        manager.stop_flask()
    elif command == 'restart':
        manager.stop_flask()
        time.sleep(2)
        manager.start_flask()
    elif command == 'status':
        manager.status()
    elif command == 'cleanup':
        manager.cleanup_orphaned_processes()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
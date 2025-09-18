#!/usr/bin/env python3
"""
ポートロック機能 - システムレベルでのポート予約
"""

import fcntl
import socket
import os
import time
from pathlib import Path

class PortLock:
    def __init__(self, port, app_name="StaffCloud"):
        self.port = port
        self.app_name = app_name
        self.lock_file = Path(f"./.port_{port}.lock")
        self.lock_fd = None
        self.socket_holder = None
    
    def __enter__(self):
        """コンテキストマネージャー - ポートをロック"""
        try:
            # ロックファイルを作成
            self.lock_fd = open(self.lock_file, 'w')
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock_fd.write(f"{self.app_name}:{os.getpid()}:{int(time.time())}")
            self.lock_fd.flush()
            
            # ポートを予約（ソケットを保持）
            self.socket_holder = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_holder.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_holder.bind(('127.0.0.1', self.port))
            
            print(f"✅ Port {self.port} locked for {self.app_name}")
            return self
            
        except (IOError, OSError) as e:
            self.cleanup()
            raise RuntimeError(f"Failed to lock port {self.port}: {e}")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー - ポートロックを解除"""
        self.cleanup()
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        if self.socket_holder:
            try:
                self.socket_holder.close()
            except:
                pass
            self.socket_holder = None
        
        if self.lock_fd:
            try:
                fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
                self.lock_fd.close()
            except:
                pass
            self.lock_fd = None
        
        if self.lock_file.exists():
            try:
                self.lock_file.unlink()
            except:
                pass
        
        print(f"🔓 Port {self.port} unlocked")

def is_port_locked(port):
    """ポートがロックされているかチェック"""
    lock_file = Path(f"./.port_{port}.lock")
    if not lock_file.exists():
        return False
    
    try:
        with open(lock_file, 'r') as f:
            content = f.read().strip()
            if content:
                app_name, pid, timestamp = content.split(':')
                # プロセスが生きているかチェック
                try:
                    os.kill(int(pid), 0)
                    return True  # プロセスが生きている
                except OSError:
                    # プロセスが死んでいる場合はロックファイルを削除
                    lock_file.unlink()
                    return False
    except:
        # ロックファイルが壊れている場合は削除
        try:
            lock_file.unlink()
        except:
            pass
        return False
    
    return False

if __name__ == "__main__":
    # テスト用
    import sys
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        print(f"Testing port lock for port {port}")
        
        with PortLock(port) as lock:
            print("Port locked, press Enter to continue...")
            input()
        
        print("Port unlocked")
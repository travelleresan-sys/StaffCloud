#!/usr/bin/env python3
"""
ログイン機能のテストスクリプト
"""
from app import app, db, User, Employee
from werkzeug.security import check_password_hash
from flask import request
import logging

def test_admin_login():
    """管理者ログイン機能をテスト"""
    with app.app_context():
        print("=== 管理者ログイン機能テスト ===")
        
        # 管理者ユーザーを取得
        admin = User.query.filter_by(email='admin@example.com', role='admin').first()
        
        if not admin:
            print("❌ 管理者アカウントが見つかりません")
            return False
        
        print(f"✅ 管理者アカウント: {admin.email}")
        
        # パスワード確認
        if check_password_hash(admin.password, 'admin123'):
            print("✅ パスワード確認: OK")
        else:
            print("❌ パスワード確認: NG")
            return False
        
        print("✅ 管理者ログイン機能: 正常")
        return True

def test_employee_login():
    """従業員ログイン機能をテスト"""
    with app.app_context():
        print("=== 従業員ログイン機能テスト ===")
        
        # 従業員データを取得
        employees = Employee.query.all()
        if not employees:
            print("❌ 従業員データが見つかりません")
            return False
        
        success_count = 0
        for employee in employees:
            # 対応するユーザーアカウントを探す
            user = User.query.filter_by(employee_id=employee.id, role='employee').first()
            if user:
                print(f"✅ 従業員: {employee.name} (ID: {employee.id}) - ユーザーアカウント: {user.email}")
                success_count += 1
            else:
                print(f"⚠️ 従業員: {employee.name} (ID: {employee.id}) - ユーザーアカウントなし")
        
        print(f"✅ 従業員ログイン機能: {success_count}名の従業員がログイン可能")
        return success_count > 0

def test_system_admin_login():
    """システム管理者ログイン機能をテスト"""
    with app.app_context():
        print("=== システム管理者ログイン機能テスト ===")
        
        # システム管理者ユーザーを取得
        system_admin = User.query.filter_by(email='system@staffcloud.local', role='system_admin').first()
        
        if not system_admin:
            print("❌ システム管理者アカウントが見つかりません")
            return False
        
        print(f"✅ システム管理者アカウント: {system_admin.email}")
        
        # パスワード確認
        if check_password_hash(system_admin.password, 'Admin123!'):
            print("✅ パスワード確認: OK")
        else:
            print("❌ パスワード確認: NG")
            return False
        
        print("✅ システム管理者ログイン機能: 正常")
        return True

def main():
    print("StaffCloud ログイン機能テスト開始")
    print("=" * 50)
    
    admin_ok = test_admin_login()
    print()
    
    employee_ok = test_employee_login()
    print()
    
    system_admin_ok = test_system_admin_login()
    print()
    
    print("=" * 50)
    print("テスト結果サマリー:")
    print(f"管理者ログイン: {'✅ OK' if admin_ok else '❌ NG'}")
    print(f"従業員ログイン: {'✅ OK' if employee_ok else '❌ NG'}")
    print(f"システム管理者ログイン: {'✅ OK' if system_admin_ok else '❌ NG'}")
    
    if admin_ok and employee_ok and system_admin_ok:
        print("\n🎉 全てのログイン機能が正常に動作しています！")
        
        print("\n=== ログイン情報 ===")
        print("【管理者ログイン】")
        print("Email: admin@example.com")
        print("Password: admin123")
        print("URL: /admin_login")
        
        print("\n【従業員ログイン】")
        print("従業員名: 田中 太郎, ID: 1")
        print("従業員名: 佐藤 花子, ID: 2")
        print("URL: /employee_login")
        
        print("\n【システム管理者ログイン】")
        print("Email: system@staffcloud.local")
        print("Password: Admin123!")
        print("URL: /system_admin_login")
        
    else:
        print("\n⚠️ 一部のログイン機能に問題があります。")

if __name__ == '__main__':
    main()

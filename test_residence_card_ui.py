#!/usr/bin/env python3
from app import app, Employee, db

def test_residence_card_ui():
    with app.app_context():
        # 在留カードファイルがある従業員を確認
        employees_with_residence_cards = Employee.query.filter(Employee.residence_card_filename.isnot(None)).all()
        
        print("在留カードファイルがある従業員:")
        for employee in employees_with_residence_cards:
            print(f"  - {employee.name}: {employee.residence_card_filename}")
            
        if employees_with_residence_cards:
            employee = employees_with_residence_cards[0]
            print(f"\n従業員詳細ページのテスト対象: {employee.name} (ID: {employee.id})")
            print(f"URL: http://127.0.0.1:5001/employee_detail/{employee.id}")
            
            # ファイルの種類を判定
            if employee.residence_card_filename.lower().endswith('.pdf'):
                print("ファイルタイプ: PDF - ダウンロード・新タブ表示機能をテスト")
            else:
                print("ファイルタイプ: 画像 - モーダル拡大表示機能をテスト")
        else:
            print("在留カードファイルがアップロードされた従業員がいません。")
            print("管理者ダッシュボードから従業員を編集して在留カードファイルをアップロードしてください。")

if __name__ == "__main__":
    test_residence_card_ui()
#!/usr/bin/env python3
"""
HTMLファイル直接生成で日本語表示テスト
"""

from app import app, Employee, LeaveCredit, LeaveRecord, db
from datetime import date

def create_employee_html_test(employee):
    """従業員HTMLを直接生成してテスト"""
    
    # 年休データを計算
    total_credited = db.session.query(db.func.sum(LeaveCredit.days_credited))\
                               .filter_by(employee_id=employee.id).scalar() or 0
    total_taken = db.session.query(db.func.sum(LeaveRecord.days_taken))\
                            .filter_by(employee_id=employee.id).scalar() or 0
    remaining_leave = total_credited - total_taken
    
    # 法定付与日数の計算
    years_employed = (date.today() - employee.join_date).days / 365.25 if employee.join_date else 0
    if years_employed < 0.5:
        legal_leave_days = 0
    elif years_employed < 1.5:
        legal_leave_days = 10
    elif years_employed < 2.5:
        legal_leave_days = 11
    elif years_employed < 3.5:
        legal_leave_days = 12
    elif years_employed < 4.5:
        legal_leave_days = 14
    elif years_employed < 5.5:
        legal_leave_days = 16
    elif years_employed < 6.5:
        legal_leave_days = 18
    else:
        legal_leave_days = 20
    
    # 年休履歴データを取得
    leave_credits = LeaveCredit.query.filter_by(employee_id=employee.id)\
                                   .order_by(LeaveCredit.date_credited.desc()).limit(10).all()
    leave_records = LeaveRecord.query.filter_by(employee_id=employee.id)\
                                   .order_by(LeaveRecord.date_taken.desc()).limit(10).all()
    
    # HTMLコンテンツ
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>従業員情報 - {employee.name}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', 'MS PGothic', 'MS Gothic', 'Yu Gothic', 'Meiryo', 'DejaVu Sans', sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: #333;
                margin: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                max-width: 800px;
                margin: 0 auto;
                padding: 30px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 3px solid #2c3e50;
            }}
            .header h1 {{
                font-size: 24px;
                color: #2c3e50;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .section {{
                margin-bottom: 25px;
            }}
            .section-title {{
                font-size: 18px;
                font-weight: bold;
                color: #34495e;
                margin-bottom: 15px;
                padding: 8px 0;
                border-bottom: 2px solid #ecf0f1;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            th {{
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 12px 10px;
                text-align: left;
                border: 1px solid #2980b9;
            }}
            td {{
                padding: 10px;
                border: 1px solid #bdc3c7;
                background-color: #fff;
            }}
            tr:nth-child(even) td {{ background-color: #f8f9fa; }}
            .info-table th {{ width: 30%; background-color: #34495e; }}
            .leave-table th {{ background-color: #27ae60; border-color: #229954; }}
            .history-table th {{ background-color: #8e44ad; border-color: #7d3c98; }}
            .status-active {{ color: #27ae60; font-weight: bold; }}
            .status-inactive {{ color: #e74c3c; font-weight: bold; }}
            .text-right {{ text-align: right; }}
            .debug {{
                background: #ffffcc;
                border: 1px solid #cccc00;
                padding: 10px;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>従業員情報 - {employee.name}</h1>
                <p>発行日: {date.today().strftime('%Y年%m月%d日')}</p>
            </div>
            
            <div class="debug">
                <h3>デバッグ情報</h3>
                <p>文字エンコーディング: UTF-8</p>
                <p>従業員名: {employee.name}</p>
                <p>従業員ID: {employee.id}</p>
                <p>文字テスト: あいうえお アイウエオ 漢字テスト</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">基本情報</h2>
                <table class="info-table">
                    <tr><th>氏名</th><td>{employee.name}</td></tr>
                    <tr><th>生年月日</th><td>{employee.birth_date.strftime('%Y年%m月%d日') if employee.birth_date else '未設定'}</td></tr>
                    <tr><th>性別</th><td>{employee.gender or '未設定'}</td></tr>
                    <tr><th>入社年月日</th><td>{employee.join_date.strftime('%Y年%m月%d日') if employee.join_date else '未設定'}</td></tr>
                    <tr><th>電話番号</th><td>{employee.phone_number or '未設定'}</td></tr>
                    <tr><th>住所</th><td>{employee.address or '未設定'}</td></tr>
                    <tr><th>国籍</th><td>{employee.nationality or '未設定'}</td></tr>
                    <tr><th>在留カード期限</th><td>{employee.residence_card_expiry.strftime('%Y年%m月%d日') if employee.residence_card_expiry else '未設定'}</td></tr>
                    <tr><th>自動車保険満了日</th><td>{employee.car_insurance_expiry.strftime('%Y年%m月%d日') if employee.car_insurance_expiry else '未設定'}</td></tr>
                    <tr><th>在籍状況</th><td class="{'status-active' if employee.status == '在籍中' else 'status-inactive'}">{employee.status}</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h2 class="section-title">年次有給休暇情報</h2>
                <table class="leave-table">
                    <tr><th>項目</th><th class="text-right">日数</th></tr>
                    <tr><td>付与日数合計</td><td class="text-right">{total_credited}日</td></tr>
                    <tr><td>取得日数合計</td><td class="text-right">{total_taken}日</td></tr>
                    <tr><td>残日数</td><td class="text-right">{remaining_leave}日</td></tr>
                    <tr><td>法定付与日数</td><td class="text-right">{legal_leave_days}日</td></tr>
                </table>
            </div>
    """
    
    # 年休付与履歴
    if leave_credits:
        html_content += """
            <div class="section">
                <h2 class="section-title">年休付与履歴</h2>
                <table class="history-table">
                    <tr><th>付与日</th><th class="text-right">付与日数</th></tr>
        """
        for credit in leave_credits:
            html_content += f"""
                    <tr>
                        <td>{credit.date_credited.strftime('%Y年%m月%d日')}</td>
                        <td class="text-right">{credit.days_credited}日</td>
                    </tr>
            """
        html_content += "</table></div>"
    
    # 年休取得履歴
    if leave_records:
        html_content += """
            <div class="section">
                <h2 class="section-title">年休取得履歴</h2>
                <table class="history-table">
                    <tr><th>取得日</th><th class="text-right">取得日数</th></tr>
        """
        for record in leave_records:
            html_content += f"""
                    <tr>
                        <td>{record.date_taken.strftime('%Y年%m月%d日')}</td>
                        <td class="text-right">{record.days_taken}日</td>
                    </tr>
            """
        html_content += "</table></div>"
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    return html_content

def test_html_generation():
    """HTMLファイル生成テスト"""
    print("=== HTML生成テスト ===")
    
    with app.app_context():
        employees = Employee.query.all()
        for employee in employees:
            try:
                print(f"従業員: {employee.name}")
                
                # HTML生成
                html_content = create_employee_html_test(employee)
                
                # HTMLファイル保存
                filename = f"employee_{employee.id}_test.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print(f"  ✓ HTML生成成功: {filename}")
                
                # 日本語文字列チェック
                if '田中' in html_content and '従業員' in html_content:
                    print("  ✓ 日本語文字列確認")
                else:
                    print("  ✗ 日本語文字列未確認")
                    
            except Exception as e:
                print(f"  ✗ HTML生成失敗: {e}")

if __name__ == "__main__":
    test_html_generation()
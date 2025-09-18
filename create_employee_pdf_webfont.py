#!/usr/bin/env python3
"""
Webフォント使用のWeasyPrint版従業員PDF生成
"""

from weasyprint import HTML, CSS
from io import BytesIO
from datetime import date
import tempfile

def create_employee_pdf_webfont(employee_data):
    """
    Webフォントを使用してWeasyPrintで従業員PDFを生成
    
    Args:
        employee_data: 従業員データ辞書
    
    Returns:
        BytesIO: PDFバイナリデータ
    """
    
    # HTMLテンプレート（Google Fonts使用）
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>従業員情報 - {employee_data['name']}</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Noto Sans JP', 'Yu Gothic', 'Meiryo', 'Hiragino Kaku Gothic ProN', 'MS PGothic', sans-serif;
                font-size: 12px;
                line-height: 1.6;
                color: #333;
                margin: 15mm;
            }}
            .header {{
                text-align: center;
                margin-bottom: 25px;
                padding-bottom: 12px;
                border-bottom: 3px solid #2c3e50;
            }}
            .header h1 {{
                font-size: 20px;
                color: #2c3e50;
                font-weight: 700;
                margin-bottom: 8px;
            }}
            .section {{
                margin-bottom: 20px;
                page-break-inside: avoid;
            }}
            .section-title {{
                font-size: 16px;
                font-weight: 700;
                color: #34495e;
                margin-bottom: 12px;
                padding: 6px 0;
                border-bottom: 2px solid #ecf0f1;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 15px;
            }}
            th {{
                background-color: #3498db;
                color: white;
                font-weight: 700;
                padding: 12px 8px;
                text-align: left;
                border: 1px solid #2980b9;
            }}
            td {{
                padding: 10px 8px;
                border: 1px solid #bdc3c7;
                background-color: #fff;
            }}
            tr:nth-child(even) td {{ background-color: #f8f9fa; }}
            .info-table th {{ width: 25%; background-color: #34495e; }}
            .leave-table th {{ background-color: #27ae60; border-color: #229954; }}
            .history-table th {{ background-color: #8e44ad; border-color: #7d3c98; }}
            .status-active {{ color: #27ae60; font-weight: 700; }}
            .status-inactive {{ color: #e74c3c; font-weight: 700; }}
            .text-right {{ text-align: right; }}
            @page {{ size: A4; margin: 10mm; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>従業員情報 - {employee_data['name']}</h1>
            <p>発行日: {date.today().strftime('%Y年%m月%d日')}</p>
        </div>
        
        <div class="section">
            <h2 class="section-title">基本情報</h2>
            <table class="info-table">
                <tr><th>氏名</th><td>{employee_data['name']}</td></tr>
                <tr><th>生年月日</th><td>{employee_data.get('birth_date', '未設定')}</td></tr>
                <tr><th>性別</th><td>{employee_data.get('gender', '未設定')}</td></tr>
                <tr><th>入社年月日</th><td>{employee_data.get('join_date', '未設定')}</td></tr>
                <tr><th>電話番号</th><td>{employee_data.get('phone_number', '未設定')}</td></tr>
                <tr><th>住所</th><td>{employee_data.get('address', '未設定')}</td></tr>
                <tr><th>国籍</th><td>{employee_data.get('nationality', '未設定')}</td></tr>
                <tr><th>在留カード期限</th><td>{employee_data.get('residence_card_expiry', '未設定')}</td></tr>
                <tr><th>自動車保険満了日</th><td>{employee_data.get('car_insurance_expiry', '未設定')}</td></tr>
                <tr><th>在籍状況</th><td class="{'status-active' if employee_data.get('status') == '在籍中' else 'status-inactive'}">{employee_data.get('status', '未設定')}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2 class="section-title">年次有給休暇情報</h2>
            <table class="leave-table">
                <tr><th>項目</th><th class="text-right">日数</th></tr>
                <tr><td>付与日数合計</td><td class="text-right">{employee_data.get('total_credited', 0)}日</td></tr>
                <tr><td>取得日数合計</td><td class="text-right">{employee_data.get('total_taken', 0)}日</td></tr>
                <tr><td>残日数</td><td class="text-right">{employee_data.get('remaining_leave', 0)}日</td></tr>
                <tr><td>法定付与日数</td><td class="text-right">{employee_data.get('legal_leave_days', 0)}日</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2 class="section-title">日本語テスト</h2>
            <table class="info-table">
                <tr><th>ひらがな</th><td>あいうえおかきくけこ</td></tr>
                <tr><th>カタカナ</th><td>アイウエオカキクケコ</td></tr>
                <tr><th>漢字</th><td>従業員基本情報管理システム</td></tr>
                <tr><th>混合文字</th><td>田中太郎さん（タナカタロウ）</td></tr>
            </table>
        </div>
    </body>
    </html>
    """
    
    try:
        # WeasyPrint設定でWebフォントを有効化
        html = HTML(string=html_content)
        
        # CSS設定（Webフォントサポート）
        css = CSS(string='''
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
        ''')
        
        # PDF生成
        pdf_bytes = html.write_pdf(stylesheets=[css])
        
        # BytesIOに変換して返す
        buffer = BytesIO(pdf_bytes)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"WeasyPrint Webフォント PDF生成エラー: {e}")
        raise

def test_webfont_employee_pdf():
    """Webフォント版従業員PDF生成をテスト"""
    from app import app, Employee
    
    with app.app_context():
        print("=== Webフォント版従業員PDFテスト ===")
        
        employees = Employee.query.all()
        for employee in employees:
            try:
                print(f"従業員: {employee.name}")
                
                # 従業員データ辞書を作成
                employee_data = {
                    'name': employee.name,
                    'birth_date': employee.birth_date.strftime('%Y年%m月%d日') if employee.birth_date else '未設定',
                    'gender': employee.gender or '未設定',
                    'join_date': employee.join_date.strftime('%Y年%m月%d日') if employee.join_date else '未設定',
                    'phone_number': employee.phone_number or '未設定',
                    'address': employee.address or '未設定',
                    'nationality': employee.nationality or '未設定',
                    'residence_card_expiry': employee.residence_card_expiry.strftime('%Y年%m月%d日') if employee.residence_card_expiry else '未設定',
                    'car_insurance_expiry': employee.car_insurance_expiry.strftime('%Y年%m月%d日') if employee.car_insurance_expiry else '未設定',
                    'status': employee.status or '未設定',
                    'total_credited': 20,
                    'total_taken': 5,
                    'remaining_leave': 15,
                    'legal_leave_days': 20
                }
                
                # PDF生成
                pdf_buffer = create_employee_pdf_webfont(employee_data)
                
                # ファイルに保存
                filename = f"webfont_employee_{employee.id}.pdf"
                with open(filename, 'wb') as f:
                    f.write(pdf_buffer.read())
                
                import os
                file_size = os.path.getsize(filename)
                print(f"  ✓ PDF生成成功: {filename} ({file_size} bytes)")
                
                # バイナリ内での日本語確認
                with open(filename, 'rb') as f:
                    data = f.read()
                    # UTF-8での「田」の16進表現をチェック
                    if b'\xe7\x94\xb0' in data or b'\xe5\xbe\x93' in data:
                        print("  ✓ 日本語バイナリデータ検出")
                    else:
                        print("  ✗ 日本語バイナリデータ未検出")
                
            except Exception as e:
                print(f"  ✗ PDF生成失敗: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    test_webfont_employee_pdf()
#!/usr/bin/env python3
"""
HTML → PDF変換による従業員PDF生成
"""

from weasyprint import HTML, CSS
from io import BytesIO
from datetime import date
import os

def create_employee_pdf_html(employee, leave_data=None):
    """
    WeasyPrintを使用してHTML → PDF変換で従業員PDFを生成
    
    Args:
        employee: Employee オブジェクト
        leave_data: 年休データ（辞書形式）
    
    Returns:
        BytesIO: PDF バイナリデータ
    """
    
    # デフォルト年休データ
    if leave_data is None:
        leave_data = {
            'total_credited': 20,
            'total_taken': 5,
            'remaining_leave': 15,
            'legal_leave_days': 20,
            'leave_credits': [],
            'leave_records': []
        }
    
    # HTML テンプレート
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>従業員情報 - {employee.name}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Noto Sans JP', 'DejaVu Sans', sans-serif;
                font-size: 13px;
                line-height: 1.8;
                color: #2c3e50;
                margin: 15mm;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 35px;
                padding: 25px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                color: white;
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                backdrop-filter: blur(4px);
                border: 1px solid rgba(255, 255, 255, 0.18);
            }}
            
            .header h1 {{
                font-size: 28px;
                color: white;
                font-weight: 700;
                margin-bottom: 8px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            
            .section {{
                margin-bottom: 30px;
                background: rgba(255, 255, 255, 0.9);
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
            
            .section-title {{
                font-size: 18px;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 20px;
                padding: 12px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 8px;
                text-align: center;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                background: white;
            }}
            
            th {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-weight: 700;
                padding: 15px 12px;
                text-align: left;
                border: none;
                font-size: 14px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            }}
            
            td {{
                padding: 12px;
                border: none;
                border-bottom: 1px solid #e9ecef;
                background-color: #fff;
                font-size: 13px;
            }}
            
            tr:nth-child(even) td {{
                background-color: #f8f9ff;
            }}
            
            tr:hover td {{
                background-color: #e8f4f8;
            }}
            
            .info-table th {{
                width: 30%;
                background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
            }}
            
            .leave-table th {{
                background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
            }}
            
            .status-active {{
                color: #27ae60;
                font-weight: 700;
                background: rgba(39, 174, 96, 0.1);
                padding: 4px 8px;
                border-radius: 20px;
                border: 1px solid #27ae60;
            }}
            
            .status-inactive {{
                color: #e74c3c;
                font-weight: 700;
                background: rgba(231, 76, 60, 0.1);
                padding: 4px 8px;
                border-radius: 20px;
                border: 1px solid #e74c3c;
            }}
            
            .text-center {{
                text-align: center;
            }}
            
            .text-right {{
                text-align: right;
            }}
            
            .no-break {{
                page-break-inside: avoid;
            }}
            
            .photo-section {{
                text-align: center;
                margin-bottom: 30px;
            }}
            
            .employee-photo {{
                width: 140px;
                height: 140px;
                object-fit: cover;
                border-radius: 12px;
                border: 3px solid white;
                box-shadow: 0 8px 24px rgba(0,0,0,0.2);
                filter: brightness(1.05) contrast(1.1);
            }}
            
            .no-photo {{
                width: 140px;
                height: 140px;
                border: 3px dashed #cbd5e1;
                border-radius: 12px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                color: #64748b;
                font-size: 16px;
                font-weight: 500;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            
            @page {{
                size: A4;
                margin: 15mm;
                @bottom-right {{
                    content: counter(page) " / " counter(pages);
                    font-size: 10px;
                    color: #7f8c8d;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>従業員情報 - {employee.name}</h1>
            <p>発行日: {date.today().strftime('%Y年%m月%d日')}</p>
        </div>
        
        <!-- 顔写真 -->
        <div class="photo-section">
            {f'<img src="static/uploads/{employee.photo_filename}" alt="顔写真" class="employee-photo">' if employee.photo_filename else '<div class="no-photo">写真なし</div>'}
        </div>
        
        <div class="section no-break">
            <h2 class="section-title">基本情報</h2>
            <table class="info-table">
                <tr>
                    <th>氏名</th>
                    <td>{employee.name}</td>
                </tr>
                <tr>
                    <th>生年月日</th>
                    <td>{employee.birth_date.strftime('%Y年%m月%d日') if employee.birth_date else '未設定'}</td>
                </tr>
                <tr>
                    <th>性別</th>
                    <td>{employee.gender or '未設定'}</td>
                </tr>
                <tr>
                    <th>入社年月日</th>
                    <td>{employee.join_date.strftime('%Y年%m月%d日') if employee.join_date else '未設定'}</td>
                </tr>
                <tr>
                    <th>電話番号</th>
                    <td>{employee.phone_number or '未設定'}</td>
                </tr>
                <tr>
                    <th>住所</th>
                    <td>{employee.address or '未設定'}</td>
                </tr>
                <tr>
                    <th>国籍</th>
                    <td>{employee.nationality or '未設定'}</td>
                </tr>
                <tr>
                    <th>在留カード期限</th>
                    <td>{employee.residence_card_expiry.strftime('%Y年%m月%d日') if employee.residence_card_expiry else '未設定'}</td>
                </tr>
                <tr>
                    <th>自動車保険満了日</th>
                    <td>{employee.car_insurance_expiry.strftime('%Y年%m月%d日') if employee.car_insurance_expiry else '未設定'}</td>
                </tr>
                <tr>
                    <th>在籍状況</th>
                    <td class="{'status-active' if employee.status == '在籍中' else 'status-inactive'}">{employee.status}</td>
                </tr>
            </table>
        </div>
        
        <div class="section no-break">
            <h2 class="section-title">年次有給休暇情報</h2>
            <table class="leave-table">
                <tr>
                    <th>項目</th>
                    <th class="text-right">日数</th>
                </tr>
                <tr>
                    <td>付与日数合計</td>
                    <td class="text-right">{leave_data['total_credited']}日</td>
                </tr>
                <tr>
                    <td>取得日数合計</td>
                    <td class="text-right">{leave_data['total_taken']}日</td>
                </tr>
                <tr>
                    <td>残日数</td>
                    <td class="text-right">{leave_data['remaining_leave']}日</td>
                </tr>
                <tr>
                    <td>法定付与日数</td>
                    <td class="text-right">{leave_data['legal_leave_days']}日</td>
                </tr>
            </table>
        </div>
    """
    
    # 年休付与履歴がある場合
    if leave_data['leave_credits']:
        html_content += """
        <div class="section no-break">
            <h2 class="section-title">年休付与履歴</h2>
            <table>
                <tr>
                    <th>付与日</th>
                    <th class="text-right">付与日数</th>
                </tr>
        """
        for credit in leave_data['leave_credits'][:10]:  # 最大10件
            html_content += f"""
                <tr>
                    <td>{credit.date_credited.strftime('%Y年%m月%d日')}</td>
                    <td class="text-right">{credit.days_credited}日</td>
                </tr>
            """
        html_content += "</table></div>"
    
    # 年休取得履歴がある場合
    if leave_data['leave_records']:
        html_content += """
        <div class="section no-break">
            <h2 class="section-title">年休取得履歴</h2>
            <table>
                <tr>
                    <th>取得日</th>
                    <th class="text-right">取得日数</th>
                </tr>
        """
        for record in leave_data['leave_records'][:10]:  # 最大10件
            html_content += f"""
                <tr>
                    <td>{record.date_taken.strftime('%Y年%m月%d日')}</td>
                    <td class="text-right">{record.days_taken}日</td>
                </tr>
            """
        html_content += "</table></div>"
    
    html_content += """
    </body>
    </html>
    """
    
    try:
        # HTMLからPDFを生成
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf()
        
        # BytesIOに変換して返す
        buffer = BytesIO(pdf_bytes)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"HTML → PDF変換エラー: {e}")
        raise

def test_html_employee_pdf():
    """HTML版の従業員PDF生成をテスト"""
    from app import app, Employee, LeaveCredit, LeaveRecord, db
    
    with app.app_context():
        employee = Employee.query.first()
        if not employee:
            print("テスト用従業員が見つかりません")
            return
        
        # 年休データを取得
        leave_credits = LeaveCredit.query.filter_by(employee_id=employee.id).all()
        leave_records = LeaveRecord.query.filter_by(employee_id=employee.id).all()
        
        total_credited = sum(credit.days_credited for credit in leave_credits) or 20
        total_taken = sum(record.days_taken for record in leave_records) or 0
        
        leave_data = {
            'total_credited': total_credited,
            'total_taken': total_taken,
            'remaining_leave': total_credited - total_taken,
            'legal_leave_days': 20,
            'leave_credits': leave_credits,
            'leave_records': leave_records
        }
        
        try:
            # HTML → PDF変換でPDF生成
            pdf_buffer = create_employee_pdf_html(employee, leave_data)
            
            # ファイルに保存
            filename = f"html_employee_{employee.id}.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_buffer.read())
            
            file_size = os.path.getsize(filename)
            print(f"✓ HTML版従業員PDF生成成功: {employee.name}")
            print(f"  ファイル名: {filename}")
            print(f"  ファイルサイズ: {file_size} bytes")
            
        except Exception as e:
            print(f"✗ HTML版従業員PDF生成失敗: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_html_employee_pdf()
#!/usr/bin/env python3
"""
WeasyPrintの基本テスト
"""

from weasyprint import HTML, CSS
import tempfile
import os

def test_weasyprint_basic():
    """WeasyPrintの基本動作をテスト"""
    print("=== WeasyPrint基本テスト ===\n")
    
    # 基本的なHTMLテスト
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: 'DejaVu Sans', sans-serif;
                margin: 20px;
            }
            .header {
                text-align: center;
                color: #333;
                border-bottom: 2px solid #333;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>従業員情報 - 田中 太郎</h1>
        </div>
        
        <h2>基本情報</h2>
        <table>
            <tr><th>項目</th><th>内容</th></tr>
            <tr><td>氏名</td><td>田中 太郎</td></tr>
            <tr><td>生年月日</td><td>1990年1月1日</td></tr>
            <tr><td>性別</td><td>男性</td></tr>
            <tr><td>入社年月日</td><td>2020年4月1日</td></tr>
            <tr><td>電話番号</td><td>090-1234-5678</td></tr>
            <tr><td>住所</td><td>東京都渋谷区...</td></tr>
        </table>
        
        <h2>年次有給休暇情報</h2>
        <table>
            <tr><th>項目</th><th>日数</th></tr>
            <tr><td>付与日数合計</td><td>20日</td></tr>
            <tr><td>取得日数合計</td><td>5日</td></tr>
            <tr><td>残日数</td><td>15日</td></tr>
        </table>
    </body>
    </html>
    """
    
    try:
        # HTMLからPDFを生成
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf()
        
        # ファイルに保存
        with open('weasyprint_basic_test.pdf', 'wb') as f:
            f.write(pdf_bytes)
        
        file_size = len(pdf_bytes)
        print(f"✓ WeasyPrint基本テスト成功")
        print(f"  ファイル名: weasyprint_basic_test.pdf")
        print(f"  ファイルサイズ: {file_size} bytes")
        
        return True
        
    except Exception as e:
        print(f"✗ WeasyPrint基本テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_weasyprint_basic()
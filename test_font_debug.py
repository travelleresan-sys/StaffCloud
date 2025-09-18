#!/usr/bin/env python3
"""
フォント問題のデバッグテスト
"""

from weasyprint import HTML, CSS
from io import BytesIO
import tempfile
import os

def test_font_debug():
    """フォント設定のデバッグテスト"""
    
    # 複数のフォント設定パターンをテスト
    font_tests = [
        # 1. WebフォントGoogle Fonts
        {
            'name': 'Google_Noto_Sans_JP',
            'css': """
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
            body { font-family: 'Noto Sans JP', sans-serif; }
            """
        },
        # 2. システムフォント詳細指定
        {
            'name': 'System_Fonts_Detailed',
            'css': """
            body { 
                font-family: 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', 'MS PGothic', 'MS Gothic', 'Meiryo', 'Yu Gothic', 'DejaVu Sans', sans-serif;
            }
            """
        },
        # 3. Unicode範囲指定
        {
            'name': 'Unicode_Range',
            'css': """
            @font-face {
                font-family: 'CustomJapanese';
                src: local('DejaVu Sans');
                unicode-range: U+3040-309F, U+30A0-30FF, U+4E00-9FAF;
            }
            body { font-family: 'CustomJapanese', 'DejaVu Sans', monospace; }
            """
        }
    ]
    
    # テスト用HTML
    html_template = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <style>
            {css}
            body {{ font-size: 14px; margin: 20px; }}
            .test {{ border: 1px solid #ccc; padding: 10px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="test">
            <h1>日本語テスト - Japanese Test</h1>
            <p>従業員情報: 田中 太郎</p>
            <p>ひらがな: あいうえお</p>
            <p>カタカナ: アイウエオ</p>
            <p>漢字: 従業員情報基本</p>
            <p>English: Employee Information</p>
        </div>
    </body>
    </html>
    """
    
    for test in font_tests:
        try:
            print(f"\n=== {test['name']} テスト ===")
            
            html_content = html_template.format(css=test['css'])
            html = HTML(string=html_content)
            pdf_bytes = html.write_pdf()
            
            filename = f"font_test_{test['name']}.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_bytes)
            
            size = len(pdf_bytes)
            print(f"✓ PDF生成成功: {filename} ({size} bytes)")
            
            # テキスト抽出試行
            try:
                import subprocess
                result = subprocess.run(['strings', filename], 
                                      capture_output=True, text=True, timeout=5)
                if '田中' in result.stdout or '従業員' in result.stdout:
                    print("  ✓ 日本語文字列検出")
                else:
                    print("  ✗ 日本語文字列未検出")
            except:
                print("  - テキスト検出スキップ")
                
        except Exception as e:
            print(f"  ✗ 失敗: {e}")

if __name__ == "__main__":
    test_font_debug()
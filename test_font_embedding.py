#!/usr/bin/env python3
"""
フォント埋め込み強制テスト
"""

from weasyprint import HTML, CSS
import os

def test_font_embedding():
    """フォント埋め込みを強制するテスト"""
    
    print("=== フォント埋め込み強制テスト ===")
    
    # 1. 利用可能なシステムフォントをチェック
    system_fonts = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/ubuntu/Ubuntu[wdth,wght].ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        '/usr/share/fonts/TTF/DejaVuSans.ttf'
    ]
    
    available_fonts = []
    for font_path in system_fonts:
        if os.path.exists(font_path):
            available_fonts.append(font_path)
            print(f"利用可能: {font_path}")
    
    if not available_fonts:
        print("システムフォントが見つかりません")
        return
    
    # 2. @font-faceで直接フォントファイルを指定
    font_path = available_fonts[0]  # 最初の利用可能フォントを使用
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @font-face {{
                font-family: 'EmbeddedFont';
                src: url('file://{font_path}') format('truetype');
                font-display: block;
            }}
            
            body {{
                font-family: 'EmbeddedFont', 'DejaVu Sans', monospace;
                font-size: 16px;
                margin: 20px;
            }}
            
            .japanese {{
                font-weight: normal;
                font-style: normal;
            }}
        </style>
    </head>
    <body>
        <h1>フォント埋め込みテスト</h1>
        <div class="japanese">
            <p>ASCII: Employee Information Test</p>
            <p>UTF-8: 従業員情報テスト</p>
            <p>ひらがな: あいうえおかきくけこ</p>
            <p>カタカナ: アイウエオカキクケコ</p>
            <p>漢字: 従業員基本情報管理</p>
        </div>
    </body>
    </html>
    """
    
    try:
        # WeasyPrintでPDF生成
        html = HTML(string=html_content, base_url='file://')
        pdf_bytes = html.write_pdf()
        
        filename = "font_embedding_test.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_bytes)
        
        size = len(pdf_bytes)
        print(f"✓ PDF生成成功: {filename} ({size} bytes)")
        
        # 埋め込みフォント確認
        import subprocess
        try:
            result = subprocess.run(['strings', filename], 
                                  capture_output=True, text=True, timeout=10)
            
            # ASCII文字列チェック
            if 'Employee' in result.stdout:
                print("  ✓ ASCII文字列検出")
            else:
                print("  ✗ ASCII文字列未検出")
            
            # UTF-8文字列の16進表現をチェック
            if any(word in result.stdout for word in ['従', '業', '員']):
                print("  ✓ 日本語文字検出")
            else:
                print("  ✗ 日本語文字未検出")
                
            # フォント情報をチェック
            if 'DejaVu' in result.stdout or 'Ubuntu' in result.stdout:
                print("  ✓ フォント埋め込み確認")
            else:
                print("  - フォント埋め込み不明")
                
        except Exception as e:
            print(f"  テキスト抽出エラー: {e}")
        
    except Exception as e:
        print(f"✗ PDF生成失敗: {e}")

def test_simple_text_render():
    """シンプルなテキスト描画テスト"""
    print("\n=== シンプルテキスト描画テスト ===")
    
    # 最もシンプルなHTMLで日本語テスト
    simple_html = """
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family: monospace; font-size: 20px;">
        <p>TEST: 田中太郎</p>
        <p>ABC123</p>
    </body>
    </html>
    """
    
    try:
        html = HTML(string=simple_html)
        pdf_bytes = html.write_pdf()
        
        filename = "simple_japanese_test.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"✓ シンプルPDF生成: {filename} ({len(pdf_bytes)} bytes)")
        
        # バイナリ内容を16進ダンプで確認
        with open(filename, 'rb') as f:
            data = f.read(1000)  # 最初の1000バイト
            hex_dump = data.hex()
            # UTF-8での「田」の16進表現: E794B0
            if 'e794b0' in hex_dump.lower():
                print("  ✓ UTF-8日本語バイナリ検出")
            else:
                print("  ✗ UTF-8日本語バイナリ未検出")
                
    except Exception as e:
        print(f"✗ シンプルPDF生成失敗: {e}")

if __name__ == "__main__":
    test_font_embedding()
    test_simple_text_render()
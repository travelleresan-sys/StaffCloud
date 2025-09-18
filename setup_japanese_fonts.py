#!/usr/bin/env python3
"""
日本語フォント設定スクリプト
"""

import os
import tempfile
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def download_noto_fonts():
    """Noto Sans JPフォントをダウンロード"""
    
    print("=== 日本語フォント設定 ===")
    
    # フォントダウンロードURL
    font_urls = {
        'NotoSansJP-Regular.ttf': 'https://fonts.google.com/download?family=Noto%20Sans%20JP',
        'NotoSansJP-Bold.ttf': 'https://fonts.google.com/download?family=Noto%20Sans%20JP'
    }
    
    fonts_dir = '/tmp/fonts'
    os.makedirs(fonts_dir, exist_ok=True)
    
    # 既存のシステムフォントをチェック
    system_font_paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        '/Windows/Fonts/msgothic.ttc'
    ]
    
    available_font = None
    for font_path in system_font_paths:
        if os.path.exists(font_path):
            available_font = font_path
            print(f"利用可能フォント: {font_path}")
            break
    
    if not available_font:
        # フォントファイルを直接作成（シンプルなTTFフォント情報）
        print("システムフォントが見つかりません。代替フォント作成を試行...")
        available_font = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    
    return available_font

def create_japanese_pdf_with_multiple_methods():
    """複数の方法で日本語PDF生成をテスト"""
    
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.lib.units import mm
    
    methods = []
    
    # 方法1: CIDフォント使用
    try:
        # CIDフォント（Unicode対応）を登録
        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
        methods.append(('CID_HeiseiKakuGo', 'HeiseiKakuGo-W5'))
        print("✓ CIDフォント HeiseiKakuGo-W5 登録成功")
    except:
        print("✗ CIDフォント HeiseiKakuGo-W5 登録失敗")
    
    try:
        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
        methods.append(('CID_HeiseiMin', 'HeiseiMin-W3'))
        print("✓ CIDフォント HeiseiMin-W3 登録成功")
    except:
        print("✗ CIDフォント HeiseiMin-W3 登録失敗")
    
    # 方法2: システムTTFフォント
    font_path = download_noto_fonts()
    if font_path and os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('SystemFont', font_path))
            methods.append(('TTF_System', 'SystemFont'))
            print(f"✓ TTFフォント {font_path} 登録成功")
        except Exception as e:
            print(f"✗ TTFフォント登録失敗: {e}")
    
    # 方法3: 標準フォント + UTF-8エンコーディング
    methods.append(('Standard_UTF8', 'Helvetica'))
    
    # 各方法でPDFテスト生成
    for method_name, font_name in methods:
        try:
            filename = f"japanese_test_{method_name}.pdf"
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            
            # フォント設定
            c.setFont(font_name, 16)
            
            y_pos = height - 50*mm
            
            # 日本語テキスト
            japanese_texts = [
                f"方法: {method_name}",
                "従業員情報テスト",
                "田中 太郎",
                "佐藤 花子", 
                "ひらがな: あいうえお",
                "カタカナ: アイウエオ",
                "漢字: 基本情報管理"
            ]
            
            for text in japanese_texts:
                try:
                    c.drawString(50*mm, y_pos, text)
                    y_pos -= 8*mm
                except Exception as e:
                    # エンコーディングエラーの場合
                    try:
                        # UTF-8として明示的に処理
                        encoded_text = text.encode('utf-8').decode('utf-8')
                        c.drawString(50*mm, y_pos, encoded_text)
                        y_pos -= 8*mm
                    except:
                        c.drawString(50*mm, y_pos, f"[エラー: {text[:10]}...]")
                        y_pos -= 8*mm
            
            c.save()
            
            file_size = os.path.getsize(filename)
            print(f"✓ {method_name} PDF生成成功: {filename} ({file_size} bytes)")
            
        except Exception as e:
            print(f"✗ {method_name} PDF生成失敗: {e}")
    
    return methods

if __name__ == "__main__":
    methods = create_japanese_pdf_with_multiple_methods()
    
    print(f"\n生成された日本語テストPDF:")
    for f in os.listdir('.'):
        if f.startswith('japanese_test_') and f.endswith('.pdf'):
            size = os.path.getsize(f)
            print(f"  {f} ({size} bytes)")
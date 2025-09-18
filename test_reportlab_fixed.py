#!/usr/bin/env python3
"""
ReportLabで確実に日本語を表示するテスト
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
import os

def test_reportlab_japanese():
    """ReportLabで日本語フォント埋め込みテスト"""
    
    print("=== ReportLab日本語テスト ===")
    
    # フォントファイルの検索
    font_paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/ubuntu/Ubuntu[wdth,wght].ttf',
        '/System/Library/Fonts/Arial.ttf'
    ]
    
    font_path = None
    for path in font_paths:
        if os.path.exists(path):
            font_path = path
            break
    
    if not font_path:
        print("✗ 利用可能なフォントが見つかりません")
        return
    
    print(f"使用フォント: {font_path}")
    
    try:
        # フォント登録
        pdfmetrics.registerFont(TTFont('JapaneseFont', font_path))
        print("✓ フォント登録成功")
        
        # PDFファイル作成
        filename = "reportlab_japanese_test.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # フォント設定
        c.setFont("JapaneseFont", 16)
        
        # テキスト描画
        y_pos = height - 50*mm
        
        # ASCII文字
        c.drawString(50*mm, y_pos, "ASCII: Employee Information")
        y_pos -= 10*mm
        
        # 日本語文字（UTF-8エンコーディング）
        japanese_texts = [
            "従業員情報",
            "田中 太郎", 
            "ひらがな: あいうえお",
            "カタカナ: アイウエオ", 
            "漢字: 基本情報管理"
        ]
        
        for text in japanese_texts:
            try:
                c.drawString(50*mm, y_pos, text)
                print(f"  ✓ テキスト描画: {text}")
            except Exception as e:
                print(f"  ✗ テキスト描画失敗: {text} - {e}")
                # エスケープして再試行
                try:
                    c.drawString(50*mm, y_pos, text.encode('utf-8').decode('utf-8'))
                    print(f"    ✓ UTF-8再試行成功: {text}")
                except:
                    print(f"    ✗ UTF-8再試行失敗: {text}")
            y_pos -= 10*mm
        
        # PDF保存
        c.save()
        
        # ファイルサイズ確認
        size = os.path.getsize(filename)
        print(f"✓ PDF生成完了: {filename} ({size} bytes)")
        
        # テキスト抽出テスト
        import subprocess
        try:
            result = subprocess.run(['strings', filename], 
                                  capture_output=True, text=True, timeout=5)
            
            if 'Employee' in result.stdout:
                print("  ✓ ASCII文字列検出")
            else:
                print("  ✗ ASCII文字列未検出")
            
            # 日本語チェック
            japanese_found = any(word in result.stdout 
                               for word in ['従業員', '田中', '太郎', 'あいうえお'])
            if japanese_found:
                print("  ✓ 日本語文字列検出")
            else:
                print("  ✗ 日本語文字列未検出")
                
        except Exception as e:
            print(f"  テキスト抽出エラー: {e}")
        
    except Exception as e:
        print(f"✗ ReportLab処理失敗: {e}")

if __name__ == "__main__":
    test_reportlab_japanese()
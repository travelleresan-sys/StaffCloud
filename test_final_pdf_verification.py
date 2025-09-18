#!/usr/bin/env python3
"""
最終的なPDF生成確認テスト
"""

from app import app, Employee, create_employee_pdf
import os

def test_final_pdf_with_verification():
    """最終PDFテストと検証"""
    
    print("=== 最終PDF生成・検証テスト ===")
    
    with app.app_context():
        employees = Employee.query.all()
        
        for employee in employees:
            try:
                print(f"\n従業員: {employee.name}")
                print(f"  ID: {employee.id}")
                print(f"  入社日: {employee.join_date}")
                print(f"  在籍状況: {employee.status}")
                
                # PDF生成
                pdf_buffer = create_employee_pdf(employee)
                
                # ファイルに保存
                filename = f"verified_employee_{employee.id}.pdf"
                with open(filename, 'wb') as f:
                    f.write(pdf_buffer.read())
                
                # ファイルサイズ確認
                file_size = os.path.getsize(filename)
                print(f"  ✓ PDF生成完了: {filename}")
                print(f"  ファイルサイズ: {file_size} bytes")
                
                # PDFが正常に生成されたことの確認
                if file_size > 5000:  # 5KB以上なら正常とみなす
                    print("  ✓ ファイルサイズ正常")
                else:
                    print("  ✗ ファイルサイズが小さすぎる")
                
                # PDFヘッダー確認
                with open(filename, 'rb') as f:
                    header = f.read(100)
                    if header.startswith(b'%PDF-'):
                        print("  ✓ 有効なPDFヘッダー確認")
                    else:
                        print("  ✗ 無効なPDFヘッダー")
                
                # ReportLabのフォント埋め込み情報を確認
                with open(filename, 'rb') as f:
                    content = f.read()
                    if b'DejaVu' in content or b'JapaneseFont' in content:
                        print("  ✓ フォント情報確認")
                    else:
                        print("  - フォント情報未確認")
                
                # 文字データの存在確認（PDF内部表現）
                japanese_chars_found = False
                with open(filename, 'rb') as f:
                    content = f.read()
                    # PDFでは文字がCIDやUnicodeで埋め込まれる
                    # 「田」「中」「従」「業」「員」のUnicodeコードポイント
                    unicode_points = [
                        '7530',  # 田
                        '4E2D',  # 中  
                        '5F93',  # 従
                        '696D',  # 業
                        '54E1'   # 員
                    ]
                    
                    content_hex = content.hex().upper()
                    for point in unicode_points:
                        if point in content_hex:
                            japanese_chars_found = True
                            print(f"    ✓ Unicode {point} 検出")
                            break
                
                if japanese_chars_found:
                    print("  ✓ 日本語文字データ確認")
                else:
                    print("  - 日本語文字データ未確認（但し埋め込み方式の違いの可能性）")
                
            except Exception as e:
                print(f"  ✗ PDF生成エラー: {e}")
                import traceback
                traceback.print_exc()
    
    print(f"\n=== テスト完了 ===")
    print("生成されたPDFファイル:")
    for f in os.listdir('.'):
        if f.startswith('verified_employee_') and f.endswith('.pdf'):
            size = os.path.getsize(f)
            print(f"  {f} ({size} bytes)")

if __name__ == "__main__":
    test_final_pdf_with_verification()
#!/usr/bin/env python3
"""
賃金台帳PDFの列幅計算確認
"""

from reportlab.lib.pagesizes import A4, landscape

def calculate_widths():
    """列幅の計算と確認"""
    page_size = landscape(A4)
    page_width, page_height = page_size
    
    print("=" * 60)
    print("賃金台帳PDF 列幅計算")
    print("=" * 60)
    
    print(f"\n📐 ページサイズ:")
    print(f"  A4横: {page_width:.1f} x {page_height:.1f} ポイント")
    print(f"  ({page_width/72:.1f} x {page_height/72:.1f} インチ)")
    
    # テーブル幅（最新の設定）
    table_x = 30  # 左マージン（縮小）
    table_width = page_width - 60  # 左右マージン合計60
    
    print(f"\n📊 テーブル全体:")
    print(f"  テーブル幅: {table_width:.1f} ポイント")
    print(f"  左マージン: {table_x} ポイント")
    print(f"  右マージン: {page_width - table_x - table_width:.0f} ポイント")
    
    # 修正前の列幅
    print(f"\n📏 修正前の列幅:")
    old_item_width = 60
    old_total_width = 40
    old_month_width = (table_width - old_item_width - old_total_width) / 12
    
    print(f"  項目列: {old_item_width} ポイント")
    print(f"  月列（各）: {old_month_width:.1f} ポイント")
    print(f"  合計列: {old_total_width} ポイント")
    print(f"  月列合計: {old_month_width * 12:.1f} ポイント")
    
    # 修正後の列幅（最新）
    print(f"\n📏 修正後の列幅（最新）:")
    new_item_width = 110
    new_total_width = 38
    new_month_width = (table_width - new_item_width - new_total_width) / 12
    
    print(f"  項目列: {new_item_width} ポイント （+{new_item_width - old_item_width}）")
    print(f"  月列（各）: {new_month_width:.1f} ポイント （{new_month_width - old_month_width:.1f}）")
    print(f"  合計列: {new_total_width} ポイント （{new_total_width - old_total_width}）")
    print(f"  月列合計: {new_month_width * 12:.1f} ポイント")
    
    # 手当・控除セクションのラベル列
    print(f"\n📋 手当・控除セクションの内訳:")
    label_col_width = 15  # 固定幅
    item_name_col_width = new_item_width - label_col_width
    
    print(f"  ラベル列（手当/控除額）: {label_col_width} ポイント")
    print(f"  項目名列: {item_name_col_width} ポイント")
    
    # 比率計算
    print(f"\n📊 比率分析:")
    print(f"  項目列が全体の: {new_item_width / table_width * 100:.1f}%")
    print(f"  月列合計が全体の: {new_month_width * 12 / table_width * 100:.1f}%")
    print(f"  合計列が全体の: {new_total_width / table_width * 100:.1f}%")
    
    print(f"\n✅ 変更効果:")
    print(f"  - 項目列が {((new_item_width - old_item_width) / old_item_width * 100):.1f}% 拡大")
    print(f"  - 月列が {((old_month_width - new_month_width) / old_month_width * 100):.1f}% 縮小")
    print(f"  - より多くの項目名テキストが表示可能に")

if __name__ == '__main__':
    calculate_widths()
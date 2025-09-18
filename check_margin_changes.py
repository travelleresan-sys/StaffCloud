#!/usr/bin/env python3
"""
賃金台帳PDFの余白変更による位置変化の確認
"""

from reportlab.lib.pagesizes import A4, landscape

def calculate_position_changes():
    """位置変更の計算"""
    page_size = landscape(A4)
    page_width, page_height = page_size
    
    print("=" * 60)
    print("賃金台帳PDF 余白とテーブル位置の変更")
    print("=" * 60)
    
    print(f"\n📐 ページサイズ:")
    print(f"  A4横: {page_width:.1f} x {page_height:.1f} ポイント")
    
    # ヘッダー部分の変更
    print(f"\n📍 ヘッダー位置の変更:")
    
    # 変更前
    old_top_margin = 30
    old_title_y = page_height - old_top_margin
    old_title_to_info = 40
    old_info_y = old_title_y - old_title_to_info
    old_info_to_date = 15
    old_date_y = old_info_y - old_info_to_date
    old_date_to_table = 30
    old_table_y = old_date_y - old_date_to_table
    
    print(f"\n  変更前:")
    print(f"    上余白: {old_top_margin} ポイント")
    print(f"    タイトル位置: {old_title_y:.1f} ポイント")
    print(f"    従業員情報位置: {old_info_y:.1f} ポイント")
    print(f"    作成日位置: {old_date_y:.1f} ポイント")
    print(f"    テーブル開始位置: {old_table_y:.1f} ポイント")
    print(f"    合計使用高さ: {old_top_margin + old_title_to_info + old_info_to_date + old_date_to_table} ポイント")
    
    # 変更後（最新）
    new_top_margin = 20
    new_title_y = page_height - new_top_margin
    new_title_to_info = 25
    new_info_y = new_title_y - new_title_to_info
    new_info_to_date = 0  # 同じ行に配置
    new_date_y = new_info_y  # 従業員情報と同じ高さ
    new_date_to_table = 10  # 更に縮小
    new_table_y = new_date_y - new_date_to_table
    
    print(f"\n  変更後:")
    print(f"    上余白: {new_top_margin} ポイント （-{old_top_margin - new_top_margin}）")
    print(f"    タイトル位置: {new_title_y:.1f} ポイント （+{new_title_y - old_title_y:.1f}）")
    print(f"    従業員情報位置: {new_info_y:.1f} ポイント （+{new_info_y - old_info_y:.1f}）")
    print(f"    作成日位置: {new_date_y:.1f} ポイント （+{new_date_y - old_date_y:.1f}）")
    print(f"    テーブル開始位置: {new_table_y:.1f} ポイント （+{new_table_y - old_table_y:.1f}）")
    print(f"    合計使用高さ: {new_top_margin + new_title_to_info + new_info_to_date + new_date_to_table} ポイント")
    
    # 節約効果
    print(f"\n📊 改善効果:")
    total_saved = (old_top_margin + old_title_to_info + old_info_to_date + old_date_to_table) - \
                  (new_top_margin + new_title_to_info + new_info_to_date + new_date_to_table)
    print(f"  ヘッダー部分の高さ削減: {total_saved} ポイント")
    print(f"  テーブルが上に移動: {new_table_y - old_table_y:.1f} ポイント上昇")
    print(f"  テーブル表示領域の拡大: +{total_saved} ポイント分")
    
    # 左右マージンの統一
    print(f"\n📏 左右マージンの統一:")
    print(f"  左マージン: 30 ポイント （全要素で統一）")
    print(f"  右マージン: 30 ポイント （全要素で統一）")
    print(f"  テーブル幅: {page_width - 60:.1f} ポイント")

if __name__ == '__main__':
    calculate_position_changes()
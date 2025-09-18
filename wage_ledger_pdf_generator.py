#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
賃金台帳PDF生成機能 - 給与明細書フォーマット準拠版
A4横サイズに12ヶ月を横並び配置し、右端に合計列を表示
"""

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
import os
import io
from datetime import datetime
from typing import Dict, List, Optional
import json

def get_company_name():
    """企業情報から会社名を取得"""
    try:
        from models import CompanySettings
        company_settings = CompanySettings.query.first()
        if company_settings and company_settings.company_name:
            return company_settings.company_name
        else:
            return "株式会社 サンプル企業"  # デフォルト値
    except Exception:
        return "株式会社 サンプル企業"  # データベースエラー時のフォールバック

def draw_justified_text(canvas, font_name, font_size, text, x, y, width):
    """項目名を均等割り付けで描画（給与明細書と同じ関数）"""
    canvas.setFont(font_name, font_size)
    
    # 2文字の場合は中央揃えで文字間に全角スペース3つを挿入
    if len(text) == 2:
        spaced_text = text[0] + "　　　" + text[1]  # 全角スペース3つ
        text_width = canvas.stringWidth(spaced_text, font_name, font_size)
        center_x = x + (width - text_width) / 2
        canvas.drawString(center_x, y, spaced_text)
        return
    
    # 1文字の場合は中央揃え
    if len(text) == 1:
        text_width = canvas.stringWidth(text, font_name, font_size)
        center_x = x + (width - text_width) / 2
        canvas.drawString(center_x, y, text)
        return
    
    # 文字間のスペースを計算
    text_width = canvas.stringWidth(text, font_name, font_size)
    if text_width >= width:
        # 文字列が幅を超える場合は通常表示
        canvas.drawString(x, y, text)
        return
    
    # 均等割り付けのため文字間の追加スペースを計算
    extra_space = width - text_width
    char_count = len(text) - 1  # 文字間の数
    
    if char_count > 0:
        space_per_char = extra_space / char_count
        current_x = x
        
        for i, char in enumerate(text):
            canvas.drawString(current_x, y, char)
            char_width = canvas.stringWidth(char, font_name, font_size)
            current_x += char_width
            if i < char_count:  # 最後の文字以外
                current_x += space_per_char
    else:
        canvas.drawString(x, y, text)

def draw_centered_text(canvas, font_name, font_size, text, x, y, width):
    """項目名を中央揃えで描画（給与明細書と同じ関数）"""
    canvas.setFont(font_name, font_size)
    text_width = canvas.stringWidth(text, font_name, font_size)
    center_x = x + (width - text_width) / 2
    canvas.drawString(center_x, y, text)

class WageLedgerPDFGenerator:
    def __init__(self):
        self.japanese_font = self.setup_japanese_font()
        self.page_size = landscape(A4)
        self.margin = 15 * mm
        
    def setup_japanese_font(self):
        """日本語フォント設定（給与明細書と同じロジック）"""
        # CIDフォントを試行（最も確実）
        cid_fonts = [
            'HeiseiKakuGo-W5',  # 日本語ゴシック
            'HeiseiMin-W3',     # 日本語明朝
        ]
        
        for font_name in cid_fonts:
            try:
                pdfmetrics.registerFont(UnicodeCIDFont(font_name))
                return font_name
            except Exception:
                continue
        
        # TTFフォントフォールバック
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('JapaneseFont', font_path))
                    return 'JapaneseFont'
                except Exception:
                    continue
        
        # 最終フォールバック
        return 'Helvetica'
    
    def generate_wage_ledger_pdf(self, employee_data: Dict, wage_data: Dict, year: int, output_path: str) -> bool:
        """賃金台帳PDFを生成 - 給与明細書フォーマット準拠
        
        Args:
            employee_data: 従業員情報 {id, name, employee_number}
            wage_data: 賃金データ（12ヶ月分）
            year: 対象年度
            output_path: 出力ファイルパス
            
        Returns:
            bool: 生成成功の場合True
        """
        try:
            # CanvasベースのPDF生成（給与明細書と同じアプローチ）
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=self.page_size)
            
            # 賃金台帳フォーマットで描画
            self.draw_wage_ledger_format(p, employee_data, wage_data, year)
            
            # ページを保存
            p.save()
            
            # ファイルへ書き込み
            with open(output_path, 'wb') as f:
                f.write(buffer.getvalue())
            
            return True
            
        except Exception as e:
            print(f"賃金台帳PDF生成エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def draw_wage_ledger_format(self, canvas, employee_data: Dict, wage_data: Dict, year: int):
        """賃金台帳フォーマットで描画（A4横サイズに12ヶ月横並び）"""
        page_width, page_height = self.page_size
        
        # ヘッダー部分の描画
        y = self.draw_header(canvas, employee_data, year, page_width, page_height)
        
        # 賃金台帳テーブルの描画
        table_end_y = self.draw_wage_ledger_table(canvas, wage_data, page_width, y)
        
        # テーブル下に会社名を表示
        self.draw_company_name_below_table(canvas, page_width, table_end_y)
    
    def draw_header(self, canvas, employee_data: Dict, year: int, page_width: float, page_height: float) -> float:
        """ヘッダー部分を描画（余白を最小限に縮小）"""
        y = page_height - 15  # 上余白を20→15に縮小
        
        # タイトル
        canvas.setFont(self.japanese_font, 18)
        title = f"{year}年度 賃金台帳"
        title_width = canvas.stringWidth(title, self.japanese_font, 18)
        canvas.drawString((page_width - title_width) / 2, y, title)
        
        y -= 20  # タイトル下の余白を25→20に縮小
        
        # 対象者情報を左側に配置
        canvas.setFont(self.japanese_font, 12)
        employee_info = f"従業員番号: {employee_data.get('employee_number', 'N/A')} {employee_data.get('name', 'N/A')} 様"
        canvas.drawString(30, y, employee_info)  # 左マージンも30に合わせる
        
        # 作成日を右側に配置（従業員情報と同じ行に配置）
        # y -= 12  # 情報間の余白を削除（同じ行に配置）
        canvas.setFont(self.japanese_font, 10)
        creation_date = datetime.now().strftime('%Y年%m月%d日')
        canvas.drawRightString(page_width - 30, y, creation_date)  # 従業員情報と同じ高さに配置
        
        y -= 8  # テーブルまでの余白を更に縮小（10→8）
        return y
    
    def draw_wage_ledger_table(self, canvas, wage_data: Dict, page_width: float, start_y: float) -> float:
        """賃金台帳テーブルを描画（A4横サイズに12ヶ月横並び）、テーブル終了位置を返す"""
        # テーブルの基本設定（余白を縮小）
        table_x = 30  # 左マージン（50→30に縮小）
        table_width = page_width - 60  # 左右マージン合計60（100→60に縮小）
        row_height = 14  # 行の高さを縮小（18→14）
        
        # 列幅設定（項目名を更に広く）
        item_col_width = 110  # 項目名列（85→110に拡大）
        total_col_width = 38  # 合計列
        month_col_width = (table_width - item_col_width - total_col_width) / 12  # 12ヶ月分（各月の幅を自動計算）
        
        current_y = start_y
        
        # ヘッダー行の描画
        current_y = self.draw_table_header(canvas, table_x, current_y, item_col_width, month_col_width, total_col_width, row_height)
        
        # データ行の描画
        final_y = self.draw_table_data(canvas, wage_data, table_x, current_y, item_col_width, month_col_width, total_col_width, row_height)
        return final_y
    
    def draw_table_header(self, canvas, table_x: float, y: float, item_width: float, month_width: float, total_width: float, row_height: float) -> float:
        """テーブルヘッダーを描画"""
        # ヘッダー背景色
        canvas.setFillColor(colors.lightgrey)
        canvas.rect(table_x, y - row_height, item_width + (month_width * 12) + total_width, row_height, fill=1, stroke=1)
        
        # ヘッダーテキスト（フォントサイズを縮小）
        canvas.setFillColor(colors.black)
        canvas.setFont(self.japanese_font, 8)
        
        # 項目列
        draw_centered_text(canvas, self.japanese_font, 8, "項目", table_x, y - 10, item_width)
        
        # 各月列
        current_x = table_x + item_width
        for month in range(1, 13):
            draw_centered_text(canvas, self.japanese_font, 8, f"{month}月", current_x, y - 10, month_width)
            current_x += month_width
        
        # 合計列
        draw_centered_text(canvas, self.japanese_font, 8, "合計", current_x, y - 10, total_width)
        
        # 列の縦線を描画
        line_x = table_x + item_width
        for i in range(13):  # 12ヶ月 + 年間合計
            canvas.line(line_x, y, line_x, y - row_height)
            if i < 12:
                line_x += month_width
            else:
                line_x += total_width
        
        return y - row_height
    
    def draw_table_data(self, canvas, wage_data: Dict, table_x: float, start_y: float, item_width: float, month_width: float, total_width: float, row_height: float) -> float:
        """テーブルデータ行を描画 - 給与明細書の項目構造と完全一致"""
        
        # 動的手当項目を生成（給与明細書と同じロジック）
        allowance_items = []
        # 基本的な手当項目（給与明細書の実装に合わせてデフォルト5項目）
        for i in range(1, 6):
            allowance_key = f'monthly_allowance{i}'
            annual_key = f'annual_allowance{i}'
            
            # データが存在するかチェック
            monthly_data = self._parse_json_field(wage_data.get(allowance_key, '{}'))
            has_data = any(monthly_data.values()) or wage_data.get(annual_key, 0)
            
            if has_data or i <= 5:  # 最低5項目は表示（給与明細書に合わせる）
                allowance_items.append((f'手当{i}', allowance_key, annual_key))
        
        # 動的控除項目を生成（給与明細書と同じロジック） 
        deduction_items = [
            ('健康保険料', 'monthly_health_insurance', 'annual_health_insurance'),
            ('厚生年金保険料', 'monthly_pension_insurance', 'annual_pension_insurance'),
            ('雇用保険料', 'monthly_employment_insurance', 'annual_employment_insurance'),
            ('所得税', 'monthly_income_tax', 'annual_income_tax'),
            ('市町村民税', 'monthly_resident_tax', 'annual_resident_tax'),
            ('定額減税分', 'monthly_tax_reduction', 'annual_tax_reduction')
        ]
        
        # その他控除項目を追加（給与明細書に合わせて最大8項目まで）
        for i in range(1, 3):  # その他控除1、その他控除2
            other_key = f'monthly_other_deduction{i}'
            annual_other_key = f'annual_other_deduction{i}'
            deduction_items.append((f'その他控除{i}', other_key, annual_other_key))
        
        # 給与明細書の項目を完全に再現（同じ順序・同じ項目名）
        wage_items = [
            # 賃金計算期間（給与明細書の最初の項目）
            ('賃金計算期間', 'monthly_calculation_period', 'annual_calculation_period'),
            
            # 労働時間・勤務日数関連項目
            ('労働日数', 'monthly_working_days', 'annual_working_days'),
            ('休業補償日数', 'monthly_paid_leave_days', 'annual_paid_leave_days'),
            ('1ヶ月所定労働時間', 'monthly_scheduled_hours', 'annual_scheduled_hours'),
            ('労働時間合計　※休日除く', 'monthly_total_working_hours', 'annual_total_working_hours'),
            ('所定労働時間（1倍）8時間以内', 'monthly_regular_hours', 'annual_regular_hours'),
            ('1ヶ月所定労働時間超（1.25倍）', 'monthly_overtime_hours', 'annual_overtime_hours'),
            ('深夜労働時間（0.25倍）', 'monthly_night_hours', 'annual_night_hours'),
            ('所定時間外労働時間（0.25倍）', 'monthly_extra_hours', 'annual_extra_hours'),
            ('法定休日労働時間（0.35倍）', 'monthly_holiday_hours', 'annual_holiday_hours'),
            
            # 基本給・割増関連項目
            ('基本給', 'monthly_base_salary', 'annual_base_salary'),
            ('1ヶ月所定労働時間超割増', 'monthly_overtime_allowance', 'annual_overtime_allowance'),
            ('深夜労働時間割増', 'monthly_night_allowance', 'annual_night_allowance'),
            ('所定時間外割増', 'monthly_extra_allowance', 'annual_extra_allowance'),
            ('法定休日割増', 'monthly_holiday_allowance', 'annual_holiday_allowance'),
            ('休業補償', 'monthly_temp_closure_compensation', 'annual_temp_closure_compensation'),
            
            # 手当セクション（給与明細書と同じ構造）
            ('ALLOWANCE_SECTION', '', ''),  # 手当セクションマーカー
            
            # 支給関連合計項目
            ('小　　　計', 'monthly_subtotal', 'annual_subtotal'),
            ('臨時の給与', 'monthly_temp_salary', 'annual_temp_salary'),
            ('賞　　　与', 'monthly_bonus', 'annual_bonus'),
            ('合　　　計', 'monthly_gross_pay', 'annual_gross_pay'),
            
            # 控除セクション（給与明細書と同じ構造）
            ('DEDUCTION_SECTION', '', ''),  # 控除セクションマーカー
            
            # 最終項目
            ('控除額合計', 'monthly_deductions', 'annual_deductions'),
            ('実物支給額', 'monthly_in_kind_payment', 'annual_in_kind_payment'),
            ('差引支給額', 'monthly_net_pay', 'annual_net_pay')
        ]
        
        current_y = start_y
        
        # 新しい項目リストで各項目を処理
        i = 0
        while i < len(wage_items):
            item_name, monthly_key, annual_key = wage_items[i]
            
            # 手当セクションの処理
            if item_name == "ALLOWANCE_SECTION":
                current_y = self.draw_allowance_section(canvas, wage_data, table_x, current_y, item_width, month_width, total_width, row_height, allowance_items)
                i += 1  # セクションマーカーのみをスキップ
                continue
            # 控除セクションの処理
            elif item_name == "DEDUCTION_SECTION":
                current_y = self.draw_deduction_section(canvas, wage_data, table_x, current_y, item_width, month_width, total_width, row_height, deduction_items)
                i += 1  # セクションマーカーのみをスキップ
                continue
            
            # 背景色の設定（給与明細書スタイルに合わせて）
            if '合計' in item_name:
                canvas.setFillColor(colors.lightyellow)
            elif '差引支給額' in item_name:
                canvas.setFillColor(colors.lightblue)
            else:
                canvas.setFillColor(colors.white)
            
            # 行の背景を描画
            canvas.rect(table_x, current_y - row_height, item_width + (month_width * 12) + total_width, row_height, fill=1, stroke=1)
            canvas.setFillColor(colors.black)
            
            # 項目名の描画（均等割り付け）- フォントサイズを7に縮小
            canvas.setFont(self.japanese_font, 7)
            if '合計' in item_name or '差引支給額' in item_name:
                draw_centered_text(canvas, self.japanese_font, 7, item_name, table_x + 3, current_y - 10, item_width - 6)
            else:
                draw_justified_text(canvas, self.japanese_font, 7, item_name, table_x + 3, current_y - 10, item_width - 6)
            
            # 各月のデータを描画
            monthly_data = self._parse_json_field(wage_data.get(monthly_key, '{}'))
            current_x = table_x + item_width
            
            for month in range(1, 13):
                value = monthly_data.get(str(month), '')
                formatted_value = self._format_value(value, item_name)
                
                # 数値は右寄せで表示（フォントサイズを7に縮小）
                canvas.setFont(self.japanese_font, 7)
                if formatted_value != '-':
                    value_width = canvas.stringWidth(formatted_value, self.japanese_font, 7)
                    canvas.drawString(current_x + month_width - value_width - 3, current_y - 10, formatted_value)
                else:
                    draw_centered_text(canvas, self.japanese_font, 7, formatted_value, current_x, current_y - 10, month_width)
                
                current_x += month_width
            
            # 年間合計を描画
            annual_total = wage_data.get(annual_key, '')
            formatted_total = self._format_value(annual_total, item_name)
            
            # 年間合計も同じく文字サイズを7に縮小
            canvas.setFont(self.japanese_font, 7)
            if formatted_total != '-':
                total_value_width = canvas.stringWidth(formatted_total, self.japanese_font, 7)
                canvas.drawString(current_x + total_width - total_value_width - 3, current_y - 10, formatted_total)
            else:
                draw_centered_text(canvas, self.japanese_font, 7, formatted_total, current_x, current_y - 10, total_width)
            
            # 縦線を描画
            line_x = table_x + item_width
            for line_idx in range(13):
                canvas.line(line_x, current_y, line_x, current_y - row_height)
                if line_idx < 12:
                    line_x += month_width
                else:
                    line_x += total_width
            
            current_y -= row_height
            i += 1  # 通常項目の場合はインデックスを1つ進める
        
        # テーブル終了位置を返す
        return current_y
    
    def draw_allowance_section_header(self, canvas, table_x: float, current_y: float, item_width: float, month_width: float, total_width: float, row_height: float) -> float:
        """手当セクションヘッダーを描画（縦書き結合セル形式）"""
        # 手当セクションは7行分の高さを持つ
        allowance_rows = 7
        allowance_height = row_height * allowance_rows
        
        # セクション全体の背景を描画
        canvas.setFillColor(colors.white)
        canvas.rect(table_x, current_y - allowance_height, item_width + (month_width * 12) + total_width, allowance_height, fill=1, stroke=1)
        
        # 項目名列に縦書き「手当」を結合セルで表示
        canvas.setFillColor(colors.black)
        canvas.setFont(self.japanese_font, 7)
        
        # 縦書きテキストの位置計算
        text_x = table_x + item_width // 2
        text_y_center = current_y - (allowance_height // 2)
        
        # 「手」と「当」を縦に配置
        canvas.drawCentredString(text_x, text_y_center + 6, "手")
        canvas.drawCentredString(text_x, text_y_center - 6, "当")
        
        # 各月と合計列は空欄で表示（手当項目は後で個別に描画）
        
        # 縦線を描画
        line_x = table_x + item_width
        for i in range(13):
            canvas.line(line_x, current_y, line_x, current_y - allowance_height)
            if i < 12:
                line_x += month_width
            else:
                line_x += total_width
        
        # 手当セクション内の横線（項目名列以外にのみ描画）
        for i in range(1, allowance_rows):
            row_y = current_y - (row_height * i)
            # 項目名列以外に横線を描画
            canvas.line(table_x + item_width, row_y, table_x + item_width + (month_width * 12) + total_width, row_y)
        
        return current_y - allowance_height
    
    def draw_deduction_section_header(self, canvas, table_x: float, current_y: float, item_width: float, month_width: float, total_width: float, row_height: float) -> float:
        """控除額セクションヘッダーを描画（縦書き結合セル形式）"""
        # 控除セクションは8行分の高さを持つ
        deduction_rows = 8
        deduction_height = row_height * deduction_rows
        
        # セクション全体の背景を描画
        canvas.setFillColor(colors.white)
        canvas.rect(table_x, current_y - deduction_height, item_width + (month_width * 12) + total_width, deduction_height, fill=1, stroke=1)
        
        # 項目名列に縦書き「控除額」を結合セルで表示
        canvas.setFillColor(colors.black)
        canvas.setFont(self.japanese_font, 7)
        
        # 縦書きテキストの位置計算
        text_x = table_x + item_width // 2
        text_y_center = current_y - (deduction_height // 2)
        
        # 「控」「除」「額」を縦に配置
        canvas.drawCentredString(text_x, text_y_center + 8, "控")
        canvas.drawCentredString(text_x, text_y_center, "除")
        canvas.drawCentredString(text_x, text_y_center - 8, "額")
        
        # 縦線を描画
        line_x = table_x + item_width
        for i in range(13):
            canvas.line(line_x, current_y, line_x, current_y - deduction_height)
            if i < 12:
                line_x += month_width
            else:
                line_x += total_width
        
        # 控除セクション内の横線（項目名列以外にのみ描画）
        for i in range(1, deduction_rows):
            row_y = current_y - (row_height * i)
            # 項目名列以外に横線を描画
            canvas.line(table_x + item_width, row_y, table_x + item_width + (month_width * 12) + total_width, row_y)
        
        return current_y - deduction_height
    
    def draw_allowance_section(self, canvas, wage_data: Dict, table_x: float, current_y: float, item_width: float, month_width: float, total_width: float, row_height: float, allowance_items: List) -> float:
        """手当セクション全体を描画（給与明細書と同じ2列形式）"""
        allowance_rows = len(allowance_items)
        allowance_height = row_height * allowance_rows
        
        # セクション全体の背景を描画
        canvas.setFillColor(colors.white)
        canvas.rect(table_x, current_y - allowance_height, item_width + (month_width * 12) + total_width, allowance_height, fill=1, stroke=1)
        
        # 給与明細書と同じ2列構成（縦書きラベル列と項目名列）
        # 縦書きラベル列の幅（項目名列全体の約1/5に縮小）
        label_col_width = 15  # 固定幅15ピクセル
        item_name_col_width = item_width - label_col_width
        
        # 縦書き「手当」列を結合セルで表示
        canvas.setFillColor(colors.black)
        canvas.setFont(self.japanese_font, 7)
        
        # 縦書きテキストの位置計算
        text_x = table_x + label_col_width // 2
        text_y_center = current_y - (allowance_height // 2)
        
        # 「手」と「当」を縦に配置
        canvas.drawCentredString(text_x, text_y_center + 6, "手")
        canvas.drawCentredString(text_x, text_y_center - 6, "当")
        
        # ラベル列の右境界線
        canvas.line(table_x + label_col_width, current_y, table_x + label_col_width, current_y - allowance_height)
        
        # 各手当項目を描画
        for j, (item_name, monthly_key, annual_key) in enumerate(allowance_items):
            item_y = current_y - (row_height * j) - 10
            
            # 項目名を項目名列に表示（給与明細書と同じ）
            if item_name:
                draw_justified_text(canvas, self.japanese_font, 7, item_name, table_x + label_col_width + 3, item_y, item_name_col_width - 6)
            
            # 各月のデータを描画
            monthly_data = self._parse_json_field(wage_data.get(monthly_key, '{}'))
            current_x = table_x + item_width
            
            for month in range(1, 13):
                value = monthly_data.get(str(month), '')
                formatted_value = self._format_value(value, item_name)
                
                # 数値は右寄せで表示
                canvas.setFont(self.japanese_font, 7)
                if formatted_value != '-':
                    value_width = canvas.stringWidth(formatted_value, self.japanese_font, 7)
                    canvas.drawString(current_x + month_width - value_width - 3, item_y, formatted_value)
                else:
                    draw_centered_text(canvas, self.japanese_font, 7, formatted_value, current_x, item_y, month_width)
                
                current_x += month_width
            
            # 年間合計を描画
            annual_total = wage_data.get(annual_key, '')
            formatted_total = self._format_value(annual_total, item_name)
            
            canvas.setFont(self.japanese_font, 7)
            if formatted_total != '-':
                total_value_width = canvas.stringWidth(formatted_total, self.japanese_font, 7)
                canvas.drawString(current_x + total_width - total_value_width - 3, item_y, formatted_total)
            else:
                draw_centered_text(canvas, self.japanese_font, 7, formatted_total, current_x, item_y, total_width)
        
        # 縦線を描画
        line_x = table_x + item_width
        for i in range(13):
            canvas.line(line_x, current_y, line_x, current_y - allowance_height)
            if i < 12:
                line_x += month_width
            else:
                line_x += total_width
        
        # 手当セクション内の横線（ラベル列以外に描画）
        for i in range(1, allowance_rows):
            row_y = current_y - (row_height * i)
            # ラベル列以外に横線を描画
            canvas.line(table_x + label_col_width, row_y, table_x + item_width + (month_width * 12) + total_width, row_y)
        
        return current_y - allowance_height
    
    def draw_deduction_section(self, canvas, wage_data: Dict, table_x: float, current_y: float, item_width: float, month_width: float, total_width: float, row_height: float, deduction_items: List) -> float:
        """控除セクション全体を描画（給与明細書と同じ2列形式）"""
        deduction_rows = len(deduction_items)
        deduction_height = row_height * deduction_rows
        
        # セクション全体の背景を描画
        canvas.setFillColor(colors.white)
        canvas.rect(table_x, current_y - deduction_height, item_width + (month_width * 12) + total_width, deduction_height, fill=1, stroke=1)
        
        # 給与明細書と同じ2列構成（縦書きラベル列と項目名列）
        # 縦書きラベル列の幅（項目名列全体の約1/5に縮小）
        label_col_width = 15  # 固定幅15ピクセル
        item_name_col_width = item_width - label_col_width
        
        # 縦書き「控除額」列を結合セルで表示
        canvas.setFillColor(colors.black)
        canvas.setFont(self.japanese_font, 7)
        
        # 縦書きテキストの位置計算
        text_x = table_x + label_col_width // 2
        text_y_center = current_y - (deduction_height // 2)
        
        # 「控」「除」「額」を縦に配置
        canvas.drawCentredString(text_x, text_y_center + 8, "控")
        canvas.drawCentredString(text_x, text_y_center, "除")
        canvas.drawCentredString(text_x, text_y_center - 8, "額")
        
        # ラベル列の右境界線
        canvas.line(table_x + label_col_width, current_y, table_x + label_col_width, current_y - deduction_height)
        
        # 各控除項目を描画
        for j, (item_name, monthly_key, annual_key) in enumerate(deduction_items):
            item_y = current_y - (row_height * j) - 10
            
            # 項目名を項目名列に表示（給与明細書と同じ）
            if item_name:
                draw_justified_text(canvas, self.japanese_font, 7, item_name, table_x + label_col_width + 3, item_y, item_name_col_width - 6)
            
            # 各月のデータを描画
            monthly_data = self._parse_json_field(wage_data.get(monthly_key, '{}'))
            current_x = table_x + item_width
            
            for month in range(1, 13):
                value = monthly_data.get(str(month), '')
                formatted_value = self._format_value(value, item_name)
                
                # 数値は右寄せで表示
                canvas.setFont(self.japanese_font, 7)
                if formatted_value != '-':
                    value_width = canvas.stringWidth(formatted_value, self.japanese_font, 7)
                    canvas.drawString(current_x + month_width - value_width - 3, item_y, formatted_value)
                else:
                    draw_centered_text(canvas, self.japanese_font, 7, formatted_value, current_x, item_y, month_width)
                
                current_x += month_width
            
            # 年間合計を描画
            annual_total = wage_data.get(annual_key, '')
            formatted_total = self._format_value(annual_total, item_name)
            
            canvas.setFont(self.japanese_font, 7)
            if formatted_total != '-':
                total_value_width = canvas.stringWidth(formatted_total, self.japanese_font, 7)
                canvas.drawString(current_x + total_width - total_value_width - 3, item_y, formatted_total)
            else:
                draw_centered_text(canvas, self.japanese_font, 7, formatted_total, current_x, item_y, total_width)
        
        # 縦線を描画
        line_x = table_x + item_width
        for i in range(13):
            canvas.line(line_x, current_y, line_x, current_y - deduction_height)
            if i < 12:
                line_x += month_width
            else:
                line_x += total_width
        
        # 控除セクション内の横線（ラベル列以外に描画）
        for i in range(1, deduction_rows):
            row_y = current_y - (row_height * i)
            # ラベル列以外に横線を描画
            canvas.line(table_x + label_col_width, row_y, table_x + item_width + (month_width * 12) + total_width, row_y)
        
        return current_y - deduction_height
    
    def draw_company_name_below_table(self, canvas, page_width: float, table_end_y: float):
        """テーブル下に会社名を表示"""
        canvas.setFont(self.japanese_font, 12)
        company_name = get_company_name()
        company_width = canvas.stringWidth(company_name, self.japanese_font, 12)
        # テーブル終了位置から15ポイント下に会社名を表示
        canvas.drawString((page_width - company_width) / 2, table_end_y - 15, company_name)
    
    def _parse_json_field(self, json_str: str) -> Dict:
        """JSON文字列をパース"""
        try:
            if not json_str or json_str == '':
                return {}
            return json.loads(json_str)
        except:
            return {}
    
    def _format_value(self, value, item_name: str) -> str:
        """値の表示形式を整える（給与明細書の項目に対応）"""
        if not value or value == '' or value is None:
            return '-'
        
        # 時間系項目の場合（給与明細書と同じフォーマット）
        if '時間' in item_name:
            if isinstance(value, (int, float)):
                if '1ヶ月所定労働時間' in item_name:
                    return "160：00"  # 固定値
                else:
                    hours = int(value) if isinstance(value, float) else value
                    return f"{hours}：00"
            return str(value)
        
        # 日数系項目の場合
        if '日数' in item_name:
            if isinstance(value, (int, float)):
                return f"{int(value)}日"
            return str(value)
        
        # 金額系項目の場合
        if isinstance(value, (int, float)):
            return f"¥{int(value):,}"
        
        return str(value)

def create_sample_wage_ledger():
    """サンプル賃金台帳作成（テスト用）"""
    generator = WageLedgerPDFGenerator()
    
    # サンプル従業員データ
    employee_data = {
        'id': 1,
        'name': '田中太郎',
        'employee_number': 'EMP001'
    }
    
    # サンプル賃金データ（12ヶ月分）
    sample_monthly_data = {}
    for month in range(1, 13):
        sample_monthly_data[str(month)] = 250000 + (month * 1000)  # 基本給例
    
    wage_data = {
        'monthly_base_salary': json.dumps(sample_monthly_data),
        'annual_base_salary': sum(sample_monthly_data.values()),
        'monthly_overtime_allowance': json.dumps({str(m): 30000 for m in range(1, 13)}),
        'annual_overtime_allowance': 360000,
        'monthly_gross_pay': json.dumps({str(m): 280000 + (m * 1000) for m in range(1, 13)}),
        'annual_gross_pay': sum([280000 + (m * 1000) for m in range(1, 13)]),
        'monthly_working_hours': json.dumps({str(m): 160.0 for m in range(1, 13)}),
        'annual_working_hours': 1920.0,
        'monthly_working_days': json.dumps({str(m): 22 for m in range(1, 13)}),
        'annual_working_days': 264
    }
    
    output_path = 'sample_wage_ledger_redesigned.pdf'
    success = generator.generate_wage_ledger_pdf(employee_data, wage_data, 2024, output_path)
    
    if success:
        print(f"✅ サンプル賃金台帳PDF生成成功: {output_path}")
    else:
        print("❌ サンプル賃金台帳PDF生成失敗")
    
    return success

if __name__ == '__main__':
    create_sample_wage_ledger()
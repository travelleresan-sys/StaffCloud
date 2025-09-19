#!/usr/bin/env python3
"""
給与明細書PDF生成機能
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
import io
import os

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
    """項目名を均等割り付けで描画"""
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
    """項目名を中央揃えで描画"""
    canvas.setFont(font_name, font_size)
    text_width = canvas.stringWidth(text, font_name, font_size)
    center_x = x + (width - text_width) / 2
    canvas.drawString(center_x, y, text)

def setup_japanese_font():
    """日本語フォント設定"""
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

def create_payroll_slip_pdf(payroll_slip, employee, payroll_calculation, payroll_settings=None):
    """給与明細書PDFを生成"""
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # フォント設定
    font_name = setup_japanese_font()
    
    # A4サイズの寸法
    page_width, page_height = A4
    
    # 2列表形式フォーマットでPDF生成
    draw_umebishi_payroll_format(p, font_name, payroll_slip, employee, payroll_calculation, payroll_settings)
    
    # ページを保存
    p.save()
    
    buffer.seek(0)
    return buffer
        
def calculate_remaining_leave(employee, year, month):
    """残有給日数を計算（簡易版）"""
    # 実装を簡略化：年度開始からの経過を基に概算
    # 実際の実装では、入社日、年度開始、付与日数、取得日数を考慮
    return "10日"  # デモ用固定値
    
def calculate_absence_deduction(payroll_slip):
    """欠勤控除額を計算"""
    if payroll_slip.absence_days and payroll_slip.absence_days > 0:
        # 基本給÷月の稼働日数×欠勤日数（簡易計算）
        daily_salary = payroll_slip.base_salary / 22  # 22日を標準稼働日数とする
        return int(daily_salary * payroll_slip.absence_days)
    return 0
    
def format_working_hours(payroll_calculation):
    """労働時間をフォーマット - 画面表示と一致させるため時間:分形式に統一"""
    if not payroll_calculation:
        return "0:00"

    total_minutes = (payroll_calculation.regular_working_minutes or 0) + (payroll_calculation.overtime_minutes or 0)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}:{minutes:02d}"

def draw_umebishi_payroll_format(canvas, font_name, payroll_slip, employee, payroll_calculation, payroll_settings):
    """2列表形式フォーマット"""
    page_width, page_height = A4
    
    # 2列表形式フォーマットで描画
    draw_two_column_format(canvas, font_name, payroll_slip, employee, payroll_calculation)

def draw_two_column_format(canvas, font_name, payroll_slip, employee, payroll_calculation):
    """2列表形式フォーマット"""
    page_width, page_height = A4
    table_width = 320  # 固定幅に変更（約20%縮小）
    
    # テーブルを中央に配置
    table_x = (page_width - table_width) / 2
    margin = 40
    
    y = page_height - 30  # 上の余白を詰める（50→30）
    
    # ヘッダー
    canvas.setFont(font_name, 18)
    title = "給与明細"
    title_width = canvas.stringWidth(title, font_name, 18)
    canvas.drawString((page_width - title_width) / 2, y, title)
    
    y -= 40
    
    # 対象者情報を枠の左側に配置
    canvas.setFont(font_name, 12)
    target_info = f"{payroll_slip.slip_year}年{payroll_slip.slip_month}月分 {employee.name} 様"
    canvas.drawString(table_x, y, target_info)
    
    # 作成日は1段下げて枠の右側に配置
    y -= 15  # 行間を狭くする（20→15）
    canvas.setFont(font_name, 10)
    creation_date = payroll_slip.issued_at.strftime('%Y年%m月%d日') if payroll_slip.issued_at else datetime.now().strftime('%Y年%m月%d日')
    canvas.drawRightString(table_x + table_width, y, creation_date)
    
    y -= 20  # 明細枠との行間を狭くする（30→20）
    
    # 2列表を作成（中央配置されたテーブルで）
    draw_two_column_table(canvas, font_name, payroll_slip, employee, payroll_calculation, table_x, y, table_width)
    
    # フッター
    canvas.setFont(font_name, 12)
    company_name = get_company_name()  # 企業情報から会社名を取得
    company_width = canvas.stringWidth(company_name, font_name, 12)
    canvas.drawString((page_width - company_width) / 2, 40, company_name)

def draw_two_column_table(canvas, font_name, payroll_slip, employee, payroll_calculation, x, y, table_width):
    """指定された順序で、2列表を作成"""
    row_height = 16  # 20→16に縮小
    current_y = y
    
    # 表の設定
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1)
    canvas.setFont(font_name, 10)  # 他の項目と同じサイズに統一
    
    # 時間と金額の計算
    regular_hours = (payroll_calculation.regular_working_minutes or 0) // 60 if payroll_calculation else 0
    overtime_hours = (payroll_calculation.overtime_minutes or 0) // 60 if payroll_calculation else 0
    
    # 手当項目データ（その他手当1～5を上から順に対応）
    allowance_items = []
    
    # その他手当の詳細を上から順に追加
    if hasattr(payroll_slip, 'other_allowances_detail') and payroll_slip.other_allowances_detail:
        for item in payroll_slip.other_allowances_detail:
            allowance_items.append((item['name'] or "", item['amount']))
    
    # 5つの項目になるまで空の項目で埋める
    while len(allowance_items) < 5:
        allowance_items.append(("", 0))
    
    # 控除額項目データ（項目名、金額）
    deduction_items = [
        ("健康保険料", payroll_slip.health_insurance),
        ("厚生年金保険料", payroll_slip.pension_insurance),
        ("雇用保険料", payroll_slip.employment_insurance),
        ("所得税", payroll_slip.income_tax),
        ("市町村民税", payroll_slip.resident_tax or 0),
        ("定額減税分", 0)
    ]
    
    # その他控除の詳細を追加
    if hasattr(payroll_slip, 'other_deductions_detail') and payroll_slip.other_deductions_detail:
        for item in payroll_slip.other_deductions_detail:
            deduction_items.append((item['name'] or "その他", item['amount']))
    
    # 8つの項目になるまで空の項目で埋める
    while len(deduction_items) < 8:
        deduction_items.append(("", 0))
    
    # 指定された項目リスト（左列：項目、右列：値）
    items = [
        ("賃金計算期間", f"{payroll_slip.slip_month}月 1日～{payroll_slip.slip_month}月 30日"),
        ("労働日数", f"{payroll_slip.working_days}日"),
        ("休業補償日数", f"{payroll_slip.paid_leave_days or 0}日"),
        ("1ヶ月所定労働時間", f"{160}:00"),
        ("労働時間合計　※休日除く", format_working_hours(payroll_calculation)),
        ("所定労働時間（1倍）8時間以内", f"{regular_hours}:00"),
        ("1ヶ月所定労働時間超（1.25倍）", f"{overtime_hours}:00"),
        ("深夜労働時間（0.25倍）", f"{(payroll_calculation.night_working_minutes // 60) if payroll_calculation and payroll_calculation.night_working_minutes else 0}:{(payroll_calculation.night_working_minutes % 60):02d}" if payroll_calculation and payroll_calculation.night_working_minutes else "0:00"),
        ("所定時間外労働時間（0.25倍）", f"{(payroll_calculation.legal_overtime_minutes // 60) if payroll_calculation and payroll_calculation.legal_overtime_minutes else 0}:{(payroll_calculation.legal_overtime_minutes % 60):02d}" if payroll_calculation and payroll_calculation.legal_overtime_minutes else "0:00"),
        ("法定休日労働時間（0.35倍）", f"{(payroll_calculation.legal_holiday_minutes // 60) if payroll_calculation and payroll_calculation.legal_holiday_minutes else 0}:{(payroll_calculation.legal_holiday_minutes % 60):02d}" if payroll_calculation and payroll_calculation.legal_holiday_minutes else "0:00"),
        ("基本給", f"¥{payroll_slip.base_salary:,}"),
        ("1ヶ月所定労働時間超割増", f"¥{payroll_slip.overtime_allowance:,}"),
        ("深夜労働時間割増", f"¥{payroll_slip.night_allowance:,}"),
        ("所定時間外割増", f"¥{int((payroll_calculation.legal_overtime_minutes / 60 * (payroll_slip.base_salary / 173) * 0.25)) if payroll_calculation and payroll_calculation.legal_overtime_minutes else 0:,}"),
        ("法定休日割増", f"¥{int((payroll_calculation.legal_holiday_minutes / 60 * (payroll_slip.base_salary / 173) * 0.35)) if payroll_calculation and payroll_calculation.legal_holiday_minutes else 0:,}"),
        ("休業補償", f"¥{payroll_slip.temporary_closure_compensation:,}"),
        ("ALLOWANCE_SECTION", ""),  # 手当セクションの開始マーカー
        ("小　　　計", f"¥{payroll_slip.gross_salary:,}"),
        ("臨時の給与", f"¥{payroll_slip.salary_payment:,}"),
        ("賞　　　与", f"¥{payroll_slip.bonus_payment:,}"),
        ("合　　　計", f"¥{payroll_slip.gross_salary:,}"),
        ("DEDUCTION_SECTION", ""),  # 控除額セクションの開始マーカー
        ("控除額合計", f"¥{payroll_slip.total_deduction:,}"),
        ("実物支給額", "¥0"),
        ("差引支給額", f"¥{payroll_slip.net_salary:,}")
    ]
    
    # 各項目を描画
    allowance_section_index = 0
    for item_name, value in items:
        # 手当セクションの特別処理
        if item_name == "ALLOWANCE_SECTION":
            current_y = draw_allowance_section(canvas, font_name, allowance_items, x, current_y, table_width, row_height)
            continue
            
        # 控除額セクションの特別処理
        if item_name == "DEDUCTION_SECTION":
            current_y = draw_deduction_section(canvas, font_name, deduction_items, x, current_y, table_width)
            continue
            
        # 背景色とフォントの設定
        if item_name in ["小　　　計", "合　　　計", "控除額合計"]:
            canvas.setFillColor(colors.lightyellow)
            canvas.setFont(font_name, 10)
        elif item_name == "差引支給額":
            canvas.setFillColor(colors.lightblue)
            canvas.setFont(font_name, 12)
        elif item_name == "控除額":
            canvas.setFillColor(colors.lightgrey)
            canvas.setFont(font_name, 11)
        else:
            canvas.setFillColor(colors.white)
            canvas.setFont(font_name, 10)
        
        # 行を描画
        canvas.rect(x, current_y - row_height, table_width, row_height, fill=1, stroke=1)
        canvas.setFillColor(colors.black)
        
        # 中央の縦線
        canvas.line(x + table_width//2, current_y, x + table_width//2, current_y - row_height)
        
        # テキスト描画
        # 小計、賞与、合計は中央揃え、その他は均等割り付け
        item_name_width = table_width // 2 - 10  # 左半分から余白を引いた幅
        if item_name in ["小　　　計", "賞　　　与", "合　　　計"]:
            draw_centered_text(canvas, font_name, 10, item_name, x + 5, current_y - 12, item_name_width)
        else:
            draw_justified_text(canvas, font_name, 10, item_name, x + 5, current_y - 12, item_name_width)
        if value:  # 値がある場合のみ表示
            value_width = canvas.stringWidth(str(value), font_name, canvas._fontsize)
            canvas.drawString(x + table_width - value_width - 5, current_y - 12, str(value))  # 15→12に調整
        
        current_y -= row_height
        
        # 全項目を表示するため制限を削除
        # if current_y < 50:  # 制限削除：全項目を確実に表示
        #     break

def draw_allowance_section(canvas, font_name, allowance_items, x, current_y, table_width, row_height):
    """手当セクションを3列形式（縦書き「手当」、項目名、金額）で描画"""
    
    # 手当セクション全体の高さを計算
    allowance_section_height = row_height * len(allowance_items)
    
    # 3列の幅設定（中央線と境界線を揃える）
    col1_width = table_width // 8   # 縦書き「手当」列（12.5%）
    col2_width = table_width * 3 // 8   # 項目名列（37.5%）
    col3_width = table_width // 2   # 金額列（50%）
    
    # 手当セクション全体の枠線とレイアウトを描画
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1)
    canvas.setFillColor(colors.white)
    
    # 手当セクション全体の背景を描画
    canvas.rect(x, current_y - allowance_section_height, table_width, allowance_section_height, fill=1, stroke=1)
    
    # 1列目（手当列）: 上下結合された単一のセル - 横線は描画しない
    # 1列目の右境界線のみ描画
    canvas.line(x + col1_width, current_y, x + col1_width, current_y - allowance_section_height)
    
    # 2列目と3列目: 各行に分割された通常のセル
    # 2列目と3列目の境界線
    canvas.line(x + col1_width + col2_width, current_y, x + col1_width + col2_width, current_y - allowance_section_height)
    
    # 2列目と3列目のみに横線を描画（1列目は結合されているので横線なし）
    for i in range(1, len(allowance_items)):
        row_y = current_y - (row_height * i)
        # 1列目を除いた部分にのみ横線を描画
        canvas.line(x + col1_width, row_y, x + col1_width + col2_width + col3_width, row_y)
    
    # 縦書き「手当」テキストを左列に描画（中央に1回だけ）
    canvas.setFillColor(colors.black)
    canvas.setFont(font_name, 10)  # 他の項目と同じサイズに統一
    
    # 縦書きテキストのための位置計算
    text_x = x + col1_width // 2
    text_y_center = current_y - (allowance_section_height // 2)
    
    # 「手」と「当」を縦に配置
    canvas.drawCentredString(text_x, text_y_center + 8, "手")  # 10→8に調整
    canvas.drawCentredString(text_x, text_y_center - 8, "当")  # 10→8に調整
    
    # 各手当項目を描画
    canvas.setFont(font_name, 10)  # 他の項目と同じサイズに統一
    for i, (item_name, amount) in enumerate(allowance_items):
        item_y = current_y - (row_height * i) - 12  # 15→12に調整
        
        # 項目名列（2列目）
        if item_name:  # 空でない項目名のみ表示
            # 均等割り付けで描画
            item_width = col2_width - 10  # 項目名列の幅から余白を引く
            draw_justified_text(canvas, font_name, 10, item_name, x + col1_width + 5, item_y, item_width)
        
        # 金額列（3列目）- 新しい幅に調整
        if amount > 0:  # 金額が0より大きい場合のみ表示
            amount_text = f"¥{amount:,}"
            amount_width = canvas.stringWidth(amount_text, font_name, 10)  # フォントサイズを10ptに統一
            # 3列目の右端に合わせて配置
            canvas.drawString(x + col1_width + col2_width + col3_width - amount_width - 5, item_y, amount_text)
    
    return current_y - allowance_section_height

def draw_deduction_section(canvas, font_name, deduction_items, x, current_y, table_width):
    """控除額セクションを3列形式（縦書き「控除額」、項目名、金額）で描画"""
    
    # 行の高さを定義（他の部分と統一）
    row_height = 16  # 20→16に縮小
    
    # 控除額セクション全体の高さを計算
    deduction_section_height = row_height * len(deduction_items)
    
    # 3列の幅設定（中央線と境界線を揃える）
    col1_width = table_width // 8   # 縦書き「控除額」列（12.5%）
    col2_width = table_width * 3 // 8   # 項目名列（37.5%）
    col3_width = table_width // 2   # 金額列（50%）
    
    # 控除額セクション全体の枠線とレイアウトを描画
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1)
    canvas.setFillColor(colors.white)
    
    # 控除額セクション全体の背景を描画
    canvas.rect(x, current_y - deduction_section_height, table_width, deduction_section_height, fill=1, stroke=1)
    
    # 1列目（控除額列）: 上下結合された単一のセル - 横線は描画しない
    # 1列目の右境界線のみ描画
    canvas.line(x + col1_width, current_y, x + col1_width, current_y - deduction_section_height)
    
    # 2列目と3列目: 各行に分割された通常のセル
    # 2列目と3列目の境界線
    canvas.line(x + col1_width + col2_width, current_y, x + col1_width + col2_width, current_y - deduction_section_height)
    
    # 2列目と3列目のみに横線を描画（1列目は結合されているので横線なし）
    for i in range(1, len(deduction_items)):
        row_y = current_y - (row_height * i)
        # 1列目を除いた部分にのみ横線を描画
        canvas.line(x + col1_width, row_y, x + col1_width + col2_width + col3_width, row_y)
    
    # 縦書き「控除額」テキストを左列に描画（中央に1回だけ）
    canvas.setFillColor(colors.black)
    canvas.setFont(font_name, 10)  # 他の項目と同じサイズに統一
    
    # 縦書きテキストのための位置計算
    text_x = x + col1_width // 2
    text_y_center = current_y - (deduction_section_height // 2)
    
    # 「控」「除」「額」を縦に配置
    canvas.drawCentredString(text_x, text_y_center + 12, "控")  # 15→12に調整
    canvas.drawCentredString(text_x, text_y_center, "除")
    canvas.drawCentredString(text_x, text_y_center - 12, "額")  # 15→12に調整
    
    # 各控除項目を描画
    canvas.setFont(font_name, 10)  # 他の項目と同じサイズに統一
    for i, (item_name, amount) in enumerate(deduction_items):
        item_y = current_y - (row_height * i) - 12  # 15→12に調整
        
        # 項目名列（2列目）
        # 均等割り付けで描画
        item_width = col2_width - 10  # 項目名列の幅から余白を引く
        draw_justified_text(canvas, font_name, 10, item_name, x + col1_width + 5, item_y, item_width)
        
        # 金額列（3列目）- 新しい幅に調整
        if amount > 0:  # 金額が0より大きい場合のみ表示
            amount_text = f"¥{amount:,}"
            amount_width = canvas.stringWidth(amount_text, font_name, 10)  # フォントサイズを10ptに統一
            # 3列目の右端に合わせて配置
            canvas.drawString(x + col1_width + col2_width + col3_width - amount_width - 5, item_y, amount_text)
    
    return current_y - deduction_section_height

# 旧版関数は互換性のために維持（空の実装）
def draw_excel_integrated_table(canvas, font_name, payroll_slip, employee, payroll_calculation, x, y, table_width):
    """統合されたExcelライク表"""
    row_height = 18
    
    # 表の外枠
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1)
    
    # 勤怠情報セクション
    current_y = y
    canvas.setFont(font_name, 11)
    canvas.setFillColor(colors.lightgrey)
    canvas.rect(x, current_y - row_height, table_width, row_height, fill=1, stroke=1)
    canvas.setFillColor(colors.black)
    canvas.drawString(x + 5, current_y - 13, "勤怠情報")
    
    current_y -= row_height
    
    # 勤怠データ行
    attendance_data = [
        ["項目", "値", "項目", "値"],
        ["労働日数", f"{payroll_slip.working_days}日", "有給取得日数", f"{payroll_slip.paid_leave_days or 0}日"],
        ["所定労働時間", "160：00", "実労働時間", format_working_hours(payroll_calculation)]
    ]
    
    for row_data in attendance_data:
        canvas.setFillColor(colors.white)
        canvas.rect(x, current_y - row_height, table_width, row_height, fill=1, stroke=1)
        canvas.setFillColor(colors.black)
        
        col_width = table_width // 4
        for i, cell_data in enumerate(row_data):
            canvas.line(x + col_width * i, current_y, x + col_width * i, current_y - row_height)
            canvas.drawString(x + col_width * i + 5, current_y - 13, str(cell_data))
        
        current_y -= row_height
    
    current_y -= 5
    
    # 労働時間内訳セクション
    canvas.setFillColor(colors.lightgrey)
    canvas.rect(x, current_y - row_height, table_width, row_height, fill=1, stroke=1)
    canvas.setFillColor(colors.black)
    canvas.drawString(x + 5, current_y - 13, "労働時間内訳")
    
    current_y -= row_height
    
    # 時間内訳データ
    regular_hours = (payroll_calculation.regular_working_minutes or 0) // 60 if payroll_calculation else 0
    overtime_hours = (payroll_calculation.overtime_minutes or 0) // 60 if payroll_calculation else 0
    
    hours_data = [
        ["1倍", "0.25倍", "0.35倍", "深夜"],
        [f"{regular_hours}：00", f"{overtime_hours}：00", "0：00", "0：00"]
    ]
    
    for row_data in hours_data:
        canvas.setFillColor(colors.white)
        canvas.rect(x, current_y - row_height, table_width, row_height, fill=1, stroke=1)
        canvas.setFillColor(colors.black)
        
        col_width = table_width // 4
        for i, cell_data in enumerate(row_data):
            canvas.line(x + col_width * i, current_y, x + col_width * i, current_y - row_height)
            cell_x = x + col_width * i + col_width//2
            cell_width = canvas.stringWidth(str(cell_data), font_name, 11)
            canvas.drawString(cell_x - cell_width//2, current_y - 13, str(cell_data))
        
        current_y -= row_height
    
    current_y -= 10
    
    # 支給・控除セクション（左右分割）
    half_width = table_width // 2
    
    # 支給項目（左側）
    draw_payment_section(canvas, font_name, payroll_slip, x, current_y, half_width - 5)
    
    # 控除項目（右側）
    draw_old_deduction_section(canvas, font_name, payroll_slip, x + half_width + 5, current_y, half_width - 5)
    
    current_y -= 180  # 支給・控除表の高さ分
    
    # 差引支給額（強調表示）
    canvas.setFillColor(colors.lightblue)
    canvas.rect(x, current_y - row_height * 2, table_width, row_height * 2, fill=1, stroke=1)
    canvas.setFillColor(colors.black)
    canvas.setFont(font_name, 16)
    canvas.drawString(x + 10, current_y - 25, "差引支給額")
    net_salary_text = f"¥{payroll_slip.net_salary:,}"
    net_salary_width = canvas.stringWidth(net_salary_text, font_name, 16)
    canvas.drawString(x + table_width - net_salary_width - 10, current_y - 25, net_salary_text)

def draw_payment_section(canvas, font_name, payroll_slip, x, y, width):
    """支給項目セクション"""
    row_height = 18
    current_y = y
    
    # ヘッダー
    canvas.setFillColor(colors.lightgrey)
    canvas.rect(x, current_y - row_height, width, row_height, fill=1, stroke=1)
    canvas.setFillColor(colors.black)
    canvas.setFont(font_name, 11)
    canvas.drawString(x + 5, current_y - 13, "支給項目")
    
    current_y -= row_height
    
    # 支給データ
    payment_items = [
        ("基本給", payroll_slip.base_salary),
        ("割増手当", payroll_slip.overtime_allowance),
        ("賞与・その他", payroll_slip.other_allowance or 0),
        ("支給合計", payroll_slip.gross_salary)
    ]
    
    for i, (item, amount) in enumerate(payment_items):
        if i == len(payment_items) - 1:  # 最終行は強調
            canvas.setFillColor(colors.lightyellow)
        else:
            canvas.setFillColor(colors.white)
        
        canvas.rect(x, current_y - row_height, width, row_height, fill=1, stroke=1)
        canvas.setFillColor(colors.black)
        canvas.line(x + width//2, current_y, x + width//2, current_y - row_height)
        
        canvas.drawString(x + 5, current_y - 13, item)
        amount_text = f"¥{amount:,}"
        amount_width = canvas.stringWidth(amount_text, font_name, 11)
        canvas.drawString(x + width - amount_width - 5, current_y - 13, amount_text)
        
        current_y -= row_height

def draw_old_deduction_section(canvas, font_name, payroll_slip, x, y, width):
    """控除項目セクション（旧版）"""
    row_height = 18
    current_y = y
    
    # ヘッダー
    canvas.setFillColor(colors.lightgrey)
    canvas.rect(x, current_y - row_height, width, row_height, fill=1, stroke=1)
    canvas.setFillColor(colors.black)
    canvas.setFont(font_name, 11)
    canvas.drawString(x + 5, current_y - 13, "控除項目")
    
    current_y -= row_height
    
    # 控除データ
    deduction_items = [
        ("健康保険", payroll_slip.health_insurance),
        ("厚生年金", payroll_slip.pension_insurance),
        ("雇用保険", payroll_slip.employment_insurance),
        ("所得税", payroll_slip.income_tax),
        ("住民税", payroll_slip.resident_tax or 0),
        ("控除合計", payroll_slip.total_deduction)
    ]
    
    for i, (item, amount) in enumerate(deduction_items):
        if i == len(deduction_items) - 1:  # 最終行は強調
            canvas.setFillColor(colors.lightyellow)
        else:
            canvas.setFillColor(colors.white)
        
        canvas.rect(x, current_y - row_height, width, row_height, fill=1, stroke=1)
        canvas.setFillColor(colors.black)
        canvas.line(x + width//2, current_y, x + width//2, current_y - row_height)
        
        canvas.drawString(x + 5, current_y - 13, item)
        amount_text = f"¥{amount:,}"
        amount_width = canvas.stringWidth(amount_text, font_name, 11)
        canvas.drawString(x + width - amount_width - 5, current_y - 13, amount_text)
        
        current_y -= row_height

def draw_attendance_table(canvas, font_name, payroll_slip, payroll_calculation, y):
    """勤怠情報表を描画"""
    # タイトル
    canvas.setFont(font_name, 12)
    canvas.drawString(50, y, "【勤怠情報】")
    y -= 25
    
    # 表のヘッダー
    table_x = 50
    table_width = 500
    row_height = 20
    col_width = table_width // 4
    
    # ヘッダー行
    canvas.setFillColor(colors.lightgrey)
    canvas.rect(table_x, y - row_height, table_width, row_height, fill=1, stroke=1)
    canvas.setFillColor(colors.black)
    canvas.setFont(font_name, 10)
    
    headers = ["労働日数", "有給取得日数", "所定労働時間", "実労働時間"]
    for i, header in enumerate(headers):
        canvas.drawCentredString(table_x + col_width * i + col_width//2, y - 15, header)
    
    y -= row_height
    
    # データ行
    canvas.setFillColor(colors.white)
    canvas.rect(table_x, y - row_height, table_width, row_height, fill=1, stroke=1)
    canvas.setFillColor(colors.black)
    
    # 各セルの縦線
    for i in range(1, 4):
        canvas.line(table_x + col_width * i, y, table_x + col_width * i, y - row_height)
    
    data = [
        f"{payroll_slip.working_days}日",
        f"{payroll_slip.paid_leave_days or 0}日",
        "160：00",  # 所定労働時間（固定）
        format_working_hours(payroll_calculation)
    ]
    
    for i, value in enumerate(data):
        canvas.drawCentredString(table_x + col_width * i + col_width//2, y - 15, value)
    
    return y - row_height

def draw_working_hours_breakdown(canvas, font_name, payroll_calculation, y):
    """労働時間内訳表を描画"""
    # タイトル
    canvas.setFont(font_name, 12)
    canvas.drawString(50, y, "【労働時間内訳】")
    y -= 25
    
    # 表の設定
    table_x = 50
    table_width = 500
    row_height = 20
    col_width = table_width // 4
    
    # ヘッダー行
    canvas.setFillColor(colors.lightgrey)
    canvas.rect(table_x, y - row_height, table_width, row_height, fill=1, stroke=1)
    canvas.setFillColor(colors.black)
    canvas.setFont(font_name, 10)
    
    headers = ["1倍", "0.25倍", "0.35倍", "深夜"]
    for i, header in enumerate(headers):
        canvas.drawCentredString(table_x + col_width * i + col_width//2, y - 15, header)
    
    y -= row_height
    
    # データ行
    canvas.setFillColor(colors.white)
    canvas.rect(table_x, y - row_height, table_width, row_height, fill=1, stroke=1)
    canvas.setFillColor(colors.black)
    
    # 各セルの縦線
    for i in range(1, 4):
        canvas.line(table_x + col_width * i, y, table_x + col_width * i, y - row_height)
    
    # 時間内訳データ
    regular_hours = (payroll_calculation.regular_working_minutes or 0) // 60 if payroll_calculation else 0
    overtime_hours = (payroll_calculation.overtime_minutes or 0) // 60 if payroll_calculation else 0
    
    data = [
        f"{regular_hours}：00",  # 1倍
        f"{overtime_hours}：00",  # 0.25倍
        "0：00",  # 0.35倍
        "0：00"   # 深夜
    ]
    
    for i, value in enumerate(data):
        canvas.drawCentredString(table_x + col_width * i + col_width//2, y - 15, value)
    
    return y - row_height

def draw_payment_items_table(canvas, font_name, payroll_slip, y):
    """支給項目表を描画"""
    # タイトル
    canvas.setFont(font_name, 12)
    canvas.drawString(50, y, "【支給項目】")
    y -= 25
    
    # 表の設定
    table_x = 50
    table_width = 500
    row_height = 20
    
    items = [
        ("項目", "金額"),
        ("基本給", f"¥{payroll_slip.base_salary:,}"),
        ("割増", f"¥{payroll_slip.overtime_allowance:,}"),
        ("賞与", f"¥{payroll_slip.other_allowance or 0:,}"),
        ("小計", f"¥{payroll_slip.base_salary + payroll_slip.overtime_allowance + (payroll_slip.other_allowance or 0):,}"),
        ("合計", f"¥{payroll_slip.gross_salary:,}")
    ]
    
    for i, (item, amount) in enumerate(items):
        if i == 0:  # ヘッダー
            canvas.setFillColor(colors.lightgrey)
            canvas.rect(table_x, y - row_height, table_width, row_height, fill=1, stroke=1)
            canvas.setFillColor(colors.black)
            canvas.setFont(font_name, 10)
        else:
            canvas.setFillColor(colors.white)
            canvas.rect(table_x, y - row_height, table_width, row_height, fill=1, stroke=1)
            canvas.setFillColor(colors.black)
        
        # 中央の縦線
        canvas.line(table_x + table_width//2, y, table_x + table_width//2, y - row_height)
        
        # テキスト描画
        canvas.drawString(table_x + 10, y - 15, item)
        canvas.drawRightString(table_x + table_width - 10, y - 15, amount)
        
        y -= row_height
    
    return y

def draw_deduction_items_table(canvas, font_name, payroll_slip, y):
    """控除項目表を描画"""
    # タイトル
    canvas.setFont(font_name, 12)
    canvas.drawString(50, y, "【控除項目】")
    y -= 25
    
    # 表の設定
    table_x = 50
    table_width = 500
    row_height = 20
    
    items = [
        ("項目", "金額"),
        ("健康保険", f"¥{payroll_slip.health_insurance:,}"),
        ("厚生年金", f"¥{payroll_slip.pension_insurance:,}"),
        ("雇用保険", f"¥{payroll_slip.employment_insurance:,}"),
        ("所得税", f"¥{payroll_slip.income_tax:,}"),
        ("住民税", f"¥{payroll_slip.resident_tax or 0:,}"),
        ("合計", f"¥{payroll_slip.total_deduction:,}")
    ]
    
    for i, (item, amount) in enumerate(items):
        if i == 0:  # ヘッダー
            canvas.setFillColor(colors.lightgrey)
            canvas.rect(table_x, y - row_height, table_width, row_height, fill=1, stroke=1)
            canvas.setFillColor(colors.black)
            canvas.setFont(font_name, 10)
        else:
            canvas.setFillColor(colors.white)
            canvas.rect(table_x, y - row_height, table_width, row_height, fill=1, stroke=1)
            canvas.setFillColor(colors.black)
        
        # 中央の縦線
        canvas.line(table_x + table_width//2, y, table_x + table_width//2, y - row_height)
        
        # テキスト描画
        canvas.drawString(table_x + 10, y - 15, item)
        canvas.drawRightString(table_x + table_width - 10, y - 15, amount)
        
        y -= row_height
    
    return y

def draw_net_salary_bold(canvas, font_name, payroll_slip, y):
    """差引支給額を太字で表示"""
    # 背景色付きのボックス
    canvas.setFillColor(colors.lightblue)
    canvas.rect(50, y - 35, 500, 35, fill=1, stroke=1)
    
    # 太字テキスト
    canvas.setFillColor(colors.black)
    canvas.setFont(font_name, 16)
    canvas.drawString(60, y - 25, "差引支給額")
    canvas.drawRightString(540, y - 25, f"¥{payroll_slip.net_salary:,}")

# 旧版の関数は互換性のために保持（空の実装）
def draw_payment_deduction_section(canvas, font_name, payroll_slip, y):
    pass

def draw_net_salary_section(canvas, font_name, payroll_slip, y):
    pass

def format_overtime_hours(payroll_calculation):
    """時間外労働時間をフォーマット"""
    if not payroll_calculation or not payroll_calculation.overtime_minutes:
        return "0：00"
    
    overtime_minutes = payroll_calculation.overtime_minutes or 0
    hours = overtime_minutes // 60
    minutes = overtime_minutes % 60
    return f"{hours}：{minutes:02d}"

def draw_standard_payroll_format(canvas, font_name, payroll_slip, payroll_calculation, start_y):
    """旧版の互換性のために保持"""
    # 2列表フォーマットを使用
    draw_umebishi_payroll_format(canvas, font_name, payroll_slip, None, payroll_calculation, None)
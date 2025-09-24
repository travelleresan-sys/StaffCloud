"""
タイムカードPDF生成モジュール
労働時間入力データを基にタイムカードPDFを生成
"""

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import calendar
from datetime import datetime, date
import os

def create_timecard_pdf(employee, working_time_records, year, month):
    """
    タイムカードPDFを生成

    Args:
        employee: 従業員オブジェクト
        working_time_records: 労働時間記録のリスト
        year: 対象年
        month: 対象月

    Returns:
        PDFのバイナリデータ
    """

    # フォント設定
    try:
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'ipaexg.ttf')
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('IPAexGothic', font_path))
            font_name = 'IPAexGothic'
        else:
            font_name = 'Helvetica'
    except:
        font_name = 'Helvetica'

    # PDFバッファ作成
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           topMargin=15*mm, bottomMargin=15*mm,
                           leftMargin=15*mm, rightMargin=15*mm)

    # スタイル設定
    styles = getSampleStyleSheet()

    # コンテンツリスト
    content = []

    # タイトル
    title_style = styles['Title'].clone('title_style')
    title_style.fontName = font_name
    title_style.fontSize = 18
    title_style.alignment = 1  # 中央揃え
    title = Paragraph(f"タイムカード", title_style)
    content.append(title)
    content.append(Spacer(1, 10*mm))

    # 基本情報
    info_style = styles['Normal'].clone('info_style')
    info_style.fontName = font_name
    info_style.fontSize = 12

    basic_info = [
        [f"対象期間: {year}年{month}月", f"従業員ID: {employee.employee_id}"],
        [f"氏名: {employee.last_name} {employee.first_name}", f"部署: {employee.department or ''}"]
    ]

    basic_table = Table(basic_info, colWidths=[90*mm, 90*mm])
    basic_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
    ]))

    content.append(basic_table)
    content.append(Spacer(1, 10*mm))

    # 労働時間データをdict形式に変換
    work_data = {}
    for record in working_time_records:
        work_data[record.day] = record

    # 月のカレンダー情報取得
    cal = calendar.monthcalendar(year, month)

    # テーブルヘッダー
    headers = ['日', '曜日', '出勤時間', '退勤時間', '休憩時間', '労働時間', '時間外', '備考']

    # テーブルデータ準備
    table_data = [headers]

    # 各日のデータを作成
    month_days = calendar.monthrange(year, month)[1]
    for day in range(1, month_days + 1):
        day_date = date(year, month, day)
        weekday = day_date.strftime('%a')

        # 日本語曜日に変換
        weekday_jp = {
            'Mon': '月', 'Tue': '火', 'Wed': '水', 'Thu': '木',
            'Fri': '金', 'Sat': '土', 'Sun': '日'
        }.get(weekday, weekday)

        if day in work_data:
            record = work_data[day]

            # 時間フォーマット関数
            def format_time(minutes):
                if minutes is None or minutes == 0:
                    return ""
                hours = minutes // 60
                mins = minutes % 60
                return f"{hours:02d}:{mins:02d}"

            # 出勤・退勤時間
            start_time = record.start_time.strftime('%H:%M') if record.start_time else ""
            end_time = record.end_time.strftime('%H:%M') if record.end_time else ""

            # 休憩時間（分から時:分に変換）
            break_time = format_time(record.break_minutes)

            # 労働時間（分から時:分に変換）
            working_time = format_time(record.working_minutes)

            # 時間外労働（分から時:分に変換）
            overtime = format_time(record.overtime_minutes)

            # 備考
            remarks = ""
            if record.is_holiday:
                remarks += "休日 "
            if record.is_paid_leave:
                remarks += "有給 "
            if record.remarks:
                remarks += record.remarks

        else:
            # データなしの場合
            start_time = end_time = break_time = working_time = overtime = remarks = ""

        # 土日の背景色設定用にフラグを保持
        is_weekend = weekday in ['Sat', 'Sun']

        row = [str(day), weekday_jp, start_time, end_time, break_time, working_time, overtime, remarks]
        table_data.append(row)

    # テーブル作成
    col_widths = [15*mm, 15*mm, 20*mm, 20*mm, 20*mm, 20*mm, 20*mm, 50*mm]
    work_table = Table(table_data, colWidths=col_widths)

    # テーブルスタイル
    table_style = [
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        # ヘッダー行のスタイル
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
    ]

    # 土日の背景色設定
    for i, row in enumerate(table_data[1:], 1):  # ヘッダーをスキップ
        day = int(row[0])
        day_date = date(year, month, day)
        if day_date.weekday() >= 5:  # 土曜日(5)、日曜日(6)
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightblue))

    work_table.setStyle(TableStyle(table_style))
    content.append(work_table)

    # 月間集計
    content.append(Spacer(1, 10*mm))

    # 集計計算
    total_working_minutes = sum(record.working_minutes or 0 for record in working_time_records)
    total_overtime_minutes = sum(record.overtime_minutes or 0 for record in working_time_records)
    total_break_minutes = sum(record.break_minutes or 0 for record in working_time_records)
    working_days = len([r for r in working_time_records if r.working_minutes and r.working_minutes > 0])

    def format_total_time(minutes):
        if minutes == 0:
            return "0時間00分"
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}時間{mins:02d}分"

    summary_data = [
        ['項目', '時間/日数'],
        ['出勤日数', f"{working_days}日"],
        ['総労働時間', format_total_time(total_working_minutes)],
        ['総時間外労働', format_total_time(total_overtime_minutes)],
        ['総休憩時間', format_total_time(total_break_minutes)],
    ]

    summary_table = Table(summary_data, colWidths=[90*mm, 90*mm])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ]))

    content.append(summary_table)

    # 印刷日時
    content.append(Spacer(1, 10*mm))
    print_time = datetime.now().strftime('%Y年%m月%d日 %H:%M')
    print_info = Paragraph(f"印刷日時: {print_time}", info_style)
    content.append(print_info)

    # PDF生成
    doc.build(content)

    buffer.seek(0)
    return buffer.getvalue()
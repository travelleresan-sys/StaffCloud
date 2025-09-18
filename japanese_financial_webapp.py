#!/usr/bin/env python3
"""
日本の財務諸表Excel出力WebアプリケーションのFlask統合
"""

from flask import Flask, render_template, request, send_file, flash, redirect, url_for, make_response
from datetime import datetime
import io
from mixed_orientation_financial_generator import generate_mixed_orientation_financial_statements

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

@app.route('/')
def index():
    """メインページ"""
    return render_template('japanese_financial_index.html')

@app.route('/financial_statements', methods=['GET', 'POST'])
def financial_statements():
    """財務諸表生成ページ"""
    if request.method == 'POST':
        # フォームデータ取得
        company_name = request.form.get('company_name', '株式会社サンプル')
        fiscal_year = int(request.form.get('fiscal_year', datetime.now().year))

        try:
            # 混合レイアウトExcel生成
            output = generate_mixed_orientation_financial_statements(company_name, fiscal_year)

            # ファイル名生成
            filename = f"財務諸表_{company_name}_{fiscal_year}年.xlsx"

            # レスポンス作成
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        except Exception as e:
            flash(f'Excel生成エラー: {str(e)}', 'error')
            return redirect(url_for('financial_statements'))

    return render_template('japanese_financial_form.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
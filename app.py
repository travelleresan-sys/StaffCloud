from flask import Flask, render_template, redirect, url_for, request, flash
app = Flask(__name__)
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
from models import db, User, Employee
from models import LeaveCredit # Added for leave management
from datetime import date # Added for leave management
from models import LeaveRecord # Added for leave management

# 年次有給休暇の自動付与ロジック
def calculate_annual_leave_days(join_date, current_date=None):
    """
    日本の労働基準法に基づく年次有給休暇の付与日数を計算
    
    労働基準法第39条に基づく：
    - 6ヶ月継続勤務：10日付与
    - 1年6ヶ月継続勤務：11日付与
    - 2年6ヶ月継続勤務：12日付与
    - 以降1年ごとに1日追加（最大20日）
    """
    if current_date is None:
        current_date = date.today()
    
    # 入社日から現在までの勤続期間を計算
    years_of_service = (current_date - join_date).days / 365.25
    
    if years_of_service < 0.5:  # 6ヶ月未満
        return 0
    elif years_of_service < 1.5:  # 6ヶ月〜1年6ヶ月未満
        return 10
    elif years_of_service < 2.5:  # 1年6ヶ月〜2年6ヶ月未満
        return 11
    else:  # 2年6ヶ月以降
        # 2年6ヶ月以降は1年ごとに1日追加（最大20日）
        additional_days = min(int(years_of_service - 2.5), 8)  # 最大8日追加
        return 12 + additional_days

def should_auto_grant_leave(employee, current_date=None):
    """
    年次有給休暇の自動付与が必要かどうかを判定
    """
    if current_date is None:
        current_date = date.today()
    
    # 入社日から1年経過しているかチェック
    years_since_join = (current_date - employee.join_date).days / 365.25
    
    if years_since_join < 1:
        return False
    
    # 前回の自動付与日をチェック
    last_auto_grant = db.session.query(LeaveCredit)\
        .filter(LeaveCredit.employee_id == employee.id)\
        .filter(LeaveCredit.date_credited >= date(current_date.year - 1, current_date.month, current_date.day))\
        .order_by(LeaveCredit.date_credited.desc())\
        .first()
    
    # 前回の自動付与から1年経過していない場合は付与しない
    if last_auto_grant:
        years_since_last_grant = (current_date - last_auto_grant.date_credited).days / 365.25
        if years_since_last_grant < 1:
            return False
    
    return True

@app.route('/auto_grant_annual_leave')
@login_required
def auto_grant_annual_leave():
    if current_user.role != 'admin':
        flash('アクセス権がありません。')
        return redirect(url_for('leave_management'))
    
    try:
        current_date = date.today()
        granted_count = 0
        
        # 全従業員をチェック
        employees = Employee.query.filter_by(status='在籍中').all()
        
        for employee in employees:
            if should_auto_grant_leave(employee, current_date):
                # 法律に基づく付与日数を計算
                days_to_grant = calculate_annual_leave_days(employee.join_date, current_date)
                
                if days_to_grant > 0:
                    # 自動付与を記録
                    new_leave_credit = LeaveCredit(
                        employee_id=employee.id,
                        days_credited=days_to_grant,
                        date_credited=current_date
                    )
                    
                    db.session.add(new_leave_credit)
                    granted_count += 1
        
        if granted_count > 0:
            db.session.commit()
            flash(f'{granted_count}名の従業員に年次有給休暇を自動付与しました。')
        else:
            flash('自動付与対象の従業員はいませんでした。')
            
    except Exception as e:
        db.session.rollback()
        flash('自動付与処理中にエラーが発生しました。')
    
    return redirect(url_for('leave_management'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # 必ず後で変更してください
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'

# 画像アップロード用の設定
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# アップロードフォルダが存在しない場合は作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """アップロードされたファイルの拡張子をチェック"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_photo(file):
    """アップロードされた画像ファイルを安全に保存"""
    if file and file.filename and allowed_file(file.filename):
        # 安全なファイル名を生成（UUID + 元の拡張子）
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        safe_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(file_path)
        return safe_filename
    return None

# データベースとアプリケーションを連携
db.init_app(app)

# ログインマネージャーの設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ここから下が各ページの処理 ---

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('メールアドレスまたはパスワードが正しくありません。')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('アクセス権がありません。')
        return redirect(url_for('login'))
    
    employees = Employee.query.all()
    
    # 期限切れの警告フラグを計算（2か月/1か月の二段階）
    from datetime import date, timedelta
    today = date.today()
    threshold_60 = today + timedelta(days=60)
    threshold_30 = today + timedelta(days=30)

    def categorize(expiry):
        if not expiry:
            return 'none'
        if expiry <= today:
            return 'expired'
        if expiry <= threshold_30:
            return 'warn30'
        if expiry <= threshold_60:
            return 'warn60'
        return 'normal'

    for employee in employees:
        # 各レベルを算出
        employee.residence_card_level = categorize(employee.residence_card_expiry)
        employee.car_insurance_level = categorize(employee.car_insurance_expiry)

        # 後方互換（既存テンプレの参照があれば）
        level_map_to_old = {
            'none': 'none',
            'normal': 'normal',
            'warn60': 'warning',
            'warn30': 'warning',
            'expired': 'expired',
        }
        employee.residence_card_warning = level_map_to_old[employee.residence_card_level]
        employee.car_insurance_warning = level_map_to_old[employee.car_insurance_level]

        # 行背景は warn30 と expired のときのみ
        employee.is_bg_row = (
            employee.residence_card_level in ['warn30', 'expired'] or
            employee.car_insurance_level in ['warn30', 'expired']
        )
        # アイコンは warn30 と expired のときのみ
        employee.show_icon = (
            employee.residence_card_level in ['warn30', 'expired'] or
            employee.car_insurance_level in ['warn30', 'expired']
        )

    return render_template('dashboard.html', employees=employees)

@app.route('/add', methods=['POST'])
@login_required
def add_employee():
    if current_user.role != 'admin':
        flash('アクセス権がありません。')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date_str = request.form.get('birth_date')
        gender = request.form.get('gender')
        join_date_str = request.form.get('join_date')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        status = request.form.get('status')
        photo = request.files.get('photo')
        nationality = request.form.get('nationality')
        residence_card_expiry_str = request.form.get('residence_card_expiry')
        car_insurance_expiry_str = request.form.get('car_insurance_expiry')
        
        if name and join_date_str and status:
            try:
                # 日付文字列をDateオブジェクトに変換
                from datetime import datetime
                join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()
                
                # 生年月日の処理
                birth_date = None
                if birth_date_str:
                    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                
                # 在留カード期限の処理
                residence_card_expiry = None
                if residence_card_expiry_str:
                    residence_card_expiry = datetime.strptime(residence_card_expiry_str, '%Y-%m-%d').date()
                
                # 自動車保険満了日の処理
                car_insurance_expiry = None
                if car_insurance_expiry_str:
                    car_insurance_expiry = datetime.strptime(car_insurance_expiry_str, '%Y-%m-%d').date()
                
                # 画像ファイルの処理
                photo_filename = None
                if photo:
                    photo_filename = save_photo(photo)
                    if not photo_filename:
                        flash('画像ファイルの形式が正しくありません。PNG、JPG、JPEG、GIF形式のみ対応しています。')
                        return redirect(url_for('dashboard'))
                
                # 新しい従業員を作成
                new_employee = Employee(
                    name=name,
                    birth_date=birth_date,
                    gender=gender if gender else None,
                    join_date=join_date,
                    phone_number=phone_number if phone_number else None,
                    address=address if address else None,
                    photo_filename=photo_filename,
                    nationality=nationality if nationality else None,
                    residence_card_expiry=residence_card_expiry,
                    car_insurance_expiry=car_insurance_expiry,
                    status=status
                )
                
                # データベースに保存
                db.session.add(new_employee)
                db.session.commit()
                
                flash('従業員が正常に追加されました。')
                return redirect(url_for('dashboard'))
                
            except ValueError:
                flash('日付の形式が正しくありません。')
                return redirect(url_for('dashboard'))
        else:
            flash('必須項目（氏名、入社年月日、在籍状況）を入力してください。')
            return redirect(url_for('dashboard'))
    
    return redirect(url_for('dashboard'))

@app.route('/edit/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def edit_employee(employee_id):
    if current_user.role != 'admin':
        flash('アクセス権がありません。')
        return redirect(url_for('login'))
    
    employee = Employee.query.get_or_404(employee_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date_str = request.form.get('birth_date')
        gender = request.form.get('gender')
        join_date_str = request.form.get('join_date')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        status = request.form.get('status')
        photo = request.files.get('photo')
        nationality = request.form.get('nationality')
        residence_card_expiry_str = request.form.get('residence_card_expiry')
        car_insurance_expiry_str = request.form.get('car_insurance_expiry')
        
        if name and join_date_str and status:
            try:
                # 日付文字列をDateオブジェクトに変換
                from datetime import datetime
                join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()
                
                # 生年月日の処理
                birth_date = None
                if birth_date_str:
                    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                
                # 在留カード期限の処理
                residence_card_expiry = None
                if residence_card_expiry_str:
                    residence_card_expiry = datetime.strptime(residence_card_expiry_str, '%Y-%m-%d').date()
                
                # 自動車保険満了日の処理
                car_insurance_expiry = None
                if car_insurance_expiry_str:
                    car_insurance_expiry = datetime.strptime(car_insurance_expiry_str, '%Y-%m-%d').date()
                
                # 画像ファイルの処理
                if photo:
                    photo_filename = save_photo(photo)
                    if not photo_filename:
                        flash('画像ファイルの形式が正しくありません。PNG、JPG、JPEG、GIF形式のみ対応しています。')
                        return redirect(url_for('edit_employee', employee_id=employee_id))
                    employee.photo_filename = photo_filename
                
                # 従業員情報を更新
                employee.name = name
                employee.birth_date = birth_date
                employee.gender = gender if gender else None
                employee.join_date = join_date
                employee.phone_number = phone_number if phone_number else None
                employee.address = address if address else None
                employee.nationality = nationality if nationality else None
                employee.residence_card_expiry = residence_card_expiry
                employee.car_insurance_expiry = car_insurance_expiry
                employee.status = status
                
                # データベースに保存
                db.session.commit()
                
                flash('従業員情報が正常に更新されました。')
                return redirect(url_for('dashboard'))
                
            except ValueError:
                flash('日付の形式が正しくありません。')
        else:
            flash('必須項目（氏名、入社年月日、在籍状況）を入力してください。')
    
    return render_template('edit_employee.html', employee=employee)

@app.route('/delete/<int:employee_id>')
@login_required
def delete_employee(employee_id):
    if current_user.role != 'admin':
        flash('アクセス権がありません。')
        return redirect(url_for('login'))
    
    employee = Employee.query.get_or_404(employee_id)
    
    try:
        # 従業員を削除
        db.session.delete(employee)
        db.session.commit()
        
        flash('従業員が正常に削除されました。')
    except Exception as e:
        flash('従業員の削除中にエラーが発生しました。')
        db.session.rollback()
    
    return redirect(url_for('dashboard'))

@app.route('/leave_management')
@login_required
def leave_management():
    if current_user.role != 'admin':
        flash('アクセス権がありません。')
        return redirect(url_for('login'))
    
    # 全従業員を取得
    employees = Employee.query.all()
    
    # 各従業員の年休付与合計、取得合計、残日数を計算
    for employee in employees:
        # 年休付与合計
        total_credited = db.session.query(db.func.sum(LeaveCredit.days_credited))\
            .filter(LeaveCredit.employee_id == employee.id)\
            .scalar() or 0
        employee.total_leave_credited = total_credited
        
        # 年休取得合計
        total_taken = db.session.query(db.func.sum(LeaveRecord.days_taken))\
            .filter(LeaveRecord.employee_id == employee.id)\
            .scalar() or 0
        employee.total_leave_taken = total_taken
        
        # 残日数
        employee.remaining_leave = total_credited - total_taken
        
        # 法律に基づく付与日数
        employee.legal_leave_days = calculate_annual_leave_days(employee.join_date)
        
        # 次回自動付与予定日を計算
        if employee.status == '在籍中':
            # 前回の自動付与日を取得
            last_auto_grant = db.session.query(LeaveCredit)\
                .filter(LeaveCredit.employee_id == employee.id)\
                .order_by(LeaveCredit.date_credited.desc())\
                .first()
            
            if last_auto_grant:
                # 前回の付与日から1年後
                from datetime import timedelta
                employee.next_auto_grant_date = last_auto_grant.date_credited + timedelta(days=365)
            else:
                # 入社日から1年後
                from datetime import timedelta
                employee.next_auto_grant_date = employee.join_date + timedelta(days=365)
        else:
            employee.next_auto_grant_date = None
    
    return render_template('leave_management.html', employees=employees)

@app.route('/add_leave_credit', methods=['POST'])
@login_required
def add_leave_credit():
    if current_user.role != 'admin':
        flash('アクセス権がありません。')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        days_credited = request.form.get('days_credited')
        
        if employee_id and days_credited:
            try:
                employee_id = int(employee_id)
                days_credited = int(days_credited)
                
                # 従業員が存在するかチェック
                employee = Employee.query.get(employee_id)
                if not employee:
                    flash('指定された従業員が見つかりません。')
                    return redirect(url_for('leave_management'))
                
                # 年休付与を記録
                new_leave_credit = LeaveCredit(
                    employee_id=employee_id,
                    days_credited=days_credited,
                    date_credited=date.today()
                )
                
                db.session.add(new_leave_credit)
                db.session.commit()
                
                flash(f'{employee.name}に{days_credited}日分の年休を付与しました。')
                return redirect(url_for('leave_management'))
                
            except ValueError:
                flash('日数は正しい数値を入力してください。')
                return redirect(url_for('leave_management'))
        else:
            flash('従業員と日数を選択してください。')
            return redirect(url_for('leave_management'))
    
    return redirect(url_for('leave_management'))

@app.route('/add_leave_record', methods=['POST'])
@login_required
def add_leave_record():
    if current_user.role != 'admin':
        flash('アクセス権がありません。')
        return redirect(url_for('leave_management'))
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        date_taken_str = request.form.get('date_taken')
        days_taken = request.form.get('days_taken')
        
        if employee_id and date_taken_str and days_taken:
            try:
                employee_id = int(employee_id)
                days_taken = int(days_taken)
                
                # 日付文字列をDateオブジェクトに変換
                from datetime import datetime
                date_taken = datetime.strptime(date_taken_str, '%Y-%m-%d').date()
                
                # 従業員が存在するかチェック
                employee = Employee.query.get(employee_id)
                if not employee:
                    flash('指定された従業員が見つかりません。')
                    return redirect(url_for('leave_management'))
                
                # 年休取得を記録
                new_leave_record = LeaveRecord(
                    employee_id=employee_id,
                    date_taken=date_taken,
                    days_taken=days_taken
                )
                
                db.session.add(new_leave_record)
                db.session.commit()
                
                flash(f'{employee.name}の年休取得（{days_taken}日）を記録しました。')
                return redirect(url_for('leave_management'))
                
            except ValueError:
                flash('日数は正しい数値を入力してください。')
                return redirect(url_for('leave_management'))
        else:
            flash('従業員、取得日、日数を入力してください。')
            return redirect(url_for('leave_management'))
    
    return redirect(url_for('leave_management'))

# 他の従業員管理機能（追加、編集、削除）はここに追加していきます。

# --- 起動と初期設定のためのコマンド ---

if __name__ == '__main__':
    app.run(debug=True)
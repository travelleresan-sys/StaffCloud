from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date, datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'employee', 'system_admin', 'accounting', 'general_affairs', or 'hr_affairs'
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)  # 従業員との関連付け
    
    # 承認権限
    can_hr_approve = db.Column(db.Boolean, default=False)  # 人事承認権限
    can_director_approve = db.Column(db.Boolean, default=False)  # 取締役承認権限

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # '男性', '女性', 'その他'
    join_date = db.Column(db.Date, nullable=False, default=date.today)
    phone_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    photo_filename = db.Column(db.String(255), nullable=True)  # アップロードされた画像のファイル名
    nationality = db.Column(db.String(50), nullable=True)  # 国籍
    residence_card_expiry = db.Column(db.Date, nullable=True)  # 在留カード期限
    residence_card_filename = db.Column(db.String(255), nullable=True)  # 在留カード画像・PDFファイル名
    car_insurance_expiry = db.Column(db.Date, nullable=True)  # 自動車保険満了日
    car_insurance_filename = db.Column(db.String(255), nullable=True)  # 自動車保険証画像・PDFファイル名
    status = db.Column(db.String(10), nullable=False)  # '在籍中' or '退職済'
    
    # 管理者専用情報（個人画面では非表示）
    position = db.Column(db.String(100), nullable=True)  # 役職
    department = db.Column(db.String(100), nullable=True)  # 部署
    manager_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)  # 上司ID
    work_history = db.Column(db.Text, nullable=True)  # 経歴
    skills = db.Column(db.Text, nullable=True)  # スキル
    qualifications = db.Column(db.Text, nullable=True)  # 資格情報
    hire_type = db.Column(db.String(50), nullable=True)  # 雇用形態（正社員、契約社員、アルバイトなど）
    salary_grade = db.Column(db.String(10), nullable=True)  # 給与グレード
    
    # 給与・勤務関連情報（経理管理用）
    wage_type = db.Column(db.String(20), nullable=True)  # 給与形態（monthly, daily, hourly）
    base_wage = db.Column(db.Integer, nullable=True)  # 基本給（円）
    working_time_system = db.Column(db.String(50), nullable=True)  # 労働時間制（standard, flex, discretionary等）
    standard_working_hours = db.Column(db.Float, default=8.0)  # 1日標準労働時間
    standard_working_days = db.Column(db.Integer, default=5)  # 週標準労働日数
    
    # 年次有給休暇との関連付け
    leave_credits = db.relationship('LeaveCredit', backref='employee', lazy=True, cascade='all, delete-orphan')
    leave_records = db.relationship('LeaveRecord', backref='employee', lazy=True, cascade='all, delete-orphan')
    
    # 組織図用の自己参照関係
    subordinates = db.relationship('Employee', backref=db.backref('manager', remote_side='Employee.id'), lazy=True)
    
    # 人事評価との関連付け
    evaluations = db.relationship('PerformanceEvaluation', backref='employee', lazy=True, cascade='all, delete-orphan')

class LeaveCredit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    days_credited = db.Column(db.Integer, nullable=False)  # 付与日数
    date_credited = db.Column(db.Date, nullable=False, default=date.today)  # 付与日

class LeaveRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date_taken = db.Column(db.Date, nullable=False)  # 取得日
    days_taken = db.Column(db.Integer, nullable=False)  # 取得日数

# 企業情報モデル
class CompanySettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)  # 会社名
    company_code = db.Column(db.String(50), nullable=True)  # 会社コード
    company_address = db.Column(db.String(500), nullable=True)  # 会社住所（36協定用）
    address = db.Column(db.String(500), nullable=True)  # 所在地（企業基本情報用）
    company_postal_code = db.Column(db.String(10), nullable=True)  # 郵便番号
    company_phone = db.Column(db.String(20), nullable=True)  # 電話番号（36協定用）
    phone = db.Column(db.String(20), nullable=True)  # 電話番号（企業基本情報用）
    fax = db.Column(db.String(20), nullable=True)  # FAX番号
    email = db.Column(db.String(120), nullable=True)  # メールアドレス
    representative_name = db.Column(db.String(100), nullable=True)  # 代表者名
    representative = db.Column(db.String(100), nullable=True)  # 代表者（企業基本情報用）
    representative_position = db.Column(db.String(100), nullable=True)  # 代表者役職
    capital = db.Column(db.Integer, nullable=True)  # 資本金
    establishment_date = db.Column(db.Date, nullable=True)  # 設立日
    business_type = db.Column(db.String(200), nullable=True)  # 業種
    business_description = db.Column(db.Text, nullable=True)  # 事業内容詳細
    employee_count = db.Column(db.Integer, nullable=True)  # 従業員数
    
    # 会計年度設定
    fiscal_year_start_month = db.Column(db.Integer, nullable=True, default=4)  # 会計年度開始月（デフォルト4月）
    fiscal_year_start_day = db.Column(db.Integer, nullable=True, default=1)  # 会計年度開始日（デフォルト1日）
    
    created_at = db.Column(db.DateTime, nullable=False)  # 作成日時
    updated_at = db.Column(db.DateTime, nullable=False)  # 更新日時

# 労働基準監督署関連情報モデル
class LaborStandardsSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    labor_office_name = db.Column(db.String(200), nullable=True)  # 管轄労働基準監督署名
    labor_office_address = db.Column(db.String(500), nullable=True)  # 監督署住所
    
    # 36協定関連
    agreement_36_filed = db.Column(db.Boolean, default=False)  # 36協定届出済み
    agreement_36_submission_date = db.Column(db.Date, nullable=True)  # 36協定提出年月日
    agreement_36_period_start = db.Column(db.Date, nullable=True)  # 協定期間開始
    agreement_36_period_end = db.Column(db.Date, nullable=True)  # 協定期間終了
    agreement_36_expiry_date = db.Column(db.Date, nullable=True)  # 36協定期限切れ日（切れ期）
    max_overtime_hours_monthly = db.Column(db.Integer, nullable=True)  # 月間時間外労働上限時間
    max_overtime_hours_yearly = db.Column(db.Integer, nullable=True)  # 年間時間外労働上限時間
    
    # 就業規則
    work_rules_filed = db.Column(db.Boolean, default=False)  # 就業規則届出済み
    work_rules_last_updated = db.Column(db.Date, nullable=True)  # 就業規則最終更新日
    
    created_at = db.Column(db.DateTime, nullable=False)  # 作成日時
    updated_at = db.Column(db.DateTime, nullable=False)  # 更新日時

# 法定休日設定モデル
class LegalHolidaySettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # 週休の設定（曜日別法定休日設定）
    monday_legal_holiday = db.Column(db.Boolean, default=False)  # 月曜日を法定休日とするか
    tuesday_legal_holiday = db.Column(db.Boolean, default=False)  # 火曜日を法定休日とするか
    wednesday_legal_holiday = db.Column(db.Boolean, default=False)  # 水曜日を法定休日とするか
    thursday_legal_holiday = db.Column(db.Boolean, default=False)  # 木曜日を法定休日とするか
    friday_legal_holiday = db.Column(db.Boolean, default=False)  # 金曜日を法定休日とするか
    saturday_legal_holiday = db.Column(db.Boolean, default=False)  # 土曜日を法定休日とするか
    sunday_legal_holiday = db.Column(db.Boolean, default=False)  # 日曜日を法定休日とするか
    
    # 特定日の法定休日指定
    specific_date = db.Column(db.Date, nullable=True)  # 特定日（祝日など）
    specific_date_name = db.Column(db.String(100), nullable=True)  # 特定日名称
    specific_date_legal = db.Column(db.Boolean, default=False)  # 特定日を法定休日とするか
    
    # 週の起算日設定
    week_start_day = db.Column(db.Integer, default=0)  # 週の起算日（0=月曜日, 6=日曜日）
    
    created_at = db.Column(db.DateTime, nullable=False)  # 作成日時
    updated_at = db.Column(db.DateTime, nullable=False)  # 更新日時

# 36協定管理モデル（詳細版）
class Agreement36(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本情報
    business_type = db.Column(db.String(200), nullable=True)  # 事業の種類
    business_name = db.Column(db.String(200), nullable=True)  # 事業の名称
    business_postal_code = db.Column(db.String(10), nullable=True)  # 事業所在地（郵便番号）
    business_address = db.Column(db.String(500), nullable=True)  # 事業所在地（住所）
    business_phone = db.Column(db.String(20), nullable=True)  # 事業所在地（電話番号）
    
    # 協定の有効期間
    agreement_start_date = db.Column(db.Date, nullable=False)  # 協定有効期間開始日
    agreement_end_date = db.Column(db.Date, nullable=False)  # 協定有効期間終了日（開始日から1年間）
    
    # 時間外労働が必要な事由と業務（最大4つ）
    overtime_reason_1 = db.Column(db.Text, nullable=True)  # 時間外労働が必要な事由1
    overtime_reason_2 = db.Column(db.Text, nullable=True)  # 時間外労働が必要な事由2
    overtime_reason_3 = db.Column(db.Text, nullable=True)  # 時間外労働が必要な事由3
    overtime_reason_4 = db.Column(db.Text, nullable=True)  # 時間外労働が必要な事由4
    overtime_business_type_1 = db.Column(db.String(200), nullable=True)  # 業務の種類1
    overtime_business_type_2 = db.Column(db.String(200), nullable=True)  # 業務の種類2
    overtime_business_type_3 = db.Column(db.String(200), nullable=True)  # 業務の種類3
    overtime_business_type_4 = db.Column(db.String(200), nullable=True)  # 業務の種類4
    overtime_employee_count = db.Column(db.Integer, nullable=True)  # 従業員数
    
    # 法定労働時間を超える時間数
    overtime_hours_daily = db.Column(db.Integer, nullable=True)  # 法定労働時間を超える時間数（1日）
    overtime_hours_monthly = db.Column(db.Integer, nullable=True)  # 法定労働時間を超える時間数（1ヶ月）
    
    # 休日労働関連（最大4つ）
    holiday_work_reason_1 = db.Column(db.Text, nullable=True)  # 休日労働が必要な事由1
    holiday_work_reason_2 = db.Column(db.Text, nullable=True)  # 休日労働が必要な事由2
    holiday_work_reason_3 = db.Column(db.Text, nullable=True)  # 休日労働が必要な事由3
    holiday_work_reason_4 = db.Column(db.Text, nullable=True)  # 休日労働が必要な事由4
    holiday_work_business_type_1 = db.Column(db.String(200), nullable=True)  # 休日労働の業務の種類1
    holiday_work_business_type_2 = db.Column(db.String(200), nullable=True)  # 休日労働の業務の種類2
    holiday_work_business_type_3 = db.Column(db.String(200), nullable=True)  # 休日労働の業務の種類3
    holiday_work_business_type_4 = db.Column(db.String(200), nullable=True)  # 休日労働の業務の種類4
    holiday_work_employee_count = db.Column(db.Integer, nullable=True)  # 休日労働従事従業員数
    legal_holiday_days_count = db.Column(db.Integer, nullable=True)  # 労働可能な法定休日日数
    holiday_work_start_time = db.Column(db.Time, nullable=True)  # 労働可能な法定休日の始業時刻
    holiday_work_end_time = db.Column(db.Time, nullable=True)  # 労働可能な法定休日の終業時刻
    
    # 協定締結情報
    agreement_conclusion_date = db.Column(db.Date, nullable=False)  # 協定締結年月日
    
    # 労働者代表
    worker_representative_position = db.Column(db.String(100), nullable=True)  # 労働者代表の役職
    worker_representative_name = db.Column(db.String(100), nullable=True)  # 労働者代表の氏名
    worker_representative_employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)  # 労働者代表の従業員ID
    worker_representative_selection_method = db.Column(db.String(200), nullable=True)  # 協定の当事者の選出方法
    
    # 使用者
    employer_position = db.Column(db.String(100), nullable=True)  # 使用者の役職
    employer_name = db.Column(db.String(100), nullable=True)  # 使用者の氏名
    employer_employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)  # 使用者の従業員ID
    
    # 提出情報（履歴用）
    submission_date = db.Column(db.Date, nullable=True)  # 提出日
    labor_office_name = db.Column(db.String(200), nullable=True)  # 提出先労働基準監督署
    submission_method = db.Column(db.String(50), nullable=True)  # 提出方法
    document_number = db.Column(db.String(100), nullable=True)  # 届出番号
    
    # 状態管理
    is_active = db.Column(db.Boolean, default=True)  # 現在有効な協定かどうか
    status = db.Column(db.String(20), default='draft')  # draft/submitted/active/expired
    
    # 備考
    notes = db.Column(db.Text, nullable=True)  # 備考
    
    # メタ情報
    created_at = db.Column(db.DateTime, default=datetime.now)  # 作成日時
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 更新日時
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 作成者
    
    # リレーション
    creator = db.relationship('User', backref='created_agreements_36', foreign_keys=[created_by])
    worker_representative = db.relationship('Employee', backref='represented_agreements_36', foreign_keys=[worker_representative_employee_id])
    employer = db.relationship('Employee', backref='employer_agreements_36', foreign_keys=[employer_employee_id])

# 36協定提出履歴モデル（簡易版・後方互換性のため残す）
class Agreement36History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # 提出情報
    submission_date = db.Column(db.Date, nullable=False)  # 提出日
    period_start = db.Column(db.Date, nullable=False)  # 協定期間開始
    period_end = db.Column(db.Date, nullable=False)  # 協定期間終了
    expiry_date = db.Column(db.Date, nullable=False)  # 期限切れ日（切れ期）
    
    # 時間外労働上限
    max_overtime_hours_monthly = db.Column(db.Integer, nullable=False)  # 月間上限時間
    max_overtime_hours_yearly = db.Column(db.Integer, nullable=False)  # 年間上限時間
    
    # 届出詳細情報
    labor_office_name = db.Column(db.String(200), nullable=True)  # 提出先労働基準監督署
    submission_method = db.Column(db.String(50), nullable=True)  # 提出方法（窓口/郵送/電子申請）
    document_number = db.Column(db.String(100), nullable=True)  # 届出番号
    representative_name = db.Column(db.String(100), nullable=True)  # 提出時の代表者名
    
    # 備考・メモ
    notes = db.Column(db.Text, nullable=True)  # 備考
    
    # 状態管理
    is_active = db.Column(db.Boolean, default=True)  # 現在有効な協定かどうか
    status = db.Column(db.String(20), default='active')  # active/expired/superseded
    
    # メタ情報
    created_at = db.Column(db.DateTime, default=datetime.now)  # 登録日時
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 登録者
    
    # リレーション
    creator = db.relationship('User', backref='agreement_36_submissions')

class CompanyCalendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # イベント・休日名
    event_date = db.Column(db.Date, nullable=False)  # 日付
    event_type = db.Column(db.String(20), nullable=False)  # 'holiday' or 'event'
    description = db.Column(db.Text, nullable=True)  # 詳細説明
    is_recurring = db.Column(db.Boolean, default=False)  # 毎年繰り返しか
    created_at = db.Column(db.Date, default=date.today)  # 作成日
    updated_at = db.Column(db.Date, default=date.today, onupdate=date.today)  # 更新日

class CalendarSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(50), unique=True, nullable=False)  # 設定キー
    setting_value = db.Column(db.String(200), nullable=False)  # 設定値
    description = db.Column(db.Text, nullable=True)  # 説明
    created_at = db.Column(db.Date, default=date.today)  # 作成日
    updated_at = db.Column(db.Date, default=date.today, onupdate=date.today)  # 更新日

# 有給休暇申請モデル
class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False, default='annual_leave')  # 'annual_leave', 'bereavement', 'sick_leave', 'maternity_leave', 'special_leave'
    start_date = db.Column(db.Date, nullable=False)  # 休暇開始日
    end_date = db.Column(db.Date, nullable=False)  # 休暇終了日
    days_requested = db.Column(db.Integer, nullable=False)  # 申請日数
    reason = db.Column(db.Text, nullable=True)  # 申請理由
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'approved', 'rejected'
    admin_comment = db.Column(db.Text, nullable=True)  # 管理者コメント
    created_at = db.Column(db.DateTime, default=datetime.now)  # 申請日時
    reviewed_at = db.Column(db.DateTime, nullable=True)  # 承認・却下日時
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 承認・却下者
    
    # リレーション
    employee = db.relationship('Employee', backref='leave_requests')
    reviewer = db.relationship('User', backref='reviewed_requests')

# 個人情報更新申請モデル
class PersonalInfoRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    request_type = db.Column(db.String(50), nullable=False)  # 'address', 'phone', 'residence_card_expiry', 'car_insurance_expiry', 'residence_card_file', 'car_insurance_file'
    current_value = db.Column(db.Text, nullable=True)  # 現在の値
    new_value = db.Column(db.Text, nullable=True)  # 新しい値（ファイルアップロードの場合はファイル名）
    uploaded_filename = db.Column(db.String(255), nullable=True)  # アップロードファイル名
    reason = db.Column(db.Text, nullable=True)  # 変更理由
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'approved', 'rejected'
    admin_comment = db.Column(db.Text, nullable=True)  # 管理者コメント
    created_at = db.Column(db.DateTime, default=datetime.now)  # 申請日時
    reviewed_at = db.Column(db.DateTime, nullable=True)  # 承認・却下日時
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 承認・却下者
    
    # リレーション
    employee = db.relationship('Employee', backref='personal_info_requests')
    reviewer = db.relationship('User', backref='reviewed_personal_info_requests')

# 人事評価モデル
class PerformanceEvaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    evaluation_period = db.Column(db.String(20), nullable=False)  # 評価期間（例：2025年上期）
    overall_rating = db.Column(db.Float, nullable=True)  # 総合評価（1.0-5.0）
    
    # 評価項目別スコア
    performance_score = db.Column(db.Float, nullable=True)  # 業績評価（1.0-5.0）
    behavior_score = db.Column(db.Float, nullable=True)  # 行動評価（1.0-5.0）
    potential_score = db.Column(db.Float, nullable=True)  # 潜在能力評価（1.0-5.0）
    
    # コメント
    strengths = db.Column(db.Text, nullable=True)  # 強み
    areas_for_improvement = db.Column(db.Text, nullable=True)  # 改善点
    goals_next_period = db.Column(db.Text, nullable=True)  # 次期目標
    evaluator_comment = db.Column(db.Text, nullable=True)  # 評価者コメント
    
    # メタ情報
    evaluator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 評価者ID
    status = db.Column(db.String(20), nullable=False, default='draft')  # 'draft', 'submitted', 'hr_approved', 'director_approved', 'approved'
    created_at = db.Column(db.DateTime, default=datetime.now)  # 作成日時
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 更新日時
    
    # 承認プロセス情報
    hr_approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 人事承認者ID
    hr_approved_at = db.Column(db.DateTime, nullable=True)  # 人事承認日時
    hr_approval_comment = db.Column(db.Text, nullable=True)  # 人事承認コメント
    
    director_approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 取締役承認者ID
    director_approved_at = db.Column(db.DateTime, nullable=True)  # 取締役承認日時
    director_approval_comment = db.Column(db.Text, nullable=True)  # 取締役承認コメント
    
    # リレーション
    evaluator = db.relationship('User', backref='conducted_evaluations', foreign_keys=[evaluator_id])
    hr_approver = db.relationship('User', backref='hr_approved_evaluations', foreign_keys=[hr_approved_by])
    director_approver = db.relationship('User', backref='director_approved_evaluations', foreign_keys=[director_approved_by])

# 勤怠記録モデル
class WorkingTimeRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)  # 勤務日
    start_time = db.Column(db.Time, nullable=True)  # 開始時刻
    end_time = db.Column(db.Time, nullable=True)  # 終了時刻
    break_time_minutes = db.Column(db.Integer, default=0)  # 休憩時間（分）
    
    # 労働時間分類（分単位）
    regular_working_minutes = db.Column(db.Integer, default=0)  # 法定内労働時間
    legal_overtime_minutes = db.Column(db.Integer, default=0)  # 法定内残業時間
    overtime_minutes = db.Column(db.Integer, default=0)  # 法定外残業時間
    legal_holiday_minutes = db.Column(db.Integer, default=0)  # 法定内休日労働時間
    holiday_minutes = db.Column(db.Integer, default=0)  # 法定外休日労働時間
    night_working_minutes = db.Column(db.Integer, default=0)  # 深夜労働時間
    
    # 休暇・欠勤記録
    is_paid_leave = db.Column(db.Boolean, default=False)  # 有給休暇
    is_special_leave = db.Column(db.Boolean, default=False)  # 特別休暇
    is_absence = db.Column(db.Boolean, default=False)  # 欠勤
    is_company_closure = db.Column(db.Boolean, default=False)  # 会社都合の休業
    
    # メタ情報
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    input_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 入力者
    
    # リレーション
    employee = db.relationship('Employee', backref='working_time_records')

# 給与計算データモデル
class PayrollCalculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)  # 対象年
    month = db.Column(db.Integer, nullable=False)  # 対象月
    
    # 基本給与情報
    base_salary = db.Column(db.Integer, default=0)  # 基本給（円）
    wage_type = db.Column(db.String(20), nullable=False)  # 給与形態（monthly, daily, hourly）
    
    # 労働時間データ（分単位）
    regular_working_minutes = db.Column(db.Integer, default=0)  # 法定内労働時間
    legal_overtime_minutes = db.Column(db.Integer, default=0)  # 法定内残業時間
    overtime_minutes = db.Column(db.Integer, default=0)  # 法定外残業時間
    legal_holiday_minutes = db.Column(db.Integer, default=0)  # 法定内休日労働時間
    holiday_minutes = db.Column(db.Integer, default=0)  # 法定外休日労働時間
    night_working_minutes = db.Column(db.Integer, default=0)  # 深夜労働時間
    
    # 休暇データ
    paid_leave_days = db.Column(db.Float, default=0)  # 有給取得日数
    special_leave_days = db.Column(db.Float, default=0)  # 特別休暇日数
    absence_days = db.Column(db.Float, default=0)  # 欠勤日数
    
    # 諸手当
    position_allowance = db.Column(db.Integer, default=0)  # 役職手当
    transportation_allowance = db.Column(db.Integer, default=0)  # 交通費
    housing_allowance = db.Column(db.Integer, default=0)  # 住宅手当
    family_allowance = db.Column(db.Integer, default=0)  # 家族手当
    overtime_allowance = db.Column(db.Integer, default=0)  # 時間外手当
    night_allowance = db.Column(db.Integer, default=0)  # 深夜手当
    holiday_allowance = db.Column(db.Integer, default=0)  # 休日手当
    other_allowances = db.Column(db.Integer, default=0)  # その他手当
    
    # 控除項目
    health_insurance = db.Column(db.Integer, default=0)  # 健康保険料
    pension_insurance = db.Column(db.Integer, default=0)  # 厚生年金保険料
    employment_insurance = db.Column(db.Integer, default=0)  # 雇用保険料
    income_tax = db.Column(db.Integer, default=0)  # 所得税
    resident_tax = db.Column(db.Integer, default=0)  # 住民税
    other_deductions = db.Column(db.Integer, default=0)  # その他控除
    
    # 計算結果
    gross_salary = db.Column(db.Integer, default=0)  # 総支給額
    total_deductions = db.Column(db.Integer, default=0)  # 総控除額
    net_salary = db.Column(db.Integer, default=0)  # 差引支給額
    
    # メタ情報
    calculated_at = db.Column(db.DateTime, default=datetime.now)  # 計算日時
    calculated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 計算者
    is_finalized = db.Column(db.Boolean, default=False)  # 確定フラグ
    
    # リレーション
    employee = db.relationship('Employee', backref='payroll_calculations')
    calculator = db.relationship('User', foreign_keys=[calculated_by])
    
    # ユニーク制約（従業員・年・月で一意）
    __table_args__ = (db.UniqueConstraint('employee_id', 'year', 'month'),)

# 賃金台帳モデル（年間給与データ集約）
class WageRegister(db.Model):
    __tablename__ = 'wage_register'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    
    # 12ヶ月分の基本給与データ（JSON形式で効率保存）
    monthly_base_salary = db.Column(db.Text)  # {"1": 250000, "2": 250000, ...}
    monthly_overtime_allowance = db.Column(db.Text)
    monthly_holiday_allowance = db.Column(db.Text)
    monthly_night_allowance = db.Column(db.Text)
    monthly_position_allowance = db.Column(db.Text)
    monthly_transportation_allowance = db.Column(db.Text)
    monthly_housing_allowance = db.Column(db.Text)
    monthly_family_allowance = db.Column(db.Text)
    monthly_other_allowances = db.Column(db.Text)
    
    # 控除項目
    monthly_health_insurance = db.Column(db.Text)
    monthly_pension_insurance = db.Column(db.Text)
    monthly_employment_insurance = db.Column(db.Text)
    monthly_income_tax = db.Column(db.Text)
    monthly_resident_tax = db.Column(db.Text)
    monthly_other_deductions = db.Column(db.Text)
    
    # 支給・控除合計
    monthly_gross_salary = db.Column(db.Text)
    monthly_total_deductions = db.Column(db.Text)
    monthly_net_salary = db.Column(db.Text)
    
    # 労働時間データ
    monthly_working_days = db.Column(db.Text)
    monthly_overtime_hours = db.Column(db.Text)
    monthly_paid_leave_days = db.Column(db.Text)
    monthly_absence_days = db.Column(db.Text)
    
    # 年間合計（計算済み）
    annual_gross_salary = db.Column(db.Integer, default=0)
    annual_total_deductions = db.Column(db.Integer, default=0)
    annual_net_salary = db.Column(db.Integer, default=0)
    annual_overtime_hours = db.Column(db.Float, default=0.0)
    
    # メタデータ
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # リレーション
    employee = db.relationship('Employee', backref='wage_registers')
    
    def __repr__(self):
        return f'<WageRegister {self.employee_id}-{self.year}>'

# 給与明細書モデル（詳細版）
class PayrollSlip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    payroll_calculation_id = db.Column(db.Integer, db.ForeignKey('payroll_calculation.id'), nullable=False)
    slip_year = db.Column(db.Integer, nullable=False)  # 給与明細年
    slip_month = db.Column(db.Integer, nullable=False)  # 給与明細月
    
    # 基本給与項目
    base_salary = db.Column(db.Integer, default=0)  # 基本給
    overtime_allowance = db.Column(db.Integer, default=0)  # 残業手当
    holiday_allowance = db.Column(db.Integer, default=0)  # 休日手当
    night_allowance = db.Column(db.Integer, default=0)  # 深夜手当
    
    # 各種手当
    position_allowance = db.Column(db.Integer, default=0)  # 役職手当
    family_allowance = db.Column(db.Integer, default=0)  # 家族手当
    transportation_allowance = db.Column(db.Integer, default=0)  # 交通費
    housing_allowance = db.Column(db.Integer, default=0)  # 住宅手当
    meal_allowance = db.Column(db.Integer, default=0)  # 食事手当
    skill_allowance = db.Column(db.Integer, default=0)  # 技能手当
    
    # 新しい支給項目
    temporary_closure_compensation = db.Column(db.Integer, default=0)  # 臨時の休業補償
    salary_payment = db.Column(db.Integer, default=0)  # 給与
    bonus_payment = db.Column(db.Integer, default=0)  # 賞与
    
    other_allowance = db.Column(db.Integer, default=0)  # その他手当
    other_allowances_json = db.Column(db.Text)  # その他手当の詳細（JSON形式）
    
    # 総支給額
    gross_salary = db.Column(db.Integer, default=0)  # 総支給額
    
    # 法定控除
    health_insurance = db.Column(db.Integer, default=0)  # 健康保険料
    pension_insurance = db.Column(db.Integer, default=0)  # 厚生年金保険料
    employment_insurance = db.Column(db.Integer, default=0)  # 雇用保険料
    long_term_care_insurance = db.Column(db.Integer, default=0)  # 介護保険料
    income_tax = db.Column(db.Integer, default=0)  # 所得税
    resident_tax = db.Column(db.Integer, default=0)  # 住民税
    
    # 法定外控除
    company_pension = db.Column(db.Integer, default=0)  # 企業年金
    union_fee = db.Column(db.Integer, default=0)  # 組合費
    parking_fee = db.Column(db.Integer, default=0)  # 駐車場代
    uniform_fee = db.Column(db.Integer, default=0)  # 制服代
    other_deduction = db.Column(db.Integer, default=0)  # その他控除
    other_deductions_json = db.Column(db.Text)  # その他控除の詳細（JSON形式）
    
    # 総控除額・手取額
    total_deduction = db.Column(db.Integer, default=0)  # 総控除額
    net_salary = db.Column(db.Integer, default=0)  # 手取額（差引支給額）
    
    # 勤怠情報
    working_days = db.Column(db.Integer, default=0)  # 出勤日数
    absence_days = db.Column(db.Float, default=0)  # 欠勤日数
    paid_leave_days = db.Column(db.Float, default=0)  # 有給取得日数
    overtime_hours = db.Column(db.Float, default=0)  # 時間外労働時間
    
    # 備考
    remarks = db.Column(db.Text, nullable=True)  # 備考
    
    # メタ情報
    created_at = db.Column(db.DateTime, default=datetime.now)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    issued_at = db.Column(db.DateTime, nullable=True)  # 発行日時
    
    # リレーション
    employee = db.relationship('Employee', backref='payroll_slips')
    payroll_calculation = db.relationship('PayrollCalculation', backref='payroll_slip')
    creator = db.relationship('User', backref='created_payroll_slips')

# 従業員給与設定モデル（詳細版）
class EmployeePayrollSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    
    # 基本給与設定
    wage_type = db.Column(db.String(20), default='monthly')  # 給与形態（monthly/daily/hourly）
    base_salary = db.Column(db.Integer, default=0)  # 基本給・月給
    hourly_rate = db.Column(db.Integer, default=0)  # 時給
    daily_rate = db.Column(db.Integer, default=0)  # 日給
    
    # 各種手当設定
    position_allowance = db.Column(db.Integer, default=0)  # 役職手当
    family_allowance = db.Column(db.Integer, default=0)  # 家族手当
    transportation_allowance = db.Column(db.Integer, default=0)  # 交通費
    housing_allowance = db.Column(db.Integer, default=0)  # 住宅手当
    meal_allowance = db.Column(db.Integer, default=0)  # 食事手当
    skill_allowance = db.Column(db.Integer, default=0)  # 技能手当
    
    # 社会保険設定
    health_insurance_rate = db.Column(db.Float, default=4.95)  # 健康保険料率（%）
    pension_insurance_rate = db.Column(db.Float, default=9.15)  # 厚生年金保険料率（%）
    employment_insurance_rate = db.Column(db.Float, default=0.3)  # 雇用保険料率（%）
    long_term_care_insurance_rate = db.Column(db.Float, default=0.58)  # 介護保険料率（%、40歳以上）
    
    # 税金設定
    income_tax_type = db.Column(db.String(20), default='automatic')  # 所得税計算方法
    resident_tax = db.Column(db.Integer, default=0)  # 住民税（月額固定）
    
    # 法定外控除
    union_fee = db.Column(db.Integer, default=0)  # 組合費
    parking_fee = db.Column(db.Integer, default=0)  # 駐車場代
    uniform_fee = db.Column(db.Integer, default=0)  # 制服代
    
    # 有効期間
    effective_from = db.Column(db.Date, nullable=False, default=date.today)  # 適用開始日
    effective_until = db.Column(db.Date, nullable=True)  # 適用終了日
    
    # メタ情報
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # リレーション
    employee = db.relationship('Employee', backref='payroll_settings')

# 会計科目マスタ
class AccountingAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_code = db.Column(db.String(10), unique=True, nullable=False)  # 勘定科目コード
    account_name = db.Column(db.String(100), nullable=False)  # 勘定科目名
    account_type = db.Column(db.String(20), nullable=False)  # 資産、負債、純資産、収益、費用
    parent_account_id = db.Column(db.Integer, db.ForeignKey('accounting_account.id'), nullable=True)  # 親科目
    is_active = db.Column(db.Boolean, default=True)  # 使用可能フラグ
    bank_name = db.Column(db.String(100), nullable=True)  # 銀行名（預金口座の場合）
    branch_name = db.Column(db.String(100), nullable=True)  # 支店名（預金口座の場合）
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 自己参照リレーション
    children = db.relationship('AccountingAccount', backref=db.backref('parent', remote_side=[id]))

# 仕訳帳
class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.Date, nullable=False)  # 取引日
    description = db.Column(db.String(255), nullable=False)  # 摘要
    reference_number = db.Column(db.String(50), nullable=True)  # 伝票番号
    total_amount = db.Column(db.Integer, nullable=False)  # 合計金額
    partner_id = db.Column(db.Integer, db.ForeignKey('business_partner.id'), nullable=True)  # 取引先ID
    created_at = db.Column(db.DateTime, default=datetime.now)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # リレーション
    creator = db.relationship('User', backref='journal_entries')
    partner = db.relationship('BusinessPartner', backref='journal_entries')

# 仕訳明細
class JournalEntryDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounting_account.id'), nullable=False)
    debit_amount = db.Column(db.Integer, default=0)  # 借方金額
    credit_amount = db.Column(db.Integer, default=0)  # 貸方金額
    description = db.Column(db.String(255), nullable=True)  # 摘要
    
    # リレーション
    journal_entry = db.relationship('JournalEntry', backref='details')
    account = db.relationship('AccountingAccount', backref='journal_details')

# 総勘定元帳（集計用ビュー的なテーブル）
class GeneralLedger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounting_account.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    opening_balance = db.Column(db.Integer, default=0)  # 期首残高
    debit_total = db.Column(db.Integer, default=0)  # 借方合計
    credit_total = db.Column(db.Integer, default=0)  # 貸方合計
    closing_balance = db.Column(db.Integer, default=0)  # 期末残高
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # リレーション
    account = db.relationship('AccountingAccount', backref='ledger_entries')

# 簡単仕訳入力用の取引パターンマスター
class TransactionPattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pattern_name = db.Column(db.String(100), nullable=False)  # パターン名（例：商品・サービスの売上）
    category = db.Column(db.String(50), nullable=False)  # カテゴリ（売上関係、仕入関係、経費関係など）
    transaction_type = db.Column(db.String(20), nullable=False)  # 入金、出金、振替
    debit_account_code = db.Column(db.String(10), nullable=True)  # 借方勘定科目コード（現金・預金の場合はNULL）
    credit_account_code = db.Column(db.String(10), nullable=True)  # 貸方勘定科目コード（現金・預金の場合はNULL）
    main_account_side = db.Column(db.String(10), nullable=False)  # cash_debit（現金・預金が借方）またはcash_credit（現金・預金が貸方）
    tax_type = db.Column(db.String(20), default='課税')  # 課税、非課税、不課税
    description = db.Column(db.String(255), nullable=True)  # 説明
    is_active = db.Column(db.Boolean, default=True)  # 使用可能フラグ
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<TransactionPattern {self.pattern_name}>'

# 取引先管理
class BusinessPartner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    partner_code = db.Column(db.String(20), unique=True, nullable=False)  # 取引先コード
    partner_name = db.Column(db.String(100), nullable=False)  # 取引先名
    partner_type = db.Column(db.String(20), nullable=False)  # 種別（顧客、仕入先、その他）
    postal_code = db.Column(db.String(10), nullable=True)  # 郵便番号
    address = db.Column(db.String(255), nullable=True)  # 住所
    phone = db.Column(db.String(20), nullable=True)  # 電話番号
    fax = db.Column(db.String(20), nullable=True)  # FAX番号
    email = db.Column(db.String(100), nullable=True)  # メールアドレス
    contact_person = db.Column(db.String(50), nullable=True)  # 担当者名
    notes = db.Column(db.Text, nullable=True)  # 備考
    is_active = db.Column(db.Boolean, default=True)  # 使用可能フラグ
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<BusinessPartner {self.partner_name}>'

# 会計年度設定・繰越管理
class AccountingPeriod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fiscal_year = db.Column(db.Integer, nullable=False, unique=True)  # 会計年度（例：2024）
    start_date = db.Column(db.Date, nullable=False)  # 期首日（例：2024-04-01）
    end_date = db.Column(db.Date, nullable=False)  # 期末日（例：2025-03-31）
    is_closed = db.Column(db.Boolean, default=False)  # 期間締め済みフラグ
    closing_date = db.Column(db.DateTime, nullable=True)  # 締め処理実行日時
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<AccountingPeriod {self.fiscal_year}年度>'

# 期首残高・繰越残高管理
class OpeningBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fiscal_year = db.Column(db.Integer, nullable=False)  # 会計年度
    account_id = db.Column(db.Integer, db.ForeignKey('accounting_account.id'), nullable=False)
    opening_balance = db.Column(db.Integer, default=0)  # 期首残高（借方プラス、貸方マイナス）
    source_type = db.Column(db.String(20), default='manual')  # manual（手動入力）、carryover（繰越処理）
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # リレーション
    account = db.relationship('AccountingAccount', backref='opening_balances')
    
    # 複合一意制約（会計年度×勘定科目）
    __table_args__ = (db.UniqueConstraint('fiscal_year', 'account_id', name='unique_fiscal_year_account'),)
    
    def __repr__(self):
        return f'<OpeningBalance {self.fiscal_year}年度 {self.account.account_name if self.account else "Unknown"}>'
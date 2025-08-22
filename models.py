from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'employee'

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
    car_insurance_expiry = db.Column(db.Date, nullable=True)  # 自動車保険満了日
    status = db.Column(db.String(10), nullable=False)  # '在籍中' or '退職済'
    
    # 年次有給休暇との関連付け
    leave_credits = db.relationship('LeaveCredit', backref='employee', lazy=True, cascade='all, delete-orphan')
    leave_records = db.relationship('LeaveRecord', backref='employee', lazy=True, cascade='all, delete-orphan')

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
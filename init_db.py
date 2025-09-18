# 必要なツールをすべてインポートする
from app import app, db, User
from models import Employee, CompanyCalendar, CalendarSettings, LeaveCredit, LeaveRequest, PersonalInfoRequest, WorkingTimeRecord, PayrollCalculation
from werkzeug.security import generate_password_hash
from datetime import date

# アプリケーションのコンテキスト内で以下の処理を実行する
with app.app_context():
    
    print("データベースを作成しています...")
    # 既存のテーブルをすべて削除し、新しいテーブルを作成する（クリーンな状態にするため）
    db.drop_all()
    db.create_all()
    print("データベースの作成が完了しました。")

    # 既存の管理者ユーザーがいないかチェックする
    if User.query.filter_by(role='admin').first() is None:
        print("管理者ユーザーを作成しています...")
        # 管理者ユーザーのデータを作成
        admin_user = User(
            email='admin@example.com', 
            password=generate_password_hash('password', method='pbkdf2:sha256'), 
            role='admin',
            can_hr_approve=True,
            can_director_approve=True
        )
        # データベースに追加して保存
        db.session.add(admin_user)
        db.session.commit()
        print("管理者ユーザー'admin@example.com'がパスワード'password'で作成されました。")
    else:
        print("管理者ユーザーはすでに存在します。")
    
    # 経理ユーザーがいないかチェックする
    if User.query.filter_by(role='accounting').first() is None:
        print("経理ユーザーを作成しています...")
        # 経理ユーザーのデータを作成
        accounting_user = User(
            email='accounting@example.com', 
            password=generate_password_hash('accounting123', method='pbkdf2:sha256'), 
            role='accounting'
        )
        # データベースに追加して保存
        db.session.add(accounting_user)
        db.session.commit()
        print("経理ユーザー'accounting@example.com'がパスワード'accounting123'で作成されました。")
    else:
        print("経理ユーザーはすでに存在します。")
    
    # システム管理者ユーザーがいないかチェックする
    if User.query.filter_by(role='system_admin').first() is None:
        print("システム管理者ユーザーを作成しています...")
        # システム管理者ユーザーのデータを作成
        system_admin_user = User(
            email='system@example.com', 
            password=generate_password_hash('systemadmin123', method='pbkdf2:sha256'), 
            role='system_admin'
        )
        # データベースに追加して保存
        db.session.add(system_admin_user)
        db.session.commit()
        print("システム管理者ユーザー'system@example.com'がパスワード'systemadmin123'で作成されました。")
    else:
        print("システム管理者ユーザーはすでに存在します。")
    
    # サンプル従業員データを作成
    if Employee.query.count() == 0:
        print("サンプル従業員データを作成しています...")
        sample_employees = [
            {
                'name': '田中 太郎',
                'birth_date': date(1990, 4, 15),
                'gender': '男性',
                'join_date': date(2020, 4, 1),
                'phone_number': '080-1234-5678',
                'address': '東京都新宿区西新宿1-1-1',
                'nationality': '日本',
                'status': '在籍中'
            },
            {
                'name': '佐藤 花子',
                'birth_date': date(1985, 8, 22),
                'gender': '女性',
                'join_date': date(2018, 7, 15),
                'phone_number': '080-9876-5432',
                'address': '東京都渋谷区恵比寿1-2-3',
                'nationality': '日本',
                'status': '在籍中'
            }
        ]
        
        for employee_data in sample_employees:
            employee = Employee(**employee_data)
            # 給与関連情報を設定（サンプルデータ）
            employee.wage_type = 'monthly'  # 月給制
            employee.base_wage = 250000 if employee.name == '田中 太郎' else 230000  # 基本給
            employee.working_time_system = 'standard'  # 標準労働時間制
            employee.standard_working_hours = 8.0  # 1日8時間
            employee.standard_working_days = 5  # 週5日
            
            db.session.add(employee)
        
        db.session.commit()
        
        # 従業員用ユーザーアカウントを作成
        employees = Employee.query.all()
        for employee in employees:
            # メールアドレスを生成（名前から）
            email = f"employee{employee.id}@example.com"
            
            employee_user = User(
                email=email,
                password=generate_password_hash('employee123', method='pbkdf2:sha256'),
                role='employee',
                employee_id=employee.id
            )
            db.session.add(employee_user)
            
            # サンプル有給休暇付与
            leave_credit = LeaveCredit(
                employee_id=employee.id,
                days_credited=20,  # 年間20日付与
                date_credited=employee.join_date
            )
            db.session.add(leave_credit)
        
        db.session.commit()
        print(f"サンプル従業員データと従業員ユーザーアカウントを作成しました。")
        print("従業員ログイン情報:")
        for employee in employees:
            print(f"  - {employee.name}: employee{employee.id}@example.com / employee123")
    else:
        print("従業員データはすでに存在します。")
    
    # サンプル会社カレンダーイベントを追加
    sample_events = [
        {
            'title': '元日',
            'event_date': date(2024, 1, 1),
            'event_type': 'holiday',
            'description': '国民の祝日',
            'is_recurring': True
        },
        {
            'title': '成人の日',
            'event_date': date(2024, 1, 8),
            'event_type': 'holiday',
            'description': '国民の祝日',
            'is_recurring': True
        },
        {
            'title': '建国記念の日',
            'event_date': date(2024, 2, 11),
            'event_type': 'holiday',
            'description': '国民の祝日',
            'is_recurring': True
        },
        {
            'title': '春分の日',
            'event_date': date(2024, 3, 20),
            'event_type': 'holiday',
            'description': '国民の祝日',
            'is_recurring': True
        },
        {
            'title': '昭和の日',
            'event_date': date(2024, 4, 29),
            'event_type': 'holiday',
            'description': '国民の祝日',
            'is_recurring': True
        },
        {
            'title': 'こどもの日',
            'event_date': date(2024, 5, 5),
            'event_type': 'holiday',
            'description': '国民の祝日',
            'is_recurring': True
        },
        {
            'title': '会社創立記念日',
            'event_date': date(2024, 6, 15),
            'event_type': 'event',
            'description': '会社設立を記念する日',
            'is_recurring': True
        },
        {
            'title': '海の日',
            'event_date': date(2024, 7, 15),
            'event_type': 'holiday',
            'description': '国民の祝日',
            'is_recurring': True
        },
        {
            'title': '山の日',
            'event_date': date(2024, 8, 11),
            'event_type': 'holiday',
            'description': '国民の祝日',
            'is_recurring': True
        },
        {
            'title': '敬老の日',
            'event_date': date(2024, 9, 16),
            'event_type': 'holiday',
            'description': '国民の祝日',
            'is_recurring': True
        },
        {
            'title': '秋分の日',
            'event_date': date(2024, 9, 22),
            'event_type': 'holiday',
            'description': '国民の祝日',
            'is_recurring': True
        },
        {
            'title': 'スポーツの日',
            'event_date': date(2024, 10, 14),
            'event_type': 'holiday',
            'description': '国民の祝日',
            'is_recurring': True
        },
        {
            'title': '文化の日',
            'event_date': date(2024, 11, 3),
            'event_type': 'holiday',
            'description': '国民の祝日',
            'is_recurring': True
        },
        {
            'title': '勤労感謝の日',
            'event_date': date(2024, 11, 23),
            'event_type': 'holiday',
            'description': '国民の祝日',
            'is_recurring': True
        },
        {
            'title': '忘年会',
            'event_date': date(2024, 12, 15),
            'event_type': 'event',
            'description': '年末恒例の忘年会',
            'is_recurring': True
        }
    ]
    
    # サンプルイベントを追加（既に存在しない場合）
    print("サンプルカレンダーイベントを追加しています...")
    added_count = 0
    for event_data in sample_events:
        existing_event = CompanyCalendar.query.filter_by(
            title=event_data['title'],
            event_date=event_data['event_date']
        ).first()
        
        if not existing_event:
            event = CompanyCalendar(**event_data)
            db.session.add(event)
            added_count += 1
    
    if added_count > 0:
        db.session.commit()
        print(f"{added_count}件のカレンダーイベントを追加しました。")
    else:
        print("カレンダーイベントはすでに存在します。")
    
    # デフォルト設定を追加
    default_settings = [
        {
            'setting_key': 'start_month',
            'setting_value': '1',
            'description': 'カレンダー表示開始月（1-12）'
        }
    ]
    
    print("デフォルト設定を追加しています...")
    settings_added = 0
    for setting_data in default_settings:
        existing_setting = CalendarSettings.query.filter_by(
            setting_key=setting_data['setting_key']
        ).first()
        
        if not existing_setting:
            setting = CalendarSettings(**setting_data)
            db.session.add(setting)
            settings_added += 1
    
    if settings_added > 0:
        db.session.commit()
        print(f"{settings_added}件のデフォルト設定を追加しました。")
    else:
        print("デフォルト設定はすでに存在します。")

print("初期設定が完了しました。")

# 必要なツールをすべてインポートする
from app import app, db, User
from werkzeug.security import generate_password_hash

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
            role='admin'
        )
        # データベースに追加して保存
        db.session.add(admin_user)
        db.session.commit()
        print("管理者ユーザー'admin@example.com'がパスワード'password'で作成されました。")
    else:
        print("管理者ユーザーはすでに存在します。")

print("初期設定が完了しました。")

from flask import Flask
from config import Config
from flask_app.extensions import db, migrate, jwt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Khởi tạo extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Đăng ký blueprint
    from flask_app.controllers.auth import auth_bp
    from flask_app.controllers.expense import expense_bp
    from flask_app.controllers.income import income_bp
    from flask_app.controllers.notification import notification_bp
    from flask_app.controllers.overview import overview_bp
    from flask_app.controllers.user_item import user_item_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(expense_bp, url_prefix='/api/expenses')
    app.register_blueprint(income_bp, url_prefix='/api/incomes')
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')
    app.register_blueprint(overview_bp, url_prefix='/api/overview')
    app.register_blueprint(user_item_bp, url_prefix='/api/user-items')

    return app
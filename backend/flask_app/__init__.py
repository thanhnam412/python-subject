import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_app.extensions import jwt
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # Import models here to register them with SQLAlchemy
    from flask_app.models.user import User
    from flask_app.models.expense import Expense
    from flask_app.models.income import Income
    from flask_app.models.notification import Notification
    from flask_app.models.user_item import UserItem

    # Register blueprints
    from flask_app.controllers.auth import auth_bp
    from flask_app.controllers.expense import expense_bp
    from flask_app.controllers.income import income_bp
    from flask_app.controllers.notification import notification_bp
    from flask_app.controllers.overview import overview_bp
    from flask_app.controllers.user_item import user_item_bp
    from flask_app.controllers.search import search_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(expense_bp, url_prefix='/api/expenses')
    app.register_blueprint(income_bp, url_prefix='/api/incomes')
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')
    app.register_blueprint(overview_bp, url_prefix='/api/overview')
    app.register_blueprint(user_item_bp, url_prefix='/api/user-items')
    app.register_blueprint(search_bp, url_prefix='/api/search')



    return app
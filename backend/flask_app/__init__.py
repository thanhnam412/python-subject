from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_app.database import init_db
from flask_app.controllers.auth_controller import auth_bp
from flask_app.controllers.expense_controller import expense_bp
from flask_app.controllers.income_controller import income_bp
from flask_app.controllers.debt_controller import debt_bp
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(
        app,
        resources={r"/*": {"origins": "http://localhost:3000"}},
        supports_credentials=True,
    )

    init_db(app)

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = True
    app.config["JWT_ACCESS_CSRF_HEADER_NAME"] = "X-CSRF-TOKEN"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 86400)
    )
    JWTManager(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(expense_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(debt_bp)

    return app

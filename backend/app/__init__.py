from flask import Flask
from flask_login import LoginManager
import mysql.connector
from datetime import datetime

class User:
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '757805'
    app.config['MYSQL_DB'] = 'QLCT'

    def get_db_connection():
        return mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )

    app.get_db_connection = get_db_connection

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'views.login'

    @login_manager.user_loader
    def load_user(user_id):
        connection = app.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user:
            return User(user['user_id'], user['username'], user['email'])
        return None

    from views import views
    app.register_blueprint(views)

    @app.template_filter('format_currency')
    def format_currency(value):
        return "{:,.2f}".format(float(value))

    @app.template_filter('datetimeformat')
    def datetimeformat(value):
        if value == 'now':
            return datetime.now().strftime('%b %d, %Y')
        return value.strftime('%b %d, %Y')

    return app
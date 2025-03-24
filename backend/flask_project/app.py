from flask import Flask
from flask_login import LoginManager
from views import views  
from auth import auth
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '757805'
app.config['MYSQL_DB'] = 'QLCT'
app.config['MYSQL_PORT'] = 3306

def get_db_connection():
    try:
        port = int(app.config['MYSQL_PORT'])
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            port=port
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES LIKE 'QLCT'")
            result = cursor.fetchone()
            if not result:
                print("Cơ sở dữ liệu QLCT không tồn tại. Vui lòng tạo cơ sở dữ liệu trước khi tiếp tục.")
                cursor.close()
                connection.close()
                return None

            connection.database = app.config['MYSQL_DB']
            print("Kết nối thành công đến MySQL database: QLCT")
            cursor.close()
        return connection
    except ValueError as ve:
        print(f"Lỗi: Giá trị port phải là một số nguyên. Giá trị hiện tại: {app.config['MYSQL_PORT']}. Chi tiết lỗi: {ve}")
        return None
    except Error as e:
        print(f"Lỗi kết nối đến MySQL: {e}")
        return None

app.get_db_connection = get_db_connection

app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    db = get_db_connection()
    if db is None:
        print("Không thể kết nối đến cơ sở dữ liệu. Trả về None cho user.")
        return None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        if user:
            from models import User
            return User(user['user_id'], user['username'], user['password'])
        return None
    except Error as e:
        print(f"Lỗi khi thực hiện truy vấn: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True)
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from flask import current_app
from werkzeug.security import check_password_hash
from models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Vui lòng nhập đầy đủ tên người dùng và mật khẩu.', 'error')
            return redirect(url_for('auth.login'))

        db = current_app.get_db_connection()
        if db is None:
            flash('Không thể kết nối đến cơ sở dữ liệu. Vui lòng thử lại sau.', 'error')
            return redirect(url_for('auth.login'))

        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()
            if user:
                print(f"User found: {user}")  
            else:
                print(f"No user found with username: {username}")  

            cursor.close()
            db.close()

            if user and check_password_hash(user['password'], password):
                user_obj = User(user['user_id'], user['username'], user['password'])
                login_user(user_obj)
                flash('Đăng nhập thành công!', 'success')
                return redirect(url_for('views.home'))
            else:
                flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'error')
        except Exception as e:
            flash(f'Đã xảy ra lỗi: {str(e)}', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đăng xuất thành công!', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Vui lòng nhập đầy đủ tên người dùng và mật khẩu.', 'error')
            return redirect(url_for('auth.register'))

        db = current_app.get_db_connection()
        if db is None:
            flash('Không thể kết nối đến cơ sở dữ liệu. Vui lòng thử lại sau.', 'error')
            return redirect(url_for('auth.register'))

        try:
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác.', 'error')
                cursor.close()
                db.close()
                return redirect(url_for('auth.register'))

            from werkzeug.security import generate_password_hash
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
            db.commit()
            cursor.close()
            db.close()

            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Đã xảy ra lỗi: {str(e)}', 'error')
            return redirect(url_for('auth.register'))

    return render_template('register.html')
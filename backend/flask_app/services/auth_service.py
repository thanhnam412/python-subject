from werkzeug.security import generate_password_hash
from flask_app.models.user import User
from flask_app import db

class AuthService:
    @staticmethod
    def create_user(username, email, password):
        if User.query.filter_by(username=username).first():
            return None, 'Tên người dùng đã tồn tại'
        if User.query.filter_by(email=email).first():
            return None, 'Email đã tồn tại'
            
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user, None

    @staticmethod
    def authenticate_user(username, password):
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return None, 'Tên người dùng hoặc mật khẩu không hợp lệ'
        return user, None
import os

class Config:
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'  
    MYSQL_PASSWORD = '757805'  
    MYSQL_DB = 'QLCT'
    MYSQL_CURSORCLASS = 'DictCursor'

    SECRET_KEY = os.environ.get('KEY', 'your-secret-key')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your-jwt-secret-key'
    SESSION_COOKIE_SECURE = False 

    SWAGGER = {
        "title": "Expense Tracker API",
        "uiversion": 3
    }
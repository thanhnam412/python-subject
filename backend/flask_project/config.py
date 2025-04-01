import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    if not MYSQL_PASSWORD:
        raise ValueError("MYSQL_PASSWORD is not set in the environment variables")
    MYSQL_DB = os.getenv("MYSQL_DB", "QLCT")
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is not set in the environment variables")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")
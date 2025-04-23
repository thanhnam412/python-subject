from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def init_db(app):
    mysql_host = os.getenv("MYSQL_HOST", "localhost")
    mysql_user = os.getenv("MYSQL_USER", "root")
    mysql_password = os.getenv("MYSQL_PASSWORD", "")
    mysql_database = os.getenv("MYSQL_DATABASE", "finance_app")
    mysql_port = os.getenv("MYSQL_PORT", "3306")

    try:
        connection = mysql.connector.connect(
            host=mysql_host, user=mysql_user, password=mysql_password, port=mysql_port
        )
        cursor = connection.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {mysql_database}")
        cursor.close()
        connection.close()

        print(f"Database '{mysql_database}' created successfully or already exists")
    except Error as e:
        print(f"Error creating database: {e}")
        raise e

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
    )

    db.init_app(app)

    with app.app_context():
        db.create_all()
        print("Database tables created successfully")

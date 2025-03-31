from flask import Flask
from markupsafe import escape
import os
import routes

host = "localhost"

try:
    be_port = os.environ["BE_PORT"]
    db_port = os.environ["DB_PORT"]
    db_user = os.environ["DB_USER"]
    db_name = os.environ["DB_NAME"]
    db_password = ""
except:
    be_port = "8080"
    db_port = "5432"
    db_user = "cps"
    db_name = "test"
    db_password = ""


app = Flask(__name__)


def create_app():
    app = Flask(__name__)

    return app


@app.route("/")
def hello_world():
    return {"message": "Hello"}


@app.route("/user/<username>")
def show_user_profile(username):
    return f"User {escape(username)}"


import mysql.connector


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


if __name__ == "__main__":
    app.run(host="localhost", port="8080", debug=True)

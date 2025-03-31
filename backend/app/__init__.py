from flask import Flask
from markupsafe import escape
from init import get_db_connection

import routes


app = Flask(__name__)
conn = get_db_connection()


@app.route("/")
def hello_world():
    return {"message": "Hello"}


@app.route("/user/<username>")
def show_user_profile(username):
    return f"User {escape(username)}"


# @app.route('/')
# def index():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM users;")
#     users = cur.fetchall()
#     cur.close()
#     conn.close()
#     return f"Danh sách người dùng: {users}"


if __name__ == "__main__":
    app.run(host="localhost", port="8080", debug=True)

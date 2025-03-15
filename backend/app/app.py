from flask import Flask
from markupsafe import escape
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/user/<username>')
def show_user_profile(username):
    return f'User {escape(username)}'

# app = Flask(__name__)

# def get_db_connection():
#     conn = psycopg2.connect(
#         host="localhost",
#         port="5432",
#         user="cps",
#         password="password",
#         database="database_name",
#     )
#     return conn

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
    app.run( host="localhost", port="8080" )
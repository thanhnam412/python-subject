from flask import Flask
from markupsafe import escape
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/user/<username>')
def show_user_profile(username):
    return f'User {escape(username)}'

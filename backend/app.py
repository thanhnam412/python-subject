from flask_app import create_app, db
from flask_app.models import User, Expense, Income, Notification, UserItem

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Expense': Expense,
        'Income': Income,
        'Notification': Notification,
        'UserItem': UserItem
    }

if __name__ == '__main__':
    app.run(debug=True)
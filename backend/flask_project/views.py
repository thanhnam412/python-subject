from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta

views = Blueprint('views', __name__)

def get_all_accounts(app, user_id):
    db = app.get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM accounts WHERE user_id = %s', (user_id,))
    accounts = cursor.fetchall()
    cursor.close()
    db.close()
    return accounts

def get_goal(app, user_id):
    db = app.get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM goals WHERE user_id = %s', (user_id,))
    goal = cursor.fetchone()
    cursor.close()
    db.close()
    return goal

def get_upcoming_bills(app, user_id):
    db = app.get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM bills WHERE user_id = %s AND due_date >= CURDATE() ORDER BY due_date LIMIT 2', (user_id,))
    bills = cursor.fetchall()
    cursor.close()
    db.close()
    return bills

def get_all_transactions(app, user_id):
    db = app.get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM transactions WHERE user_id = %s ORDER BY transaction_date DESC LIMIT 5', (user_id,))
    transactions = cursor.fetchall()
    cursor.close()
    db.close()
    return transactions

def get_weekly_stats(app, user_id):
    db = app.get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT DATE(transaction_date) as day, SUM(amount) as total FROM transactions WHERE user_id = %s AND transaction_date >= DATE_SUB(CURDATE(), INTERVAL 14 DAY) GROUP BY DATE(transaction_date)', (user_id,))
    stats = cursor.fetchall()
    cursor.close()
    db.close()
    return stats

def get_expense_analysis(user_id):
    db = current_app.get_db_connection()
    if db is None:
        print("Không thể kết nối đến cơ sở dữ liệu trong get_expense_analysis.")
        return []

    try:
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT c.category_name, SUM(t.amount) as total 
        FROM transactions t 
        JOIN categories c ON t.category_id = c.category_id 
        WHERE t.user_id = %s AND t.transaction_type = 'expense' 
        GROUP BY c.category_name
        """
        cursor.execute(query, (user_id,))
        expense_analysis = cursor.fetchall()
        cursor.close()
        db.close()
        return expense_analysis
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu phân tích chi tiêu: {e}")
        return []

def get_all_categories(app, user_id):
    db = app.get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM categories WHERE user_id = %s OR user_id IS NULL', (user_id,))
    categories = cursor.fetchall()
    cursor.close()
    db.close()
    return categories

@views.route('/')
@login_required
def home():
    user_id = current_user.id
    username = current_user.username

    accounts = get_all_accounts(current_app, user_id)
    total_balance = sum([account['balance'] for account in accounts]) if accounts else 0.0
    total_balance = "{:,.0f}".format(total_balance)
    for account in accounts:
        account['balance'] = "{:,.0f}".format(account['balance'])

    goal = get_goal(current_app, user_id)
    if goal:
        goal['budget'] = "{:,.0f}".format(goal['budget'])
        goal['progress'] = 12500  
        goal['progress_percentage'] = (goal['progress'] / float(goal['budget'].replace(',', ''))) * 100

    bills = get_upcoming_bills(current_app, user_id)

    transactions = get_all_transactions(current_app, user_id)
    for transaction in transactions:
        transaction['amount'] = "{:,.0f}".format(transaction['amount'])

    weekly_stats = get_weekly_stats(current_app, user_id)
    labels = ['17 Sun', '18 Mon', '19 Tue', '20 Wed', '21 Thu', '22 Fri', '23 Sat']
    this_week_data = [0] * 7
    last_week_data = [0] * 7
    today = datetime.today()
    for stat in weekly_stats:
        day = stat['day'].day
        if today.day - 7 <= day <= today.day:
            idx = day - 17
            if 0 <= idx < 7:
                this_week_data[idx] = stat['total']
        elif today.day - 14 <= day < today.day - 7:
            idx = day - 10
            if 0 <= idx < 7:
                last_week_data[idx] = stat['total']

    expense_analysis = get_expense_analysis(current_user.id)
    
    return render_template('home.html', 
                          username=username,
                          total_balance=total_balance,
                          accounts=accounts,
                          goal=goal,
                          bills=bills,
                          transactions=transactions,
                          labels=labels,  
                          this_week_data=this_week_data,  
                          last_week_data=last_week_data,  
                          expense_analysis=expense_analysis)

# Route để thêm tài khoản
@views.route('/add-account', methods=['GET', 'POST'])
@login_required
def add_account():
    if request.method == 'POST':
        account_type = request.form.get('account_type')
        balance = float(request.form.get('balance'))
        account_number = request.form.get('account_number')
        logo_url = request.form.get('logo_url')

        db = current_app.get_db_connection()
        cursor = db.cursor()
        cursor.execute('INSERT INTO accounts (user_id, account_type, balance, account_number, logo_url) VALUES (%s, %s, %s, %s, %s)',
                       (current_user.id, account_type, balance, account_number, logo_url))
        db.commit()
        cursor.close()
        db.close()

        flash('Tài khoản đã được thêm thành công!', 'success')
        return redirect(url_for('views.home'))

    return render_template('add_account.html', username=current_user.username)

# Route để thêm mục tiêu
@views.route('/add-goal', methods=['GET', 'POST'])
@login_required
def add_goal():
    if request.method == 'POST':
        budget = float(request.form.get('budget'))

        db = current_app.get_db_connection()
        cursor = db.cursor()
        cursor.execute('INSERT INTO goals (user_id, budget) VALUES (%s, %s)', (current_user.id, budget))
        db.commit()
        cursor.close()
        db.close()

        flash('Mục tiêu đã được thêm thành công!', 'success')
        return redirect(url_for('views.home'))

    return render_template('add_goal.html', username=current_user.username)

# Route để thêm hóa đơn
@views.route('/add-bill', methods=['GET', 'POST'])
@login_required
def add_bill():
    if request.method == 'POST':
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        amount = float(request.form.get('amount'))

        db = current_app.get_db_connection()
        cursor = db.cursor()
        cursor.execute('INSERT INTO bills (user_id, description, due_date, amount) VALUES (%s, %s, %s, %s)',
                       (current_user.id, description, due_date, amount))
        db.commit()
        cursor.close()
        db.close()

        flash('Hóa đơn đã được thêm thành công!', 'success')
        return redirect(url_for('views.home'))

    return render_template('add_bill.html', username=current_user.username)

# Route để thêm giao dịch
@views.route('/add-transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    categories = get_all_categories(current_app, current_user.id)

    if request.method == 'POST':
        category_id = int(request.form.get('category_id'))
        amount = float(request.form.get('amount'))
        transaction_type = request.form.get('transaction_type')
        description = request.form.get('description')
        transaction_date = request.form.get('transaction_date')

        db = current_app.get_db_connection()
        cursor = db.cursor()
        cursor.execute('INSERT INTO transactions (user_id, category_id, amount, transaction_type, description, transaction_date) VALUES (%s, %s, %s, %s, %s, %s)',
                       (current_user.id, category_id, amount, transaction_type, description, transaction_date))
        db.commit()
        cursor.close()
        db.close()

        flash('Giao dịch đã được thêm thành công!', 'success')
        return redirect(url_for('views.home'))

    return render_template('add_transaction.html', username=current_user.username, categories=categories)

# Route để thêm danh mục
@views.route('/add-category', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        category_name = request.form.get('category_name')

        db = current_app.get_db_connection()
        cursor = db.cursor()
        cursor.execute('INSERT INTO categories (category_name, user_id) VALUES (%s, %s)', (category_name, current_user.id))
        db.commit()
        cursor.close()
        db.close()

        flash('Danh mục đã được thêm thành công!', 'success')
        return redirect(url_for('views.home'))

    return render_template('add_category.html', username=current_user.username)

@views.route('/balance')
@login_required
def balance():
    return render_template('balance.html')

@views.route('/list-transactions')
@login_required
def list_transactions():
    return render_template('list_transactions.html')

@views.route('/list-categories')
@login_required
def list_categories():
    return render_template('list_categories.html')
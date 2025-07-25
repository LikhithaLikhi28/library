from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Initialize the database
def init_db():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        # Books Table
        c.execute('''CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            quantity INTEGER
        )''')
        # Members Table
        c.execute('''CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT
        )''')
        # Transactions Table
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            book_id INTEGER,
            issue_date TEXT,
            return_date TEXT,
            returned INTEGER DEFAULT 0
        )''')
        conn.commit()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# ---------------------- BOOKS ----------------------

@app.route('/books')
def books():
    with sqlite3.connect('database.db') as conn:
        books = conn.execute("SELECT * FROM books").fetchall()
    return render_template('books.html', books=books)

@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    quantity = request.form['quantity']
    with sqlite3.connect('database.db') as conn:
        conn.execute("INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)", (title, author, quantity))
    return redirect(url_for('books'))

# ---------------------- MEMBERS ----------------------

@app.route('/members')
def members():
    with sqlite3.connect('database.db') as conn:
        members = conn.execute("SELECT * FROM members").fetchall()
    return render_template('members.html', members=members)

@app.route('/add_member', methods=['POST'])
def add_member():
    name = request.form['name']
    email = request.form['email']
    with sqlite3.connect('database.db') as conn:
        conn.execute("INSERT INTO members (name, email) VALUES (?, ?)", (name, email))
    return redirect(url_for('members'))

# ---------------------- ISSUE / RETURN ----------------------

@app.route('/issue_return')
def issue_return():
    with sqlite3.connect('database.db') as conn:
        transactions = conn.execute("SELECT * FROM transactions ORDER BY id DESC").fetchall()
    return render_template('issue_return.html', transactions=transactions)

@app.route('/issue_book', methods=['POST'])
def issue_book():
    member_id = request.form['member_id']
    book_id = request.form['book_id']
    issue_date = request.form['issue_date']

    with sqlite3.connect('database.db') as conn:
        conn.execute("INSERT INTO transactions (member_id, book_id, issue_date) VALUES (?, ?, ?)", (member_id, book_id, issue_date))
        conn.execute("UPDATE books SET quantity = quantity - 1 WHERE id = ?", (book_id,))
    return redirect(url_for('issue_return'))

@app.route('/return_book', methods=['POST'])
def return_book():
    transaction_id = request.form['transaction_id']
    return_date = request.form['return_date']

    with sqlite3.connect('database.db') as conn:
        book_id = conn.execute("SELECT book_id FROM transactions WHERE id = ?", (transaction_id,)).fetchone()
        if book_id:
            conn.execute("UPDATE transactions SET return_date = ?, returned = 1 WHERE id = ?", (return_date, transaction_id))
            conn.execute("UPDATE books SET quantity = quantity + 1 WHERE id = ?", (book_id[0],))
    return redirect(url_for('issue_return'))

# ---------------------- REPORTS ----------------------

@app.route('/reports')
def reports():
    filter_type = request.args.get('filter', 'daily')
    today = datetime.today()

    if filter_type == 'daily':
        start_date = today.strftime('%Y-%m-%d')
    elif filter_type == 'weekly':
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    elif filter_type == 'monthly':
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    else:
        start_date = '1970-01-01'  # fallback

    with sqlite3.connect('database.db') as conn:
        reports = conn.execute("SELECT * FROM transactions WHERE issue_date >= ? ORDER BY id DESC", (start_date,)).fetchall()

    return render_template('reports.html', reports=reports)

# ---------------------- MAIN ----------------------

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'
DB_NAME = 'database.db'

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/coffees')
def coffees():
    return render_template('coffees.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        with connect_db() as conn:
            conn.execute('INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)', (name, email, message))
        flash('Message submitted successfully!')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with connect_db() as conn:
            admin = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
            if admin and check_password_hash(admin['password'], password):
                session['username'] = username
                return redirect(url_for('dashboard'))
            error = 'Invalid login credentials'
    return render_template('admin_login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    with connect_db() as conn:
        contacts = conn.execute('SELECT * FROM contacts ORDER BY id DESC').fetchall()
    return render_template('dashboard.html', contacts=contacts)

@app.route('/logout')
def admin_logout():
    session.pop('username', None)
    return redirect(url_for('admin_login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = generate_password_hash(password)
        try:
            with connect_db() as conn:
                conn.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (username, hashed))
                conn.commit()
                flash("Admin created successfully! You can now log in.")
                return redirect(url_for('admin_login'))
        except sqlite3.IntegrityError:
            error = "Username already exists."
    return render_template('register.html', error=error)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, session, flash, jsonify
import pyodbc

app = Flask(__name__)
app.secret_key = 'supersecret'  # Required for session handling

# SQL Server connection
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"  # ← update this
    "DATABASE=DwarakaBhojanam;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()

# Context processor to pass session data to templates
@app.context_processor
def inject_user():
    return dict(logged_user=session.get('user'))

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Menu page
@app.route('/menu')
def menu():
    cursor.execute("SELECT * FROM MenuItems")
    items = cursor.fetchall()
    return render_template('menu.html', items=items)

# Cart page
@app.route('/cart')
def cart():
    return render_template('cart.html')

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Login page and logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM Users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        if user:
            session['user'] = user[1]  # user's name
            flash("Login successful!", "success")
            return redirect('/')
        else:
            flash("Invalid credentials", "danger")
            return redirect('/login')
    return render_template('login_signup.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully", "info")
    return redirect('/')

# Signup logic
@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    try:
        cursor.execute("INSERT INTO Users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        flash("Signup successful! Please log in.", "success")
    except:
        flash("Email already exists or error occurred.", "danger")
    return redirect('/login')

# API to fetch menu items
@app.route('/api/menu')
def menu_api():
    cursor.execute("SELECT * FROM MenuItems")
    items = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    return jsonify([dict(zip(columns, row)) for row in items])

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, session, flash, jsonify, url_for
import pyodbc
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecret'

# SQL Server connection
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=DwarakaBhojanam;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

@app.context_processor
def inject_user():
    return dict(logged_user=session.get('user'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu')
def menu():
    cursor.execute("SELECT * FROM MenuItems")
    items = cursor.fetchall()
    return render_template('menu.html', items=items)

@app.route('/cart')
def cart():
    if 'user' not in session:
        flash("Please log in to view your cart.", "warning")
        return redirect('/login')
    email = session.get('email')
    cursor.execute("""
        SELECT c.id, m.name, m.price, c.quantity
        FROM Cart c
        JOIN MenuItems m ON c.item_id = m.id
        WHERE c.user_email = ?
    """, email)
    cart_items = cursor.fetchall()
    total = sum(item[2] * item[3] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        flash("Please log in to add items to your cart.", "warning")
        return redirect('/login')
    email = session.get('email')
    item_id = request.form['item_id']
    cursor.execute("SELECT * FROM Cart WHERE user_email = ? AND item_id = ?", (email, item_id))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("UPDATE Cart SET quantity = quantity + 1 WHERE id = ?", existing[0])
    else:
        cursor.execute("INSERT INTO Cart (user_email, item_id, quantity) VALUES (?, ?, 1)", (email, item_id))
    conn.commit()
    flash("Item added to cart!", "success")
    return redirect('/menu')

@app.route('/remove_from_cart/<int:cart_id>')
def remove_from_cart(cart_id):
    cursor.execute("DELETE FROM Cart WHERE id = ?", cart_id)
    conn.commit()
    flash("Item removed from cart.", "info")
    return redirect('/cart')

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user' not in session:
        flash("Please log in to place an order.", "warning")
        return redirect('/login')
    email = session.get('email')
    cursor.execute("SELECT item_id, quantity FROM Cart WHERE user_email = ?", email)
    items = cursor.fetchall()
    if not items:
        flash("Your cart is empty.", "info")
        return redirect('/menu')
    total = 0
    for item_id, qty in items:
        cursor.execute("SELECT price FROM MenuItems WHERE id = ?", item_id)
        price = cursor.fetchone()[0]
        total += price * qty
    cursor.execute("INSERT INTO Orders (user_email, total) VALUES (?, ?)", (email, total))
    conn.commit()
    order_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
    for item_id, qty in items:
        cursor.execute("INSERT INTO OrderItems (order_id, item_id, quantity) VALUES (?, ?, ?)", (order_id, item_id, qty))
    cursor.execute("DELETE FROM Cart WHERE user_email = ?", email)
    conn.commit()
    return redirect('/order_success')

@app.route('/order_success')
def order_success():
    return render_template('order_success.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM Users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        if user:
            session['user'] = user[1]
            session['email'] = user[2]
            flash("Login successful!", "success")
            return redirect('/')
        else:
            flash("Invalid credentials", "danger")
            return redirect('/login')
    return render_template('login_signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    try:
        cursor.execute("INSERT INTO Users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        flash("Signup successful! Please log in.", "success")
    except:
        flash("Email already exists or error occurred.", "danger")
    return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
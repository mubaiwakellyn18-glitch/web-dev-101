import sqlite3
from flask import Flask , request, url_for, render_template, redirect, session
app = Flask(__name__)
connection = sqlite3.connect('ExpenseTracker.db', check_same_thread=False)
connection.row_factory=sqlite3.Row
app.secret_key= "in-the-hurting"
cursor= connection.cursor()
from werkzeug.security import generate_password_hash, check_password_hash
cursor.execute("""
  CREATE TABLE IF NOT EXISTS expenses(
  id  INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  description TEXT NOT NULL,
  amount REAL NOT NULL,
  category TEXT NOT NULL,
  expense_date TEXT NOT NULL
  )
""")
cursor.execute("""
  CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  password_hash TEXT NOT NULL,
  username TEXT UNIQUE NOT NULL
)
""") 
connection.commit()
@app.route("/", methods=["GET","POST"])
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template('home.html')
@app.route("/add_expense", methods=["GET","POST"])
def add_expense():
    if request.method=='POST':
        cursor=connection.cursor()
        user_id = session["user_id"]
        description= request.form.get('description')
        amount = float(request.form.get('amount'))
        category= request.form.get('category')
        expense_date= request.form.get('expense_date')
        cursor.execute("""
        INSERT INTO  expenses(description,amount,category,expense_date,user_id) VALUES(?,?,?,?,?)""",(description,amount,category,expense_date,user_id))
        connection.commit()
        return redirect(url_for('add_expense'))
        return "Expense added successfully!"
    return render_template("add_expense.html")

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id=?",(id,))
    exps= cursor.fetchone()
    if request.method=='POST':
        cursor=connection.cursor()
        description= request.form.get('description')
        amount = float(request.form.get('amount'))
        category= request.form.get('category')
        expense_date= request.form.get('expense_date')
        cursor.execute("UPDATE expenses SET description=?, amount=? ,category=? ,expense_date=? WHERE id=?", (description,amount,category,expense_date,id))
        connection.commit()
        return redirect(url_for('display'))
    return render_template("edit.html", exp=exps)


@app.route('/delete/<int:id>')
def delete(id):
    cursor= connection.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ?',(id,))
    connection.commit()
    return redirect(url_for('display'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username= request.form.get("username")
        password= request.form.get("password")
        hashed_password= generate_password_hash(password)
        cursor=connection.cursor()
        try:
            cursor.execute(" INSERT INTO users (username,password_hash)  VALUES(?,?)", (username, hashed_password))
            connection.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return "Username already exists!"
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username= request.form.get("username")
        password= request.form.get("password")
        cursor = connection.cursor()
        cursor.execute(" SELECT * FROM users WHERE username= ? ",(username,))
        user= cursor.fetchone()
        if user and check_password_hash( user["password_hash"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("home"))
        else:
            return "invalid usename or password"
    return render_template("login.html")
                    
@app.route("/display")
def display():
    user_id= session["user_id"]
    cursor=connection.cursor()
    search = request.args.get('search','')
    sort= request.args.get('sort','sort')
    if sort == "desc":
        cursor.execute("SELECT * FROM expenses WHERE user_id=? AND  (description like ? OR category like ? )  ORDER BY expense_date DESC",(user_id,f"%{search}%",f"%{search}%"))
    else:
        cursor.execute("SELECT * FROM expenses WHERE user_id = ? AND (description like ? OR category like ?) ORDER BY expense_date ASC",(user_id,f"%{search}%",f"%{search}%"))
    expense = cursor.fetchall()
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (session["user_id"],))
    total= cursor.fetchone()[0]
    ["total"] or 0
    cursor.execute("SELECT category, SUM(amount) AS total . expenses WHERE user_id=? GROUP BY category ",(session["user_id"],))                
    category_totals=cursor.fetchall()
    return render_template("display.html", expenses=expense,search=search,total=total,category_totals=category_totals)
if __name__== "__main__":
    app.run(debug=True)

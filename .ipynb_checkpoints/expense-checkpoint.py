import sqlite3
from flask import Flask , request, url_for, render_template, redirect, session
app = Flask(__name__)
connection = sqlite3.connect('ExpenseTracker.db', check_same_thread=False)
connection.row_factory=sqlite3.Row
cursor= connection.cursor()
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
connection.commit()
@app.route("/", methods=["GET","POST"])
def home():
    return render_template('home.html')
@app.route("/add_expense", methods=["GET","POST"])
def add_expense():
    if request.method=='POST':
        cursor=connection.cursor()
        description= request.form.get('description')
        amount = float(request.form.get('amount'))
        category= request.form.get('category')
        expense_date= request.form.get('expense_date')
        cursor.execute("""
        INSERT INTO  expenses(description,amount,category,expense_date) VALUES(?,?,?,?)""",(description,amount,category,expense_date))
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
        return redirect(url_for('display'))
    return render_template("edit.html", exp=exps)
@app.route('/delete/<int:id>')
def delete(id):
    cursor= connection.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ?',(id,))
    return redirect(url_for('display'))

@app.route("/display")
def display():
    cursor=connection.cursor()
    search = request.args.get('search','')
    sort= request.args.get('sort','sort')
    #cursor.execute(" SELECT * FROM expenses WHERE description LIKE?",('%' + search + '%',))
    if sort == "desc":
        cursor.execute("SELECT * FROM expenses WHERE description like ? OR category like ?  ORDER BY expense_date DESC",(f"%{search}%",f"%{search}%"))
    else:
        cursor.execute("SELECT * FROM expenses WHERE description like ? OR category like ? ORDER BY expense_date ASC",(f"%{search}%",f"%{search}%"))
    expense = cursor.fetchall()
    cursor.execute('SELECT SUM(amount) FROM expenses')
    total= cursor.fetchone() [0]
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    category_totals=cursor.fetchall()
    return render_template("display.html", expenses=expense,search=search,total=total,category_totals=category_totals)
if __name__== "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import select, text

# APP INSTANCE
app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'

# DATABASE--------------------------------------------------------------------------------------------------------------
# Configuring the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# USER DATABSE
# SQLAlchemy database instance
db = SQLAlchemy(app)

# Ensure the app is aware of the database commands
app.app_context().push()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username_email = db.Column(db.String(20), unique=True, nullable=False) 
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(60), nullable=False) 
    debts = db.relationship('DebtItem', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username_email}', '{self.first_name}', '{self.last_name}')"

# Define the DebtItem model
class DebtItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(50), nullable=False)
    payer = db.Column(db.String(50), nullable=False)
    debtor_1 = db.Column(db.String(50), nullable=False)
    debtor_2 = db.Column(db.String(50), nullable=True)
    debtor_3 = db.Column(db.String(50), nullable=True)
    monetary_value = db.Column(db.Float, nullable=False)
    group_id = db.Column(db.String(50), nullable=False)
    time_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 

    def __repr__(self):
        return f"DebtItem('{self.item_name}', '{self.monetary_value}')"

if __name__ == "__main__":
    db.create_all() 

# Simulated data store - DEPRECATED
# users = {'user@example.com': {'password': 'password123', 'name': 'John Doe', 'id': 1}}
# debts = [
#    {'id': 1, 'item_name': 'Lunch', 'amount': 10.5, 'creditor_id': 1, 'debtor_id': 2, 'timestamp': '2021-09-01'},
#    {'id': 2, 'item_name': 'Coffee', 'amount': 4.75, 'creditor_id': 2, 'debtor_id': 1, 'timestamp': '2021-09-02'},
#]

# PAGES ----------------------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user_id' in session:
        if request.method == 'POST':
            item_name = request.form['item_name']
            amount = float(request.form['amount'])
            # In a real application, you would update the debts data structure here
            flash('This is a simulated action. Debt was not actually added.', 'info')
        return render_template('index.html', debts=debts, user_name=session.get('user_name'))
    else:
        return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email]['password'] == password:
            session['user_id'] = users[email]['id']
            session['user_name'] = users[email]['name']
            flash('You were successfully logged in', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your credentials', 'danger')
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    flash('You were successfully logged out', 'success')
    return redirect(url_for('login'))


@app.route('/settle_debts')
def settle_debts_view():
    if 'user_id' in session:
        # This is a placeholder for the settlement algorithm
        transactions = []  # Simulate transactions
        return render_template('result.html', transactions=transactions)
    else:
        return render_template('index.html')

@app.route("/user_profile")
def user_profile(title='Profile page'):
    return render_template('user_profile.html',
                           title=title)

@app.route("/debt_view")
def debt_view(title='See all your debts, past and present!'):
        return render_template('debt_view.html',
                               title=title)


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import select, text

# APP INSTANCE
app = Flask(__name__)


# SETTLEMENT ALGO ------------------------------------------------------------------------------------------------------
def settle_debts(debts):
    transactions = []

    for debtor, creditor_amounts in debts.items():
        for creditor, amount in creditor_amounts.items():
            transactions.append((debtor, creditor, amount))

    return transactions

# DATABASE--------------------------------------------------------------------------------------------------------------
# Configuring the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# USER DATABSE
# SQLAlchemy database instance
db_user = SQLAlchemy(app)

# Ensure the app is aware of the database commands
app.app_context().push()

# Defining a model
class UserInput(db_user.Model):
    user_id = db_user.Column(db_user.Integer, primary_key=True)
    username_email = db_user.Column(db_user.String(20), nullable=False)
    first_name = db_user.Column(db_user.String(20), nullable=False)
    last_name = db_user.Column(db_user.String(20), nullable=False)
    password = db_user.Column(db_user.String(20), nullable=False)
    debts = db_user.relationship('DebtItem', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username_email}', '{self.first_name}', '{self.last_name}')"


# DEBT DATABASE
db_debt = SQLAlchemy(app)

app.app_context().push()
# Defining a model
class DebtItem(db_debt.Model):
    debt_id = db_debt.Column(db_debt.Integer, primary_key=True) # Auto assigned
    item_name = db_debt.Column(db_debt.String(50), nullable=False)
    payer = db_debt.Column(db_debt.String(50), nullable=False)
    debtor_1 = db_debt.Column(db_debt.String(50), nullable=False)
    debtor_2 = db_debt.Column(db_debt.String(50), nullable=True)
    debtor_3 = db_debt.Column(db_debt.String(50), nullable=True)
    monetary_value = db_debt.Column(db_debt.Float, nullable=False) # Changed to floating point
    group_id = db_debt.Column(db_debt.String(50), nullable=False)
    time_date = db_debt.Column(db_debt.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"DebtItem('{self.item_name}', '{self.monetary_value}')"

# PAGES ----------------------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
@app.route("/home")
def debt_calculator():
    if request.method == 'POST':
        debts = {}
        # Assuming form data will have specific naming convention: debtorX, creditorX, amountX
        form_data = list(request.form.items())
        num_entries = len(form_data) // 3

        for i in range(num_entries):
            debtor = request.form.get(f'debtor{i}')
            creditor = request.form.get(f'creditor{i}')
            amount = float(request.form.get(f'amount{i}', 0))

            if debtor and creditor and amount:
                if debtor not in debts:
                    debts[debtor] = {}
                debts[debtor][creditor] = debts[debtor].get(creditor, 0) + amount

        transactions = settle_debts(debts)
        return render_template('result.html', transactions=transactions)
    else:
        return render_template('index.html')

@app.route("/login")
def login(title='Login Screen'):
    return render_template('login.html',
                           title=title)

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

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import select, text
from werkzeug.security import check_password_hash, generate_password_hash


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
    email = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.email}', '{self.first_name}', '{self.last_name}')"

class DebtItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(50), nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    debtor_1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    debtor_2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    debtor_3_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    monetary_value = db.Column(db.Float, nullable=False)
    group_id = db.Column(db.String(50), nullable=False)
    time_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # define relationships
    payer = db.relationship('User', foreign_keys=[payer_id], backref=db.backref('paid_debts', lazy=True))
    debtor_1 = db.relationship('User', foreign_keys=[debtor_1_id], backref=db.backref('debts_1', lazy=True))
    debtor_2 = db.relationship('User', foreign_keys=[debtor_2_id], backref=db.backref('debts_2', lazy=True))
    debtor_3 = db.relationship('User', foreign_keys=[debtor_3_id], backref=db.backref('debts_3', lazy=True))

    def __repr__(self):
        return f"DebtItem('{self.item_name}', '{self.monetary_value}')"

# PAGES ----------------------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'user_id' in session:
        if request.method == 'POST':
            item_name = request.form['item_name']
            amount = float(request.form['amount'])
            # update the debts data structure here
            flash('This is a simulated action. Debt was not actually added.', 'info')
        return render_template('index.html', user_name=session.get('user_name'))
    else:
        return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'warning')
            return redirect(url_for('register'))
        
        password_hash = generate_password_hash(password)
        
        new_user = User(email=email, password_hash=password_hash, first_name=first_name, last_name=last_name)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id  
            flash('You have successfully logged in!', 'success')
            return redirect(url_for('home'))  
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.clear()
    flash('You were successfully logged out', 'success')
    return redirect(url_for('login'))


@app.route("/user_profile")
def user_profile(title='Profile page'):
    return render_template('user_profile.html',
                           title=title)


@app.route('/debt_view')
def show_debts():
    return render_template('debt_view.html', debts=debts, message=message)


@app.route('/settle_debts')
def settle_debts_view():
    if 'user_id' in session:
        # This is a placeholder for the settlement algorithm
        transactions = []  # Simulate transactions
        return render_template('result.html', transactions=transactions)
    else:
        return render_template('index.html')


def calculate_debts(user_id):
    all_debts = DebtItem.query.all()
    owe_amounts = {}  # dic to hold how much each user owes to othes

    for debt in all_debts:
        debtors = [debt.debtor_1, debt.debtor_2, debt.debtor_3]  
        split_value = debt.monetary_value / len([debtor for debtor in debtors if debtor])  # assumes equal split - need to make this variable later

        for debtor in debtors:
            if debtor:  # check  debtor exists (as debtor_2 and debtor_3 might not exist) - later need to make these linked to user ids in the database
                if debtor not in owe_amounts:
                    owe_amounts[debtor] = {}
                # later need to make debtors linked to unique ids
                if debt.payer not in owe_amounts[debtor]:
                    owe_amounts[debtor][debt.payer] = 0
                owe_amounts[debtor][debt.payer] += split_value

    # Return the total amount the current user owes to each other user
    return owe_amounts.get(user_id, {})


if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
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
    debts = db.relationship('DebtItem', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.email}', '{self.first_name}', '{self.last_name}')"

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

@app.route('/settle_debts')
def settle_debts_view():
    if 'user_id' in session:
        # This is a placeholder for the settlement algorithm
        transactions = []  # Simulate transactions
        return render_template('result.html', transactions=transactions)
    else:
        return render_template('index.html')


@app.route('/debt_view')
def show_debts():
    try:
        # This is where you would normally fetch your debts, e.g., from a database
        debts = fetch_debts_from_database()
    except SomeException:
        # If fetching debts fails for some reason, set debts to an empty list
        debts = []

    # Check if the debts list is empty and display a message accordingly
    if not debts:
        message = "You have no debt"
    else:
        message = None  # or any logic you want when there are debts

    return render_template('debt_view.html', debts=debts, message=message)


if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True)

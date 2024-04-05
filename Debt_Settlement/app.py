from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.models import db, User, DebtItem
from config import Config
from werkzeug.security import check_password_hash, generate_password_hash



# APP INSTANCE
app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

@app.before_request
def create_tables():
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

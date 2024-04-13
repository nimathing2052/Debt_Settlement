from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify
from datetime import datetime
from sqlalchemy import func
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
    debtor_1 = db.Column(db.String(50), nullable=True)
    debtor_2 = db.Column(db.String(50), nullable=True)
    debtor_3 = db.Column(db.String(50), nullable=True)
    monetary_value = db.Column(db.Float, nullable=False)
    group_id = db.Column(db.String(50), nullable=True)
    time_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"DebtItem('{self.item_name}', '{self.monetary_value}')"

def calculate_total_debt():
    # Get the ID of the currently logged-in user from the session
    user_id = session.get('user_id')

    if user_id is None:
        return jsonify({'error': 'User not logged in'})

    # Query the database to retrieve all debt items associated with the user
    user_debts = DebtItem.query.filter_by(user_id=user_id).all()

    # Initialize total debt amount
    total_debt = 0.0

    # Sum up the monetary values of these debt items
    for debt in user_debts:
        total_debt += debt.monetary_value

    return total_debt

 # Import User model and db instance from your module


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



@app.route('/update_monetary_value', methods=['GET', 'POST'])
def update_monetary_value():
    if request.method == 'POST':
        # Print the form data
        print("Form Data:", request.form)

        item_id = request.form.get('user_id')
        amount = float(request.form.get('amount'))

        debt_item = DebtItem.query.get_or_404(item_id)
        debt_item.monetary_value += amount
        db.session.commit()
        print("successful")
        return redirect(url_for('home'))

    # If it's a GET request, render the form
    items = DebtItem.query.all()
    return render_template('update_money.html', items=items)


# Route to handle input of monetary value and item name
@app.route('/input_monetary_value', methods=['GET', 'POST'])
def input_monetary_value():
    if request.method == 'POST':
        item_name = request.form['item_name']
        monetary_value = request.form['monetary_value']
        user_id = session.get('user_id')  # Retrieve the logged-in user's ID from the session

        # Retrieve the logged-in user
        user = User.query.get(user_id)
        if user:
            # Set the payer to the logged-in user's email
            payer = user.email

            # Create the DebtItem object with all required fields
            debt_item = DebtItem(item_name=item_name, payer=payer, monetary_value=monetary_value, user=user)
            db.session.add(debt_item)
            db.session.commit()
            return 'Monetary value updated successfully'
        else:
            return 'User not found'

    return render_template('input_monetary_value.html')
       

# Route to retrieve and display monetary values for the logged-in user
@app.route('/show_monetary_values')
def show_monetary_values():
    # Retrieve the user's ID from the session
    user_id = session.get('user_id')
    if user_id:
        # Query the DebtItem table to retrieve monetary values associated with the user ID
        monetary_values = DebtItem.query.filter_by(user_id=user_id).with_entities(DebtItem.monetary_value).all()

        # Calculate the total monetary value
        total_monetary_value = sum(value[0] for value in monetary_values)

        return render_template('show_balance.html', monetary_values=monetary_values, total_monetary_value=total_monetary_value)
    else:
        return 'User not logged in'

# Route to display the list of users and send money
@app.route('/send_money', methods=['GET', 'POST'])
def send_money():
    # Retrieve logged-in user's monetary value
    user_id = session.get('user_id')
    sender = DebtItem.query.get(user_id)
    monetary_values = DebtItem.query.filter_by(user_id=user_id).with_entities(DebtItem.monetary_value).all()
    #sender_monetary_value = db.session.query(func.sum(DebtItem.monetary_value)).filter_by(id=user_id).scalar() or 0.0
    sender_monetary_value = sum(value[0] for value in monetary_values)


    if request.method == 'POST':
        # Retrieve recipient's information
        recipient_id = int(request.form['recipient'])
        recipient = DebtItem.query.get(recipient_id)

        # Retrieve amount to send
        amount = float(request.form['amount'])

        # Check if sender has sufficient funds
        if sender_monetary_value < amount:
            return 'Insufficient funds'

        user1 = User.query.get(user_id)
        if user1:
            # Set the payer to the logged-in user's email
            #payer = user.email
            payer = user1.email

            # Create the DebtItem object with all required fields
            debt_item = DebtItem(item_name="Payment", payer=payer, monetary_value= -amount, user=user1)
            db.session.add(debt_item)
            db.session.commit()
        # Update sender's monetary value
        sender.monetary_value -= amount

        user2 = User.query.get(recipient_id)
        if user2:
            # Set the payer to the logged-in user's email
            # payer = user.email
            payer = user2.email

            # Create the DebtItem object with all required fields
            debt_item = DebtItem(item_name="Payment", payer=payer, monetary_value=amount, user=user2)
            db.session.add(debt_item)
            db.session.commit()

        # Update recipient's monetary value
        recipient.monetary_value += amount

        # Commit changes to the database
        db.session.commit()

        # Update sender's monetary value in the database after successful transfer
        #sender = User.query.get(user_id)  # Retrieve sender object again
        sender.monetary_value -= amount  # Subtract the transferred amount
        db.session.add(DebtItem(id=user_id, monetary_value= int(-amount)))
        #db.session.commit()  # Commit the update to the database

        return 'Transfer successful'

    # Get all users except the logged-in user
    users = User.query.filter(User.id != user_id).all()

    return render_template('send_money.html', users=users, sender_monetary_value=sender_monetary_value)


@app.route('/input_debts', methods=['GET', 'POST'])
def input_debts():
    if request.method == 'POST':
        # Retrieve the logged-in user's ID
        user_id = session.get('user_id')

        # Retrieve the selected debtor's ID and debt amount from the form
        debtor_id = int(request.form['debtor'])
        amount = float(request.form['amount'])

        # Retrieve the debtor's information
        debtor = User.query.get(debtor_id)

        # Save the debt under the user's debts column
        user = User.query.get(user_id)
        user.debts += amount

        # Save the debt information in the DebtItem table
        debt_item = DebtItem(item_name="Debt", monetary_value=-amount, user_id=user_id)
        debt_item.debtor_1 = debtor.first_name + " " + debtor.last_name
        db.session.add(debt_item)
        db.session.commit()

        # Retrieve all users who have the current user's name in their list of debts
        users_who_owe = User.query.filter(User.debts > 0).all()

        # Print the names of users who owe the current user along with their debt amounts
        for user_who_owes in users_who_owe:
            print(user_who_owes.first_name, user_who_owes.last_name, "owes you", user_who_owes.debts)

        # Calculate the total amount owed to the current user
        total_debts = sum(user_who_owes.debts for user_who_owes in users_who_owe)
        print("Total amount owed to you:", total_debts)

        # Redirect or render a template as needed
        # return redirect(url_for('some_route'))

    # Render the template with the list of users for selection
    users = User.query.all()
    return render_template('input_debts.html', users=users)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=9999)

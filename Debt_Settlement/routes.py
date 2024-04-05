from flask import render_template, request, redirect, url_for, session, flash
from Debt_Settlement.models.user import User
from Debt_Settlement import db  # Import the global db instance
from werkzeug.security import check_password_hash, generate_password_hash

def init_routes(app):
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

from flask import render_template, session, request, flash, redirect, url_for
from app.models import DebtItem, User, db
def init_home_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/home', methods=['GET', 'POST'])
    def home():
        if 'user_id' in session:
            if request.method == 'POST':
                item_name = request.form['item_name']
                amount = float(request.form['amount'])
                # update the debts data structure here
                flash('This is a simulated action. Debt was not actually added.', 'info')
            # Assuming 'user_name' is set in the session or somewhere else accessible
            return render_template('index.html', user_name=session.get('user_name'))
        else:
            # If the 'login' route is in the 'auth' blueprint, this is correct
            # Otherwise, adjust the 'url_for' argument to match the blueprint name and function
            return redirect(url_for('login'))  # Adjust this if login is not part of 'auth' blueprint

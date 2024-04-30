from flask import request, session, flash, redirect, url_for, render_template
from app.models import User, Transaction, db

def init_home_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/home', methods=['GET', 'POST'])
    def home():
        if 'user_id' in session:
            if request.method == 'POST':
                item_name = request.form.get('item_name')
                amount = request.form.get('amount')

                if item_name is not None and amount is not None:
                    try:
                        amount = float(amount)
                        # Implement actual logic here to add the debt
                        flash('This is a simulated action. Debt was not actually added.', 'info')
                    except ValueError:
                        flash('Invalid amount entered.', 'danger')
                else:
                    flash('Missing item name or amount.', 'warning')

            user_name = session.get('user_name', 'Guest')  # Fallback to 'Guest' if not set
            return render_template('index.html', user_name=user_name)
        else:
            return redirect(url_for('login'))

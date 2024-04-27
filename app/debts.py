from flask import Flask, request, session, flash, redirect, url_for, render_template
from app.models import Transaction, User, db, Transaction
from .debt_resolver import Solution, read_db_to_adjacency_matrix
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func
from datetime import datetime
from .forms import SendMoneyForm
def init_debt_routes(app):
    @app.route("/user_profile")
    def user_profile(title='Profile page'):
        if 'user_id' not in session:
            flash('Please log in to view your profile.', 'warning')
            return redirect(url_for('login'))
            # Here you can add more logic to handle user profile data
        return render_template('user_profile.html', title='Profile page')

    @app.route('/settle_debts')
    def settle_debts_view():
        if 'user_id' not in session:
            flash('Please log in to proceed.', 'warning')
            return redirect(url_for('login'))

        # Placeholder for settlement algorithm
        transactions = []  # Simulate transactions
        return render_template('result.html', transactions=transactions)

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            flash('Please log in to view the dashboard.', 'warning')
            return redirect(url_for('login'))

        # Aggregate the debts and credits
        debts = db.session.query(
            User.first_name, User.last_name,
            func.sum(Transaction.amount).label('total_debt')
        ).join(User, User.id == Transaction.debtor_id) \
            .group_by(User.first_name, User.last_name) \
            .all()

        credits = db.session.query(
            User.first_name, User.last_name,
            func.sum(Transaction.amount).label('total_credit')
        ).join(User, User.id == Transaction.payer_id) \
            .group_by(User.first_name, User.last_name) \
            .all()

        return render_template('dashboard.html', debts=debts, credits=credits)
    @app.route('/debt_view')
    def show_debts():
        if 'user_id' not in session:
            flash('Please log in to view debts.', 'warning')
            return redirect(url_for('login'))

        user_id = session.get('user_id')
        debts = Transaction.query.filter_by(debtor_id=user_id).all()
        message = "You have no debt" if not debts else None
        return render_template('debt_view.html', debts=debts, message=message)

    @app.route('/update_monetary_value', methods=['GET', 'POST'])
    def update_monetary_value():
        if request.method == 'POST':
            # Print the form data
            print("Form Data:", request.form)

            item_id = request.form.get('user_id')
            amount = float(request.form.get('amount'))

            debt_item = Transaction.query.get_or_404(item_id)
            debt_item.monetary_value += amount
            db.session.commit()
            print("successful")
            return redirect(url_for('home'))

        # If it's a GET request, render the form
        items = Transaction.query.all()
        return render_template('update_money.html', items=items)

    # Route to handle input of monetary value and item name
    @app.route('/input_monetary_value', methods=['GET', 'POST'])
    def input_monetary_value():
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))

        if request.method == 'POST':
            try:
                user_id = session['user_id']
                item_name = request.form.get('item_name')
                amount = float(request.form.get('monetary_value'))

                if not item_name or amount <= 0:
                    flash('Invalid input: Item name must be provided and amount must be greater than zero.', 'warning')
                    return redirect(url_for('input_monetary_value'))

                new_transaction = Transaction(
                    item_name=item_name,
                    amount=amount,  # assuming a positive amount indicates a credit
                    payer_id=user_id,  # assuming the current user is the payer
                    debtor_id=user_id  # if the user is paying themselves, like adding a credit
                )

                db.session.add(new_transaction)
                db.session.commit()
                flash('Monetary value added successfully.', 'success')

            except ValueError:
                flash('Invalid amount entered.', 'danger')
            except SQLAlchemyError as e:
                db.session.rollback()
                flash('An error occurred while adding the monetary value.', 'danger')
                # In production, you might log the error here
        return render_template('input_monetary_value.html')

    # Route to retrieve and display monetary values for the logged-in user
    @app.route('/show_monetary_values')
    def show_monetary_values():
        # Check if user is logged in
        user_id = session.get('user_id')
        if not user_id:
            flash('Please log in to view monetary values.', 'warning')
            return redirect(url_for('login'))

        try:
            # Query the database for transactions where the user is the payer
            credit_transactions = Transaction.query.filter_by(payer_id=user_id).all()
            total_credit = sum(transaction.amount for transaction in credit_transactions)

            # Query the database for transactions where the user is the debtor
            debit_transactions = Transaction.query.filter_by(debtor_id=user_id).all()
            total_debit = sum(transaction.amount for transaction in debit_transactions)

            # Calculate net balance
            net_balance = total_credit - total_debit

            # Prepare data for template
            monetary_values = [
                {'description': 'Total Credit', 'value': total_credit},
                {'description': 'Total Debit', 'value': -total_debit},  # Debit shown as positive number
                {'description': 'Net Balance', 'value': net_balance}
            ]

            return render_template(
                'show_balance.html',
                monetary_values=monetary_values,
                total_monetary_value=net_balance  # Or whatever summary statistic you prefer
            )
        except Exception as e:
            # In a production app, you'd want to log this error.
            flash('An error occurred while fetching monetary values.', 'danger')
            return redirect(url_for('user_profile'))

    # Route to display the list of users and send money


    @app.route('/input_debts', methods=['GET', 'POST'])
    def input_debts():
        if request.method == 'POST':
            if 'user_id' not in session:
                flash('Please log in to input debts.', 'warning')
                return redirect(url_for('login'))

            user_id = session['user_id']
            debtor_id = int(request.form.get('debtor'))
            amount = float(request.form.get('amount'))

            payer = User.query.get_or_404(user_id)
            debtor = User.query.get_or_404(debtor_id)

            try:
                debt_item = Transaction(item_name="Debt", amount=-amount, payer_id=payer.id, debtor_id=debtor.id)
                db.session.add(debt_item)
                db.session.commit()
                flash('Debt recorded successfully.', 'success')
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(str(e), 'danger')

            return redirect(url_for('input_debts'))

        users = User.query.all()
        return render_template('input_debts.html', users=users)

    @app.route('/settle_up', methods=['GET', 'POST'])
    def settle_up():
        if request.method == 'POST':
            try:
                adjacency_matrix, persons = read_db_to_adjacency_matrix()
                solver = Solution()
                payment_instructions = solver.minCashFlow(adjacency_matrix, persons)
                return render_template('result2.html', payments=payment_instructions)
            except NotFound:
                flash('No transactions found to settle up.', 'warning')
            except Exception as e:
                flash(str(e), 'danger')

        return render_template('settle_up.html')

    @app.route('/send_money', methods=['GET', 'POST'])
    def send_money():
        user_id = session.get('user_id')
        if not user_id:
            flash('Please log in to send money.', 'warning')
            return redirect(url_for('login'))

        form = SendMoneyForm()
        form.recipient.choices = [(u.id, u.first_name + ' ' + u.last_name) for u in
                                  User.query.filter(User.id != user_id).all()]

        if form.validate_on_submit():
            recipient_id = form.recipient.data
            amount = form.amount.data

            if not has_sufficient_funds(user_id, amount):
                flash('Insufficient funds.', 'warning')
                return redirect(url_for('send_money'))

            try:
                transaction = Transaction(
                    item_name="Transfer",
                    amount=-amount,  # Negative because it's a debit from the payer
                    payer_id=user_id,
                    debtor_id=recipient_id,
                    time_date=datetime.utcnow()
                )
                db.session.add(transaction)
                db.session.commit()
                flash('Money sent successfully!', 'success')
                return redirect(url_for('user_profile'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash('Failed to send money: ' + str(e), 'danger')
                return render_template('send_money.html', form=form)

        return render_template('send_money.html', form=form)
    def has_sufficient_funds(user_id, amount):
        total_credit = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.debtor_id == user_id).scalar() or 0
        total_debit = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.payer_id == user_id).scalar() or 0
        return (total_credit + total_debit) >= amount


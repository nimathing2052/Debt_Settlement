from flask import Flask, request, session, flash, redirect, abort, url_for, render_template
from app.models import Transaction, User, db
from .debt_resolver import Solution, read_db_to_adjacency_matrix, build_adjacency_matrix_from_transactions, resolve_group_debts
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func
from datetime import datetime
from .forms import SendMoneyForm
from sqlalchemy.orm import aliased
from .models import Group, GroupTransaction
from flask_login import current_user
from .models.group import UserGroup
from sqlalchemy.orm import joinedload
from matplotlib import pyplot as plt
from .algorithm_complexity import generate_complexity_plots


def init_debt_routes(app):

    @app.route('/settle_debts')
    def settle_debts_view():
        if 'user_id' not in session:
            flash('Please log in to proceed.', 'warning')
            return redirect(url_for('login'))

        transactions = Transaction.query.filter(
            (Transaction.payer_id == current_user.id) | (Transaction.debtor_id == current_user.id)
        ).all()
        return render_template('result.html', transactions=transactions)

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            flash('Please log in to view the dashboard.', 'warning')
            return redirect(url_for('login'))

        # Subquery for total credits per user
        credit_subquery = db.session.query(
            GroupTransaction.payer_id.label('user_id'),
            func.sum(func.abs(GroupTransaction.amount)).label('total_credit')  # Using abs() to ensure positive values
        ).group_by(GroupTransaction.payer_id).subquery()

        # Subquery for total debts per user
        debt_subquery = db.session.query(
            GroupTransaction.debtor_id.label('user_id'),
            func.sum(func.abs(GroupTransaction.amount)).label('total_debt')  # Using abs() to ensure positive values
        ).group_by(GroupTransaction.debtor_id).subquery()

        # Main query to calculate net balances, total credits, and total debts
        net_balances = db.session.query(
            User.first_name, User.last_name,
            func.coalesce(credit_subquery.c.total_credit, 0).label('total_incomings'),
            func.coalesce(debt_subquery.c.total_debt, 0).label('total_outgoings'),
            (func.coalesce(credit_subquery.c.total_credit, 0) - func.coalesce(debt_subquery.c.total_debt, 0)).label(
                'net_balance')
        ).outerjoin(credit_subquery, User.id == credit_subquery.c.user_id) \
            .outerjoin(debt_subquery, User.id == debt_subquery.c.user_id) \
            .group_by(User.first_name, User.last_name) \
            .all()

        # Define aliases for User model
        Payer = aliased(User, name='payer')
        Debtor = aliased(User, name='debtor')

        # Fetch all transactions with payer and debtor details
        transactions = db.session.query(
            GroupTransaction.description,
            Payer.first_name.label('payer_first_name'),
            Payer.last_name.label('payer_last_name'),
            Debtor.first_name.label('debtor_first_name'),
            Debtor.last_name.label('debtor_last_name'),
            GroupTransaction.amount,
            GroupTransaction.created_at
        ).join(Payer, Payer.id == GroupTransaction.payer_id) \
            .join(Debtor, Debtor.id == GroupTransaction.debtor_id).all()

        return render_template('dashboard.html', net_balances=net_balances, transactions=transactions)

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

    
    @app.route('/input_debts', methods=['GET', 'POST'])
    def input_debts():
        if request.method == 'POST':
            if 'user_id' not in session:
                flash('Please log in to input debts.', 'warning')
                return redirect(url_for('login'))

            payer_id = int(request.form.get('payer'))
            debtor_id = int(request.form.get('debtor'))
            item_name = request.form.get('item_name')
            amount = float(request.form.get('amount'))

            payer = User.query.get_or_404(payer_id)
            debtor = User.query.get_or_404(debtor_id)

            try:
                debt_item = Transaction(
                    item_name=item_name,
                    amount=-amount,
                    payer_id=payer.id,
                    debtor_id=debtor.id)

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
            if 'user_id' not in session:
                flash('Please log in to Settle Up Functions', 'warning')
                return redirect(url_for('login'))
            plot_file_2d, plot_file_3d = generate_complexity_plots()

            try:
                adjacency_matrix, persons = read_db_to_adjacency_matrix()
                solver = Solution()
                payment_instructions = solver.minCashFlow(adjacency_matrix, persons)
                return render_template('result2.html', payments=payment_instructions, plot_file_2d=plot_file_2d,
                                       plot_file_3d=plot_file_3d)
            except NotFound:
                flash('No transactions found to settle up.', 'warning')
            except Exception as e:
                flash(str(e), 'danger')

        return render_template('settle_up.html')

    @app.route('/create_group', methods=['GET', 'POST'])
    def create_group():
        if request.method == 'POST':
            group_name = request.form.get('group_name')
            members_ids = request.form.getlist('members')  # Retrieves all selected user IDs from the form

            if group_name:
                existing_group = Group.query.filter_by(name=group_name).first()
                if existing_group:
                    flash('A group with this name already exists.', 'warning')
                else:
                    try:
                        group = Group(name=group_name)
                        db.session.add(group)
                        db.session.flush()

                        for member_id in members_ids:
                            user = User.query.get(int(member_id))
                            if user:
                                user_group = UserGroup(user_id=user.id, group_id=group.id)
                                db.session.add(user_group)
                            else:
                                flash(f"No user found with ID {member_id}", 'error')

                        db.session.commit()
                        flash('Group created successfully', 'success')
                        return redirect(url_for('list_groups'))
                    except SQLAlchemyError as e:
                        db.session.rollback()
                        flash(str(e), 'danger')
            else:
                flash('Please provide a group name', 'warning')

        all_users = User.query.all()
        return render_template('create_group.html', all_users=all_users)

    @app.route('/list_groups')
    def list_groups():
        page = request.args.get('page', 1, type=int)
        per_page = 10

        member_count_subquery = db.session.query(
            UserGroup.group_id.label('group_id'),
            func.count('*').label('member_count')
        ).group_by(UserGroup.group_id).subquery()

        transaction_stats_subquery = db.session.query(
            GroupTransaction.group_id.label('group_id'),
            func.count('*').label('total_transactions'),
            func.sum(GroupTransaction.amount).label('total_amount')
        ).group_by(GroupTransaction.group_id).subquery()

        try:
            groups = db.session.query(
                Group.id,
                Group.name,
                Group.created_at,
                func.coalesce(member_count_subquery.c.member_count, 0).label('member_count'),
                func.coalesce(transaction_stats_subquery.c.total_transactions, 0).label('total_transactions'),
                func.coalesce(transaction_stats_subquery.c.total_amount, 0).label('total_amount')
            ).outerjoin(member_count_subquery, Group.id == member_count_subquery.c.group_id) \
            .outerjoin(transaction_stats_subquery, Group.id == transaction_stats_subquery.c.group_id) \
            .paginate(page=page, per_page=per_page, error_out=False)
        except Exception as e:
            flash(f"Database error: {e}", 'error')
            abort(500, description="Error accessing the database")
        
        return render_template('list_groups.html', groups=groups)

    @app.route('/add_transaction_to_group', methods=['GET', 'POST'])
    def add_transaction_to_group():
        if request.method == 'POST':
            if 'user_id' not in session:
                flash('Please log in to input debts.', 'warning')
                return redirect(url_for('login'))

            group_id = request.form.get('group_id', type=int)
            payer_id = session.get('user_id')
            debtor_id = int(request.form.get('debtor_id'))  # Retrieve debtor_id from the form
            amount = request.form.get('amount', type=float)
            description = request.form.get('description', type=str)
            payer = User.query.get_or_404(payer_id)
            debtor = User.query.get_or_404(debtor_id)
            # Input validation for all fields:
            if not debtor_id or debtor_id == payer_id:
                flash('Invalid debtor specified.', 'warning')
                return redirect(url_for('add_transaction_to_group'))
            if amount <= 0:
                flash('Amount must be positive', 'warning')
                return redirect(url_for('add_transaction_to_group'))

            transaction = GroupTransaction(
                group_id=group_id,
                payer_id=payer_id,
                debtor_id=debtor_id,
                amount=amount,
                description=description
            )
            db.session.add(transaction)
            db.session.commit()
            flash('Transaction added successfully', 'success')
            return redirect(url_for('view_group', group_id=group_id))
        
        
        users = User.query.all()
        groups = Group.query.all()
        return render_template('add_transaction_to_group.html', groups=groups, users=users)

    @app.route('/group/<int:group_id>')
    def view_group(group_id):
        group = Group.query.get_or_404(group_id)
        transactions = GroupTransaction.query.filter_by(group_id=group_id) \
            .options(joinedload(
            GroupTransaction.payer)).all()  
        return render_template('view_group.html', group=group, transactions=transactions)
    
    
    @app.route('/dashboard_personal')
    def dashboard_personal():
        user_id = session.get('user_id')
        if not user_id:
            flash('Please log in', 'warning')
            return redirect(url_for('login'))

        try:
            credit_transactions = Transaction.query.filter_by(payer_id=user_id).all()
            debit_transactions = Transaction.query.filter_by(debtor_id=user_id).all()

            total_credit = sum(transaction.amount for transaction in credit_transactions)
            total_debit = sum(transaction.amount for transaction in debit_transactions)

            net_balance = total_credit - total_debit

            monetary_values = {
                'credits': credit_transactions,
                'debts': debit_transactions,
                'total_credit': total_credit,
                'total_debit': total_debit,
                'net_balance': net_balance
            }

            transactions = credit_transactions + debit_transactions
            transactions.sort(key=lambda x: x.time_date, reverse=True)
            
            user_groups = Group.query.join(UserGroup).filter(UserGroup.user_id == user_id).all()


            return render_template('dashboard_personal.html', monetary_values=monetary_values, transactions=transactions, user_groups=user_groups)

        except Exception as e:
            flash('Error retrieving your data', 'error')
            return redirect(url_for('login'))


    @app.route('/add_member_to_group', methods=['POST'])
    def add_member_to_group():
        user_id = request.form.get('user_id', type=int)
        group_id = request.form.get('group_id', type=int)
        if not user_id or not group_id:
            flash('Invalid user or group ID', 'error')
            return redirect(url_for('list_groups'))

        user_group = UserGroup(user_id=user_id, group_id=group_id)
        db.session.add(user_group)
        db.session.commit()
        flash('Member added successfully', 'success')
        return redirect(url_for('view_group.html', group_id=group_id))


    @app.route('/remove_member_from_group/<int:group_id>/<int:user_id>', methods=['POST'])
    def remove_member_from_group(group_id, user_id):
        user_group = UserGroup.query.filter_by(group_id=group_id, user_id=user_id).first()
        if user_group:
            db.session.delete(user_group)
            db.session.commit()
            flash('Member removed successfully', 'success')
        else:
            flash('Member not found', 'error')
        return redirect(url_for('view_group', group_id=group_id))


    @app.route('/settle_group_debts', methods=['GET', 'POST'])
    def settle_group_debts():
        page = request.args.get('page', 1, type=int)
        per_page = 10
        payment_instructions = []
        selected_group = None

        member_count_subquery = db.session.query(
            UserGroup.group_id.label('group_id'),
            func.count('*').label('member_count')
        ).group_by(UserGroup.group_id).subquery()

        transaction_stats_subquery = db.session.query(
            GroupTransaction.group_id.label('group_id'),
            func.count('*').label('total_transactions'),
            func.sum(GroupTransaction.amount).label('total_amount')
        ).group_by(GroupTransaction.group_id).subquery()

        groups = db.session.query(
            Group.id,
            Group.name,
            Group.created_at,
            func.coalesce(member_count_subquery.c.member_count, 0).label('member_count'),
            func.coalesce(transaction_stats_subquery.c.total_transactions, 0).label('total_transactions'),
            func.coalesce(transaction_stats_subquery.c.total_amount, 0).label('total_amount')
        ).outerjoin(member_count_subquery, Group.id == member_count_subquery.c.group_id) \
        .outerjoin(transaction_stats_subquery, Group.id == transaction_stats_subquery.c.group_id) \
        .paginate(page=page, per_page=per_page, error_out=False)

        if request.method == 'POST':
            if 'user_id' not in session:
                flash('Please log in to Settle Group Debts', 'warning')
                return redirect(url_for('login'))

            group_id = request.form.get('group_id', type=int)
            selected_group = Group.query.get_or_404(group_id)  
            payment_instructions = resolve_group_debts(group_id)

        return render_template('settle_group_debts.html', groups=groups, selected_group=selected_group, payment_instructions=payment_instructions)

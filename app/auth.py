from flask import request, render_template, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from .models import transaction, User, db

def init_auth_routes(app):
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
                session['first_name'] = user.first_name  
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


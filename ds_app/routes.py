from flask import render_template, redirect, url_for, flash, request, session
from Debt_Settlement import app, db
from Debt_Settlement.models import User, DebtItem
from Debt_Settlement.forms import LoginForm, RegistrationForm, UpdateProfileForm

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Add login logic here
        flash('Login requested for user {}'.format(form.email.data))
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Add registration logic here
        flash('Registration requested for user {}'.format(form.email.data))
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    debts = DebtItem.query.filter_by(owner=user)
    return render_template('user_profile.html', user=user, debts=debts)

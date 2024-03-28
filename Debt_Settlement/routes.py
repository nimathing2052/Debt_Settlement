from flask import render_template, flash, redirect, url_for
from flaskapp import app, db
from flaskapp.models import BlogPost
from flaskapp.forms import PostForm

from flask import Flask, render_template, request, redirect, url_for, session, flash

# what is going on here? we should set the '/' as the landing page and the home page as the user dashboard
@app.route('/')
def landing():
    if 'user_id' in session:
        # User is logged in, redirect to the dashboard
        return redirect(url_for('dashboard'))
    # User is not logged in, show the landing page
    return render_template('landing.html')


@app.route('/user_profile')
def user_profile():
    # Logic to fetch user details
    return render_template('user_profile.html', user_name='Your fetched username')


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access this page.')
        return redirect(url_for('main.login'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found.')
        return redirect(url_for('main.home'))

    form = UpdateProfileForm(obj=user)
    
    if form.validate_on_submit():
        user.name = form.user_name.data
        # Update other fields as necessary
        db.session.commit()
        flash('Your profile has been updated successfully!')
        return redirect(url_for('main.user_profile', user_id=user_id))
    

# landing page
    @app.route('/')
def landing():
    return render_template('landing.html')


# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Logic for logging in
    # If login successful, redirect to user's profile page
    return render_template('login.html')

# registering page
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Logic for registering a new user
    # If registration successful, redirect to user's profile page or login page
    return render_template('register.html')







########## nimas code
' @app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email]['password'] == password:
            session['user_id'] = users[email]['id']
            session['user_name'] = users[email]['name']
            flash('You were successfully logged in', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your credentials', 'danger')
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    flash('You were successfully logged out', 'success')
    return redirect(url_for('login'))

@app.route('/settle_debts')
def settle_debts_view():
    if 'user_id' in session:
        # This is a placeholder for the settlement algorithm
        transactions = []  # Simulate transactions
        return render_template('result.html', transactions=transactions)
    else:
        return redirect(url_for('login'))`
###########

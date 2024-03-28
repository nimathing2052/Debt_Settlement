from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Simulated data store
users = {'user@example.com': {'password': 'password123', 'name': 'John Doe', 'id': 1}}
debts = [
    {'id': 1, 'item_name': 'Lunch', 'amount': 10.5, 'creditor_id': 1, 'debtor_id': 2, 'timestamp': '2021-09-01'},
    {'id': 2, 'item_name': 'Coffee', 'amount': 4.75, 'creditor_id': 2, 'debtor_id': 1, 'timestamp': '2021-09-02'},
]

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user_id' in session:
        if request.method == 'POST':
            item_name = request.form['item_name']
            amount = float(request.form['amount'])
            # In a real application, you would update the debts data structure here
            flash('This is a simulated action. Debt was not actually added.', 'info')
        return render_template('index.html', debts=debts, user_name=session.get('user_name'))
    else:
        return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
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
        return redirect(url_for('login'))

@app.route("/user_profile")
def user_profile():
    if 'user_id' in session:
        return render_template('user_profile.html', user_name=session.get('user_name'))
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)


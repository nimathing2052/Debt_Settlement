from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def settle_debts(debts):
    transactions = []
    for debtor, creditor_amounts in debts.items():
        for creditor, amount in creditor_amounts.items():
            transactions.append((debtor, creditor, amount))
    return transactions

@app.route('/', methods=['GET', 'POST'])
def debt_calculator():
    if request.method == 'POST':
        debts = {}
        form_data = list(request.form.items())
        num_entries = len(form_data) // 3

        for i in range(num_entries):
            debtor = request.form.get(f'debtor{i}')
            creditor = request.form.get(f'creditor{i}')
            amount = float(request.form.get(f'amount{i}', 0))

            if debtor and creditor and amount:
                if debtor not in debts:
                    debts[debtor] = {}
                debts[debtor][creditor] = debts[debtor].get(creditor, 0) + amount

        transactions = settle_debts(debts)
        return render_template('result.html', transactions=transactions)
    else:
        return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            return redirect(url_for('debt_calculator'))
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)

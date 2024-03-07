from flask import Flask, render_template, request

app = Flask(__name__)


def settle_debts(debts):
    transactions = []

    for debtor, creditor_amounts in debts.items():
        for creditor, amount in creditor_amounts.items():
            transactions.append((debtor, creditor, amount))

    return transactions


@app.route('/', methods=['GET', 'POST'])
@app.route("/home")
def debt_calculator():
    if request.method == 'POST':
        debts = {}
        # Assuming form data will have specific naming convention: debtorX, creditorX, amountX
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

@app.route("/login"):
def login(
        title='Login Screen'
        return render_template('login.html',
                               title=title)
)

@app.route("/user_profile"):
def user_profile(
        title='Profile page'
        return render_template('user_profile.html',
                               title=title)
)


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request

app = Flask(__name__)

def settle_debts(debts):
    transactions = []

    for person, owes in debts.items():
        for owed_to, amount in owes.items():
            if person in debts.get(owed_to, {}) and debts[owed_to][person] >= amount:
                transactions.append((person, owed_to, amount))
                debts[owed_to][person] -= amount
            else:
                transactions.append((person, owed_to, amount))

    return transactions

@app.route('/', methods=['GET', 'POST'])
def debt_calculator():
    if request.method == 'POST':
        debts = {}  # Structure to collect debts from the form (implementation below)

        transactions = settle_debts(debts)
        return render_template('result.html', transactions=transactions)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

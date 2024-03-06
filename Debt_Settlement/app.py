from flask import Flask, render_template, request

app = Flask(__name__)


def calculate_reduced_payment(total_debt, interest_rate, settlement_percentage):
    """Calculates a reduced payment based on a settlement offer.

    Args:
        total_debt (float): The total outstanding debt amount.
        interest_rate (float): The annual interest rate (as a percentage).
        settlement_percentage (float):  The percentage of the debt the user is offering to settle (as a decimal).

    Returns:
        float: The calculated reduced payment amount.
    """

    settlement_amount = total_debt * settlement_percentage
    monthly_interest = (interest_rate / 100) / 12  # Convert to monthly
    return settlement_amount + (settlement_amount * monthly_interest)  # Simplified

# Example usage
debt = 5000.00
interest = 18.0
settlement_offer = 0.65  # 65% of the original debt

reduced_payment = calculate_reduced_payment(debt, interest, settlement_offer)
print(f"Reduced Payment Offer: ${reduced_payment:.2f}")

@app.route('/', methods=['GET', 'POST'])
def debt_calculator():
    if request.method == 'POST':
        debt = float(request.form['debt'])
        interest = float(request.form['interest'])
        settlement = float(request.form['settlement']) / 100
        result = calculate_reduced_payment(debt, interest, settlement)
        return render_template('result.html', result=result)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

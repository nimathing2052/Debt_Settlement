from Debt_Settlement import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

# Relationships (the backref allows access to debts from the User model)
    paid_debts = db.relationship('DebtItem', foreign_keys='DebtItem.payer_id', backref='payer', lazy=True)
    debts_1 = db.relationship('DebtItem', foreign_keys='DebtItem.debtor_1_id', backref='debtor_1', lazy=True)
    debts_2 = db.relationship('DebtItem', foreign_keys='DebtItem.debtor_2_id', backref='debtor_2', lazy=True)
    debts_3 = db.relationship('DebtItem', foreign_keys='DebtItem.debtor_3_id', backref='debtor_3', lazy=True)

    def __repr__(self):
        return f"User('{self.email}', '{self.first_name}', '{self.last_name}')"
from Debt_Settlement import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128))
    debts = db.relationship('DebtItem', backref='owner', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

class DebtItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<DebtItem {self.item_name}, Amount: {self.amount}>'

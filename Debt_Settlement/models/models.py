from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.email}', '{self.first_name}', '{self.last_name}')"

class DebtItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(50), nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    debtor_1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    debtor_2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    debtor_3_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    monetary_value = db.Column(db.Float, nullable=False)
    group_id = db.Column(db.String(50), nullable=False)
    time_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # define relationships
    payer = db.relationship('User', foreign_keys=[payer_id], backref=db.backref('paid_debts', lazy=True))
    debtor_1 = db.relationship('User', foreign_keys=[debtor_1_id], backref=db.backref('debts_1', lazy=True))
    debtor_2 = db.relationship('User', foreign_keys=[debtor_2_id], backref=db.backref('debts_2', lazy=True))
    debtor_3 = db.relationship('User', foreign_keys=[debtor_3_id], backref=db.backref('debts_3', lazy=True))

    def __repr__(self):
        return f"DebtItem('{self.item_name}', '{self.monetary_value}')"

import datetime

from . import db

class DebtItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(50), nullable=False)
    payer = db.Column(db.String(50), nullable=False)
    debtor_1 = db.Column(db.String(50), nullable=True)
    debtor_2 = db.Column(db.String(50), nullable=True)
    debtor_3 = db.Column(db.String(50), nullable=True)
    monetary_value = db.Column(db.Float, nullable=False)
    group_id = db.Column(db.String(50), nullable=True)
    time_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"DebtItem('{self.item_name}', '{self.monetary_value}')"

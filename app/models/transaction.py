import datetime

from . import db

# This is replaces UserItem model

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(50), nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    debtor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    time_date = db.Column(db.DateTime, default=datetime.UTC)
    
    def __repr__(self):
        return f"Transaction('{self.item_name}', '{self.monetary_value}')"

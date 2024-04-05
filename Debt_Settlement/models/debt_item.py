from datetime import datetime
from Debt_Settlement import db

class DebtItem(db.Model):
    __tablename__ = 'debt_item'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(50), nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    debtor_1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    debtor_2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    debtor_3_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    monetary_value = db.Column(db.Float, nullable=False)
    group_id = db.Column(db.String(100), nullable=False)  # Increased length for more flexibility
    time_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"DebtItem('{self.item_name}', '{self.monetary_value}')"
from . import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationships
    transactions_as_payer = db.relationship('Transaction', foreign_keys='Transaction.payer_id', backref='payer', lazy='dynamic')
    transactions_as_debtor = db.relationship('Transaction', foreign_keys='Transaction.debtor_id', backref='debtor', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
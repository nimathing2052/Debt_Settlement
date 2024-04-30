from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    groups = db.relationship('UserGroup', back_populates='user')

    # Relationships
    transactions_as_payer = db.relationship('Transaction', foreign_keys='Transaction.payer_id', backref='payer', lazy='dynamic')
    transactions_as_debtor = db.relationship('Transaction', foreign_keys='Transaction.debtor_id', backref='debtor', lazy='dynamic')

    # Required for Flask-Login
    def get_id(self):
        return str(self.id)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    debts = db.relationship('DebtItem', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.email}', '{self.first_name}', '{self.last_name}')"

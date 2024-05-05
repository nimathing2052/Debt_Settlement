from datetime import datetime
from . import db

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('UserGroup', back_populates='group', lazy='dynamic')

    # Relationship with group transactions
    transactions = db.relationship('GroupTransaction', backref='group', lazy='dynamic')

class GroupTransaction(db.Model):
    __tablename__ = 'group_transactions'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    payer = db.relationship('User', foreign_keys=[payer_id])
    debtor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserGroup(db.Model):
    __tablename__ = 'user_groups'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), primary_key=True)
    is_admin = db.Column(db.Boolean, default=False)

    user = db.relationship("User", back_populates="groups")
    group = db.relationship("Group", back_populates="users")

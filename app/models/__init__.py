from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User 
from .debt_item import DebtItem  # deprecated
from .transaction import Transaction  
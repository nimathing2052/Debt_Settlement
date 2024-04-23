from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User  # Assuming User model imports db from here
from .debt_item import DebtItem  # Assuming DebtItem model imports db from here

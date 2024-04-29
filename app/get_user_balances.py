from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from app.models import Transaction, User, db, Transaction


db = SQLAlchemy()

class UserBalances:
    @staticmethod
    def paid_subquery():
        return (
            db.session.query(
                Transaction.payer_id.label('user_id'),
                Transaction.debtor_id.label('counterpart_id'),
                func.sum(Transaction.amount).label('paid_amount')
            )
            .group_by(Transaction.payer_id, Transaction.debtor_id)
            .subquery()
        )

    @staticmethod
    def received_subquery():
        return (
            db.session.query(
                Transaction.debtor_id.label('user_id'),
                Transaction.payer_id.label('counterpart_id'),
                func.sum(Transaction.amount).label('received_amount')
            )
            .group_by(Transaction.debtor_id, Transaction.payer_id)
            .subquery()
        )

    @staticmethod
    def get_balances():
        paid = UserBalances.paid_subquery()
        received = UserBalances.received_subquery()

        balance_query = db.session.query(
            paid.c.user_id,
            paid.c.counterpart_id,
            (paid.c.paid_amount - func.coalesce(received.c.received_amount, 0)).label('net_balance')
        ).outerjoin(
            received, 
            db.and_(
                paid.c.user_id == received.c.user_id, 
                paid.c.counterpart_id == received.c.counterpart_id
            )
        ).filter(paid.c.paid_amount != received.c.received_amount) # Adjust filter as needed

        return balance_query.all()
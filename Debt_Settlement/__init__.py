from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('Debt_Settlement.config.Config')
    db.init_app(app)

    from Debt_Settlement.routes import init_routes
    init_routes(app)

    return app

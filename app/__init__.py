from flask import Flask
from .models import db
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Import route-defining functions directly from files in the 'app' directory
    from .home import init_home_routes
    from .auth import init_auth_routes
    from .debts import init_debt_routes

    # Initialize routes
    init_home_routes(app)
    init_auth_routes(app)
    init_debt_routes(app)

    return app

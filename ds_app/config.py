from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from Debt_Settlement.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from Debt_Settlement import routes

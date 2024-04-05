from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Creating your flaskapp instance
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

# Configuring the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Creating a SQLAlchemy database instance
db = SQLAlchemy(app)
app.app_context().push()

from Debt_Settlement import routes
from Debt_Settlement import models 



#### alternat version (Henry)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('yourapplication.config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from yourapplication import routes, models

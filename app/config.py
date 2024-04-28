import os
from datetime import timedelta


basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1) 

    SQLALCHEMY_TRACK_MODIFICATIONS = False

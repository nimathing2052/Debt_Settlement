import os
from datetime import timedelta


basedir = os.path.abspath(os.path.dirname(__file__))
class Config():
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite for tests
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing forms
    SERVER_NAME = 'localhost.localdomain'  # Local domain name for url_for
    APPLICATION_ROOT = '/'  # Root of the application, adjust if your app is not hosted at the root
    PREFERRED_URL_SCHEME = 'http'


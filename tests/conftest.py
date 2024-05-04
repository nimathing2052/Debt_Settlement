# tests/conftest.py
import pytest
from app import create_app, db
from app.config import TestConfig

@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test."""
    _app = create_app()
    _app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SERVER_NAME": 'localhost.localdomain'# Disable CSRF forms protection in testing.
    })
    with _app.app_context():
        db.create_all()
        yield _app
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    """Return a test client for the app."""
    return app.test_client()

@pytest.fixture(scope='module')
def init_database(app):
    """Initialize the database."""
    # You can add here some initial data if needed for tests
    yield db
    db.session.remove()

import pytest
from flask import url_for, session
from app.models.user import User, db

@pytest.fixture(scope='module')
def user(app):
    """Create a user for the tests."""
    with app.app_context():
        user = User(first_name='Test', last_name='Test', email='test@example.com', password_hash='test')
        user.set_password('test')  # Ensure this hashes the password
        db.session.add(user)
        db.session.commit()
    return user

def test_login_success(client, user):
    """Test successful login."""
    with client:
        response = client.post(url_for('login'), data={
            'first_name' : "Test",
            'last_name' : "Test",
            'email': 'test@example.com',
            'password': 'Test@123'
        }, follow_redirects=True)
        assert response.status_code == 200
def test_login_failure(client):
    """Test login failure with wrong credentials."""
    with client:
        response = client.post(url_for('login'), data={
            'email': 'wrong@example.com',
            'password': 'wrong'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'Invalid email or password' in response.get_data(as_text=True)
        assert 'user_id' not in session  # Ensure no user is in the session

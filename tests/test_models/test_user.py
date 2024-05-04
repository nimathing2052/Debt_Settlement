# tests/test_models/test_user.py
import pytest
from app.models.user import User

def test_new_user(init_database):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password fields are defined correctly
    """
    user = User(email='test@example.com', first_name='Test', last_name='User')
    user.set_password('FlaskIsAwesome')  # Assume you have a method to hash passwords
    init_database.session.add(user)
    init_database.session.commit()
    retrieved = User.query.filter_by(email='test@example.com').first()
    assert retrieved.email == 'test@example.com'
    assert retrieved.check_password('FlaskIsAwesome')  # This should also be a method in your User model
    assert not retrieved.check_password('Nope')

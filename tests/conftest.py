import os
import tempfile
import pytest
from flask import Flask
from flask_login import login_user

from my_flask_app import create_app, db
from my_flask_app.models import User

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    # Create the app with test config
    app = create_app({'TESTING': True, 
                      'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
                      'WTF_CSRF_ENABLED': False})
    
    # Create the database and the tables
    with app.app_context():
        db.create_all()
        
        # Create a test user
        test_user = User(
            name="Test User",
            email="test@example.com",
            password="sha256$abc123hash", # This should be a properly hashed password in reality
            phone=1234567890,
            gender="M"
        )
        db.session.add(test_user)
        db.session.commit()
    
    yield app
    
    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    """Authentication helper for tests."""
    class AuthActions:
        def login(self, email="test@example.com", password="test_password"):
            return client.post(
                '/login',
                data={'email': email, 'password': password}
            )
            
        def logout(self):
            return client.get('/logout')
            
    return AuthActions()

@pytest.fixture
def logged_in_client(client, app):
    """A test client that is logged in as the test user."""
    with client.session_transaction() as session:
        # Set a user ID in the session to simulate login
        with app.app_context():
            user = User.query.filter_by(email="test@example.com").first()
            # Flask-Login's login_user sets these session variables
            session['_user_id'] = str(user.id)
            session['_fresh'] = True
    
    return client 
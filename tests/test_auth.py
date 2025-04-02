import pytest
from flask import session

def test_login_success(client, auth):
    """Test successful login."""
    response = auth.login()
    assert response.status_code == 302  # Redirect after successful login
    
    # Follow the redirect
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Logout' in response.data  # Check for logout link which indicates logged in state

def test_login_with_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        '/login',
        data={'email': 'wrong@example.com', 'password': 'wrong_password'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Please check your login details and try again' in response.data

def test_logout(client, auth):
    """Test logout functionality."""
    auth.login()
    
    response = auth.logout()
    assert response.status_code == 302  # Redirect after logout
    
    # After logout, protected pages should redirect to login
    response = client.get('/profile', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location

def test_register_new_user(client, app):
    """Test registering a new user."""
    response = client.post(
        '/signup',
        data={
            'name': 'New User',
            'email': 'new@example.com',
            'password': 'new_password'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    
    # Check if the user was added to the database
    with app.app_context():
        from my_flask_app.models import User
        assert User.query.filter_by(email='new@example.com').first() is not None

def test_register_existing_email(client):
    """Test registering with an email that already exists."""
    # First register a user
    client.post(
        '/signup',
        data={
            'name': 'Existing User',
            'email': 'existing@example.com',
            'password': 'password'
        }
    )
    
    # Try to register again with the same email
    response = client.post(
        '/signup',
        data={
            'name': 'Another User',
            'email': 'existing@example.com',
            'password': 'another_password'
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert b'Email address already exists' in response.data 
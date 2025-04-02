import pytest
from my_flask_app.models import User

def test_profile_page_content(logged_in_client, app):
    """Test that the profile page shows the user's information."""
    response = logged_in_client.get('/profile')
    assert response.status_code == 200
    
    # Check for user information
    assert b'Test User' in response.data
    assert b'test@example.com' in response.data

def test_save_profile(logged_in_client, app):
    """Test updating user profile information."""
    # Update profile with new information
    response = logged_in_client.post(
        '/save_profile',
        data={
            'phone': '9876543210',
            'gender': 'Female'
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert b'Profile updated successfully' in response.data
    
    # Verify the database was updated
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user.phone == 9876543210
        assert user.gender == 'F'  # Gender should be stored as 'F' in database

def test_save_profile_invalid_phone(logged_in_client, app):
    """Test updating profile with invalid phone number."""
    # Update profile with invalid phone
    response = logged_in_client.post(
        '/save_profile',
        data={
            'phone': 'not-a-number',
            'gender': 'Male'
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    # Verify phone was not updated but gender was
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user.phone is None  # Should be None since 'not-a-number' is invalid
        assert user.gender == 'M'

def test_empty_phone_field(logged_in_client, app):
    """Test that empty phone field doesn't change the existing value."""
    # First set a phone number
    logged_in_client.post(
        '/save_profile',
        data={
            'phone': '1234567890',
            'gender': 'Male'
        }
    )
    
    # Then submit with empty phone field
    response = logged_in_client.post(
        '/save_profile',
        data={
            'phone': '',
            'gender': 'Male'
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    # Phone should remain unchanged
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user.phone == 1234567890  # Should still have the old value 
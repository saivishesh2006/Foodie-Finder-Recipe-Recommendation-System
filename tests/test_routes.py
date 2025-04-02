import pytest

def test_index_page(client):
    """Test that the landing page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Foodie Finder' in response.data

def test_login_page(client):
    """Test that the login page loads successfully."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_register_page(client):
    """Test that the registration page loads successfully."""
    response = client.get('/signup')
    assert response.status_code == 200
    assert b'Sign Up' in response.data

def test_protected_pages_redirect_when_not_logged_in(client):
    """Test that protected pages redirect to login when user is not authenticated."""
    # List of protected routes to test
    protected_routes = [
        '/home',
        '/profile',
        '/favourites',
        '/discover'
    ]
    
    for route in protected_routes:
        response = client.get(route, follow_redirects=False)
        assert response.status_code == 302  # Should redirect
        assert '/login' in response.location  # Should redirect to login

def test_protected_pages_accessible_when_logged_in(logged_in_client):
    """Test that protected pages are accessible when user is authenticated."""
    # List of protected routes to test
    protected_routes = [
        '/home',
        '/profile',
        '/discover'
    ]
    
    for route in protected_routes:
        response = logged_in_client.get(route)
        assert response.status_code == 200 
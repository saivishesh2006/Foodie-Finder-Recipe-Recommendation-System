import pytest
from my_flask_app.models import Favourite

def test_add_to_favorites(logged_in_client, app, mock_recipe_data):
    """Test adding a recipe to favorites."""
    # Add a recipe to favorites
    response = logged_in_client.get('/add_to_favourites/2', follow_redirects=True)
    assert response.status_code == 200
    
    # Verify it was added to the database
    with app.app_context():
        user_id = 1  # Test user ID from conftest.py
        favorites = Favourite.query.filter_by(user_id=user_id, recipe_id=2).all()
        assert len(favorites) == 1

def test_add_duplicate_favorite(logged_in_client, app):
    """Test adding the same favorite twice."""
    # Add a recipe to favorites
    logged_in_client.get('/add_to_favourites/1')
    
    # Try to add the same recipe again
    response = logged_in_client.get('/add_to_favourites/1', follow_redirects=True)
    assert response.status_code == 200
    assert b'Already added to Favourites' in response.data
    
    # Verify only one entry exists in the database
    with app.app_context():
        user_id = 1  # Test user ID from conftest.py
        favorites = Favourite.query.filter_by(user_id=user_id, recipe_id=1).all()
        assert len(favorites) == 1

def test_favorites_page(logged_in_client, app, mock_recipe_data):
    """Test that the favorites page displays user's favorites."""
    # First add some favorites
    logged_in_client.get('/add_to_favourites/1')
    logged_in_client.get('/add_to_favourites/3')
    
    # Then check the favorites page
    response = logged_in_client.get('/favourites')
    assert response.status_code == 200
    
    # Verify the page contains the recipes we favorited
    assert b'Pasta Carbonara' in response.data
    assert b'Vegetable Soup' in response.data

def test_empty_favorites_page(logged_in_client):
    """Test the favorites page when user has no favorites."""
    response = logged_in_client.get('/favourites')
    assert response.status_code == 200
    
    # Page should load but not contain any recipe cards
    assert b'recipe-card' not in response.data 
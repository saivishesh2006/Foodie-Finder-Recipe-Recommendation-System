import pytest
import os
import pickle
import pandas as pd
from unittest.mock import patch, MagicMock
import numpy as np
from scipy.sparse import csr_matrix

# Sample test data
@pytest.fixture
def sample_recipes():
    """Create a sample recipes DataFrame for testing."""
    return pd.DataFrame({
        'Srno': [1, 2, 3],
        'RecipeName': ['Pasta Carbonara', 'Chicken Curry', 'Vegetable Soup'],
        'Ingredients': [
            'pasta, eggs, cheese, pancetta', 
            'chicken, curry powder, onion, garlic',
            'carrots, celery, onion, vegetable broth'
        ],
        'Instructions': [
            '[Step 1, Step 2, Step 3]',
            '[Step 1, Step 2, Step 3]',
            '[Step 1, Step 2, Step 3]'
        ],
        'TotalTimeInMins': [30, 45, 20],
        'Difficulty': ['Easy', 'Medium', 'Easy'],
        'Course': ['Dinner', 'Dinner', 'Lunch'],
        'images': [
            'https://example.com/pasta.jpg',
            'https://example.com/curry.jpg',
            'https://example.com/soup.jpg'
        ]
    })

@pytest.fixture
def mock_recipe_data(monkeypatch, sample_recipes):
    """Mock the loading of recipe data."""
    # Create a mock for pickle.load to return our sample data
    mock_pickle_load = MagicMock(return_value=sample_recipes)
    monkeypatch.setattr(pickle, 'load', mock_pickle_load)
    
    # Mock the TF-IDF matrix and vectorizers
    mock_tfidf = csr_matrix((3, 10))  # 3 recipes, 10 features
    mock_vectorizer = MagicMock()
    mock_vectorizer.transform.return_value = csr_matrix((1, 5))  # 1 query, 5 features
    
    return {
        'recipes': sample_recipes,
        'tfidf': mock_tfidf,
        'vectorizer': mock_vectorizer
    }

@pytest.mark.usefixtures("mock_recipe_data")
def test_search_results_page(logged_in_client):
    """Test that the search results page loads successfully."""
    response = logged_in_client.get('/results?ingredients=chicken')
    assert response.status_code == 200
    assert b'Recipe Recommendations' in response.data

@pytest.mark.usefixtures("mock_recipe_data")
def test_empty_search_results(logged_in_client):
    """Test that searching with no ingredients redirects to home."""
    response = logged_in_client.get('/results')
    assert response.status_code == 302  # Redirect
    assert '/home' in response.location

@pytest.mark.usefixtures("mock_recipe_data")
def test_search_no_matches(logged_in_client):
    """Test that searching for non-existent ingredients shows no results."""
    with patch('my_flask_app.main.cosine_similarity') as mock_cosine:
        # Simulate all scores below threshold
        mock_cosine.return_value = np.array([[0.1, 0.1, 0.1]])
        
        response = logged_in_client.get('/results?ingredients=nonexistentingredient')
        assert response.status_code == 200
        assert b'No matches found' in response.data

@pytest.mark.usefixtures("mock_recipe_data")
def test_search_with_matches(logged_in_client):
    """Test that searching for existing ingredients shows results."""
    with patch('my_flask_app.main.cosine_similarity') as mock_cosine:
        # Simulate one score above threshold
        mock_cosine.return_value = np.array([[0.1, 0.3, 0.1]])
        
        response = logged_in_client.get('/results?ingredients=chicken')
        assert response.status_code == 200
        assert b'Recipe Recommendations' in response.data
        assert b'Chicken Curry' in response.data  # Should find this recipe 
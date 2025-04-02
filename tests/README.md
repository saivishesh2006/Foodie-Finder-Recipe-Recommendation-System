# Foodie Finder Testing Suite

This directory contains tests for the Foodie Finder recipe application.

## Setup

Install the testing dependencies:

```bash
pip install -r requirements-test.txt
```

## Running Tests

Run all tests:

```bash
pytest
```

Run with coverage report:

```bash
pytest --cov=my_flask_app
```

Run a specific test file:

```bash
pytest tests/test_routes.py
```

Run tests with detailed output:

```bash
pytest -v
```

## Test Structure

- `conftest.py`: Common fixtures and setup for all tests
- `test_routes.py`: Tests for application routes and page loading
- `test_auth.py`: Tests for user authentication (login, register)
- `test_recipe_search.py`: Tests for recipe search functionality
- `test_user_profile.py`: Tests for user profile operations
- `test_favorites.py`: Tests for favorites functionality

## Test Data

The `test_data` directory contains sample data files used by the tests, including:
- `sample_recipes.csv`: A small set of recipes for testing search functionality

## Mocking

The tests use Python's `unittest.mock` to mock external dependencies:
- Recipe data loading from pickle files
- TF-IDF matrix and vectorizers for recipe matching
- Cosine similarity calculations

## Notes for Extending Tests

When adding new tests:
1. Use the existing fixtures where possible
2. Mock external dependencies to avoid filesystem access
3. For new features, create separate test files
4. Follow the pattern of setting up test data, taking an action, and asserting the results 
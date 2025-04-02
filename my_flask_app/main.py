import os
import pickle
from flask import Blueprint, request, render_template,redirect,url_for,flash
from flask_login import login_required,current_user
from my_flask_app.utils.preprocess import preprocess_user_ingredients
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack
import re
import ast
from . import db
from .models import Favourite
import pandas as pd

main = Blueprint('main', __name__)

def safe_literal_eval(val):
    try:
        val = re.sub(r'\s+', ' ', val)  # Remove non-printable spaces
        return ast.literal_eval(val)  # Try to convert safely
    except (ValueError, SyntaxError):
        return val  # Return original text if conversion fails

# Get the directory of the current Python script
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "..", "data")

@main.route('/home', methods=['GET', 'POST'])
@login_required
def dish_finder():
    if request.method == 'POST':
        user_ingredients = request.form['ingredients']
        # Instead of processing and rendering results immediately,
        # redirect to a new results route with the ingredients as a query parameter.
        return redirect(url_for('main.results', ingredients=user_ingredients))
    return render_template('dish_finder.html')


@main.route('/results', methods=['GET'])
@login_required
def results():
    user_ingredients = request.args.get('ingredients')
    if not user_ingredients:
        # If no ingredients provided, redirect back to the dish finder page.
        return redirect(url_for('main.dish_finder'))

    print(f"Original user input: '{user_ingredients}'")
    preprocessed_user_ingredients = preprocess_user_ingredients(user_ingredients)
    print(f"Preprocessed user input: '{preprocessed_user_ingredients}'")

    # Load vectorizers and combined TF-IDF matrix
    with open(os.path.join(data_dir, "processed", "Vectorizer_names.pkl"), 'rb') as file:
        vectorizer_name = pickle.load(file)
    with open(os.path.join(data_dir, "processed", "Vectorizer_ingredients.pkl"), 'rb') as file:
        vectorizer_ing = pickle.load(file)
    with open(os.path.join(data_dir, "processed", "TFidf_matrix.pkl"), 'rb') as file:
        tfidf_combined = pickle.load(file)
    with open(os.path.join(data_dir, "processed", "Recipes.pkl"), 'rb') as file:
        recipe_df = pickle.load(file)

    # For a 50/50 weighting, use the same query for both fields
    user_query_name = preprocessed_user_ingredients  # assuming query tokens are relevant to names
    user_query_ing = preprocessed_user_ingredients

    # Transform the user query for both vectorizers
    user_vector_name = vectorizer_name.transform([user_query_name])
    user_vector_ing = vectorizer_ing.transform([user_query_ing])

    # Combine the user vectors with the same weighting used during training (0.5 each)
    user_vector_combined = hstack([0.5 * user_vector_name, 0.5 * user_vector_ing])

    # Compute cosine similarity with the combined TF-IDF matrix
    similarity_scores = cosine_similarity(user_vector_combined, tfidf_combined)
    scores = similarity_scores.flatten()
    top_indices = scores.argsort()[-6:][::-1]
    
    # Debug prints
    print(f"\nSearch query: '{user_ingredients}'")
    print(f"Preprocessed query: '{preprocessed_user_ingredients}'")
    print(f"Top 6 similarity scores: {[round(scores[idx], 4) for idx in top_indices]}")
    
    threshold = 0.25  # Set your similarity threshold
    print(f"Threshold: {threshold}")

    # Get the similarity scores corresponding to top_indices
    filtered_indices = [idx for idx in top_indices if scores[idx] >= threshold]
    
    # Debug prints
    print(f"Filtered indices: {filtered_indices}")
    print(f"Filtered scores: {[round(scores[idx], 4) for idx in filtered_indices if idx < len(scores)]}")

    # Check if we have any results
    has_results = len(filtered_indices) > 0
    
    if has_results:
        recommended_recipes = recipe_df.iloc[filtered_indices].copy()
        # See caveats regarding assignment to a slice; using .loc avoids the warning
        recommended_recipes.loc[:, 'Instructions'] = recommended_recipes['Instructions'].apply(safe_literal_eval)
        print(f"Recipe names found: {recommended_recipes['RecipeName'].tolist()}")
    else:
        # Create an empty DataFrame with the same structure as recipe_df
        recommended_recipes = pd.DataFrame(columns=recipe_df.columns)
        print("No recipes met the similarity threshold")
    
    # Debug print
    print(f"Number of recommended recipes: {len(filtered_indices)}")
    print(f"Has results: {has_results}")
    print(f"Type of recipes passed to template: {type(recommended_recipes)}")
    print(f"Is recipes empty?: {len(recommended_recipes) == 0}")

    # Pass an empty DataFrame with the right structure if there are no results
    if not has_results:
        return render_template('res.html', recipes=recommended_recipes, has_results=False)
    
    return render_template('res.html', recipes=recommended_recipes, has_results=True)


@main.route('/add_to_favourites/<int:id>', methods=['GET'])
def add_to_favourites(id):
    existing_fav = Favourite.query.filter_by(user_id=current_user.id, recipe_id=id).first()
    if not existing_fav:
        new_fav = Favourite(user_id=current_user.id, recipe_id=id)
        db.session.add(new_fav)
        db.session.commit()
        flash('Added to favourites!', 'success')
    else:
        flash('Already added to Favourites', 'info')

    next_page = request.args.get('next')
    if next_page:
        return redirect(next_page)
    return redirect(request.referrer)

@main.route('/recipe_details/<int:id>',methods=['GET'])
@login_required
def recipe_details(id):
    with open(os.path.join(data_dir, "processed", "Recipes.pkl"), 'rb') as file:
        recipe_df = pickle.load(file)

    recipe = recipe_df[recipe_df['Srno'] == id].iloc[0]
    recipe['Instructions'] = safe_literal_eval(recipe['Instructions'])

    return render_template('recipe_details.html',recipe=recipe)

@main.route('/favourites')
@login_required
def favourites():
    fav_entries = Favourite.query.filter_by(user_id=current_user.id).all()
    recipe_ids = [fav.recipe_id for fav in fav_entries]
    with open(os.path.join(data_dir, "processed", "Recipes.pkl"), 'rb') as file:
        recipe_df = pickle.load(file)

    favs = recipe_df[recipe_df['Srno'].isin(recipe_ids)]

    return render_template('fav.html',favs=favs)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main.route('/save_profile', methods=['POST'])
@login_required
def save_profile():
    if request.method == 'POST':
        # Get form data
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        
        gender_map = {
            'Male': 'M',
            'Female': 'F'
        }
        
        user = current_user
        if phone:
            user.phone = int(phone) if phone.isdigit() else None
        user.gender = gender_map.get(gender, None)
        
        db.session.commit()
        
        # Show success message
        flash('Profile updated successfully!', 'success')
        
        return redirect(url_for('main.profile'))

@main.route('/discover')
@login_required
def discover():
    with open(os.path.join(data_dir, "processed", "Recipes.pkl"), 'rb') as file:
        recipe_df = pickle.load(file)
    
    # Pre-filter recipes by category and limit to 6 per category
    categories = ['Lunch', 'Snack', 'Dinner', 'South Indian Breakfast', 'North Indian Breakfast', 'Brunch']
    filtered_recipes = {}
    
    for category in categories:
        category_recipes = recipe_df[recipe_df['Course'] == category]
        if len(category_recipes) > 6:
            category_recipes = category_recipes.head(6)
        filtered_recipes[category] = category_recipes
    
    return render_template('discover.html', recipes=filtered_recipes)

@main.route('/')
def home():
    return render_template('index.html')
  

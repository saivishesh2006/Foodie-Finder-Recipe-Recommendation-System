import os
import pickle
from flask import Blueprint, request, render_template
from my_flask_app.utils.preprocess import preprocess_user_ingredients
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack
import re
import ast

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

@main.route('/home', methods=['GET','POST'])
def dish_finder():
    if request.method == 'POST':
        user_ingredients = request.form['ingredients']
        preprocessed_user_ingredients = preprocess_user_ingredients(user_ingredients)
        
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
        top_indices = scores.argsort()[-5:][::-1]
        
        recommended_recipes = recipe_df.iloc[top_indices]
        recommended_recipes['Instructions'] = recommended_recipes['Instructions'].apply(safe_literal_eval)
        return render_template('res.html', recipes=recommended_recipes)
    return render_template('dish_finder.html')


# @main.route('/profile')
# @login_required
# def profile():
#     return render_template('profile.html',name=current_user.name)

@main.route('/')
def home():
    return render_template('index.html')
  

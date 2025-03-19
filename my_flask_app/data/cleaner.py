import pandas as pd
from my_flask_app.utils.preprocess import preprocess_ingredients
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack
import pickle
import re

# --- Optional: Preprocess Recipe Names ---
def preprocess_recipe_name(name):
    # Simple preprocessing: lowercase and remove non-alphabetic characters
    name = name.lower()
    name = re.sub(r'[^a-z\s]', '', name)
    return name

# Read the Recipe file
df = pd.read_csv("data/raw/cleaned_IndianFoodDatasetCSV.csv")
df_original = df.copy(deep=True)

# Preprocess ingredients and recipe names
df['Ingredients'] = df['Ingredients'].apply(preprocess_ingredients)
df['RecipeName_clean'] = df['RecipeName'].apply(preprocess_recipe_name)

# Create two vectorizers: one for ingredients and one for recipe names
vectorizer_ing = TfidfVectorizer()
vectorizer_name = TfidfVectorizer()

# Fit and transform each field
tfidf_ing = vectorizer_ing.fit_transform(df['Ingredients'])
tfidf_name = vectorizer_name.fit_transform(df['RecipeName_clean'])

# Combine the two matrices with equal weight (50% each)
tfidf_combined = hstack([0.5 * tfidf_name, 0.5 * tfidf_ing])

# Save the combined matrix and both vectorizers for later use
with open('data/processed/TFidf_matrix.pkl', 'wb') as file:
    pickle.dump(tfidf_combined, file)

with open('data/processed/Vectorizer_names.pkl', 'wb') as file:
    pickle.dump(vectorizer_name, file)

with open('data/processed/Vectorizer_ingredients.pkl', 'wb') as file:
    pickle.dump(vectorizer_ing, file)

with open('data/processed/Recipes.pkl', 'wb') as file:
    pickle.dump(df_original, file)

print("Combined TF-IDF matrix, vectorizers, and recipes data saved.")

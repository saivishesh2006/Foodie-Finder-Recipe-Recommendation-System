import nltk
import re
import ast
from nltk.corpus import stopwords as nltk_stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

nltk.download('stopwords')
nltk.download('punkt')

stopwords = set(nltk_stopwords.words('english'))
stemmer = PorterStemmer()

paren_pattern = re.compile(r'\(.*\)')
non_alpha_pattern = re.compile(r'[^a-z\s]+')

measurements = [
    'tbsp', 'tbsp.', 'tablespoon', 'tablespoons',
    'tsp', 'tsp.', 'teaspoon', 'teaspoons',
    'oz', 'ounce', 'ounces', 'ounc',
    'fl oz', 'fl. oz', 'fluid ounce', 'fluid ounces', 'fluid ounc',
    'c', 'cup', 'cups',
    'qt', 'quart', 'quarts',
    'pt', 'pint', 'pints','pinch'
    'gal', 'gallon', 'gallons',
    'lb', 'pound', 'pounds',
    'ml', 'mL', 'millilitre', 'milliliter', 'milliliters',
    'cc',
    'g', 'gram', 'grams',
    'kg', 'kilogram', 'kilograms',
    'l', 'L', 'liter', 'liters', 'litre','inch'
]

# Extended list of generic and unwanted words
unwanted_words = [
    # Common generic cooking terms
    'chop', 'chopped', 'slice', 'sliced', 'cut', 'deseed', 'deseeded',
    'cooked', 'boil', 'boiled', 'soak', 'soaked', 'overnight', 'pressure',
    'fry', 'fried', 'grate', 'grated', 'puree', 'pureed', 'mince', 'minced',
    'dice', 'diced', 'shred', 'shredded','breast',
    
    # Pieces and measurements descriptions
    'piece', 'pieces', 'piec',
    
    # Size descriptors (if already not filtered by stopwords)
    'large', 'medium', 'mediums', 'small', 'best', 'big',
    'light', 'lightly', 'little', 'medium-large', 'mini', 'thick','few',
    
    # Additional preparation methods or descriptors
    'drain', 'drained', 'rinsed', 'julienned', 'crush', 'crushed',
    'sifted', 'rough', 'roughly', 'finely', 'coarse', 'coarsely',
    
    # Sometimes adjectives that are not informative for ingredient identity
    'fresh', 'extra', 'extra-large', 'extra-small',
    'tiny','used','garnish','and','an','the','a','as','per','taste','or','whole','crushed','homemade','cleaned','washed','separated',
    'cubed','broken','bunch','dice','finely','from','grated','handful','heavy', 'hot', 'into', 'mashed', 'mix', 'moist', 'more', 'needed', 'optional', 'or', 'peeled', 'prepared','pureed','roasted','scooped','seasoned','seasoning','slightly','smashed','soaked','some','sprig','squeezed','stalk','stick','strained','thinly','toasted','tsp','warm','wedges','well','with','without','your','oneinch','long','split'
]

def preprocess_ingredients(ingredients_input):
    """
    Preprocess a list of ingredients provided either as a list or as a string representation of a list.
    
    Steps:
    1. Convert input into a list if needed.
    2. For each ingredient:
       - Remove text within parentheses.
       - Take the text before the first comma (assuming it holds the primary ingredient name).
       - Remove any non-alphabetic characters.
       - Tokenize, stem, and filter out stopwords, measurement units, and unwanted words.
       - Exclude ingredients that contain generic words like 'oil', 'salt', or 'water'.
    3. Return a single string of processed ingredients.
    """
    # Convert input to a list if it is not already one
    if not isinstance(ingredients_input, list):
        try:
            ingredients_list = ast.literal_eval(ingredients_input)
        except Exception:
            # Fallback to a simple comma split if literal_eval fails
            ingredients_list = ingredients_input.split(',')
    else:
        ingredients_list = ingredients_input

    preprocessed = []  # Using list to preserve order

    for ingredient in ingredients_list:
        ingredient = paren_pattern.sub('', ingredient).strip()
        ingredient = ingredient.split(',')[0].lower()
        ingredient = non_alpha_pattern.sub('', ingredient).strip()
        ingredient_tokens = word_tokenize(ingredient)
        stemmed_tokens = [stemmer.stem(token) for token in ingredient_tokens]
        filtered_tokens = [
            token for token in stemmed_tokens
            if token not in stopwords 
            and token not in measurements 
            and token not in unwanted_words 
            and len(token) > 1
        ]
        # Reconstruct the ingredient string from the tokens
        cleansed_ingredient = ' '.join(filtered_tokens)
        # Exclude generic ingredients
        """
        These ingredients are used in almost every recipe, so they don't help differentiate one recipe from another. By removing them, the model can focus on more unique ingredients that are better at distinguishing between recipes
        """
        if ('oil' not in cleansed_ingredient and 
            'salt' not in cleansed_ingredient and 
            'water' not in cleansed_ingredient and 
            cleansed_ingredient != ''):
            preprocessed.append(cleansed_ingredient)
    
    return ' '.join(preprocessed)

def preprocess_user_ingredients(user_ingredients):
    """
    Preprocess user input ingredients.
    
    The function splits a string of ingredients (comma separated) into a list and then
    passes it to the preprocess_ingredients function.
    """
    ingredients_list = user_ingredients.split(',')
    return preprocess_ingredients(ingredients_list)

def preprocess_recipe_name(name):
    # Simple preprocessing: lowercase and remove non-alphabetic characters
    name = name.lower()
    name = re.sub(r'[^a-z\s]', '', name)
    return name

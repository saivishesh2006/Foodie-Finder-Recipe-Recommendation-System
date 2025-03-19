import nltk
import re
import ast
from nltk.corpus import stopwords as nltk_stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer,WordNetLemmatizer

# Download necessary NLTK resources if not already present
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

# Initialize stopwords and stemmer
stopwords = set(nltk_stopwords.words('english'))
stemmer = PorterStemmer()
lemmetizer = WordNetLemmatizer()

# Precompile regular expressions for efficiency
non_alpha_pattern = re.compile(r'[^a-z\s]+')

# List of measurement units remains unchanged
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
            ingredients_list = ingredients_input.split('-')
    else:
        ingredients_list = ingredients_input

    preprocessed = []  # Using list to preserve order

    for ingredient in ingredients_list:
        # Remove any text inside parentheses and trim whitespace
        ingredient = re.sub(r'[\(\)]', ' ', ingredient).strip()
        # Split on comma and take the first part (if there are additional descriptors)
        ingredient = ingredient.split(',')[0].lower()
        # Remove non-alphabetical characters
        ingredient = non_alpha_pattern.sub('', ingredient).strip()
        # Tokenize and then apply stemming
        ingredient_tokens = word_tokenize(ingredient)
        stemmed_tokens = [lemmetizer.lemmatize(token) for token in ingredient_tokens]
        # Filter tokens: remove stopwords, measurement units, unwanted words, and very short tokens
        filtered_tokens = [
            token for token in stemmed_tokens
            if token not in stopwords 
            and token not in measurements 
            and token not in unwanted_words 
            and len(token) > 1
        ]
        # Reconstruct the ingredient string from the tokens
        cleansed_ingredient = ' '.join(filtered_tokens)
        # Exclude generic ingredients if necessary
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
    s = preprocess_ingredients(ingredients_list)
    words = s.split()

    # Use dict.fromkeys to remove duplicates while preserving the order
    unique_words = list(dict.fromkeys(words))

    # Join the unique words back into a string
    result = " ".join(unique_words)
    return result


# Example usage:
if __name__ == "__main__":
    # Sample ingredient string taken from your dataset examples
    ing_str = (
        "300 grams Boneless chicken - cut into pieces,1/2 cup Curd (Dahi / Yogurt),2 teaspoon Ginger Garlic Paste,1/2 teaspoon Turmeric powder (Haldi),1/2 teaspoon Garam masala powder,1 teaspoon Kashmiri Red Chilli Powder,1 teaspoon Salt,1 tablespoon Butter,1 teaspoon Red Chilli powder,1 teaspoon Coriander Powder (Dhania),1/2 teaspoon Garam masala powder,1 cup Homemade tomato puree,1 teaspoon Honey,1/4 cup Fresh cream,1 tablespoon Kasuri Methi (Dried Fenugreek Leaves),Salt - to taste,1/4 cup Fresh cream,1 tablespoon Kasuri Methi (Dried Fenugreek Leaves),Salt - to taste"
    )
    
    preprocessed_ingredients = preprocess_user_ingredients(ing_str)
    print("Preprocessed Ingredients:")
    print(preprocessed_ingredients)


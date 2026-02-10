import re
from typing import List, Tuple

# Keywords allowed in nutrition-related discussions
NUTRITION_KEYWORDS = {
    'meal', 'food', 'eat', 'eating', 'breakfast', 'lunch', 'dinner', 'snack',
    'calories', 'calorie', 'macro', 'macros', 'protein', 'carbs', 'carbohydrates',
    'fat', 'fats', 'nutrition', 'nutritious', 'healthy', 'diet', 'dietary',
    'recipe', 'ingredient', 'ingredients', 'cooking', 'cook', 'prepared',
    'energy', 'weight', 'health', 'condition', 'medical', 'diabetic', 'diabetes',
    'cholesterol', 'blood pressure', 'celiac', 'lactose', 'allergy', 'allergic',
    'gluten', 'vegan', 'vegetarian', 'organic', 'nutrients', 'vitamin', 'minerals',
    'sodium', 'sugar', 'fiber', 'portion', 'serving', 'caloric', 'wellness',
    'fitness', 'exercise', 'balance', 'monitor', 'track', 'analyze', 'analysis',
    'hello', 'hi', 'start', 'help', 'test', 'ok', 'okay', 'thanks', 'thank',
    'yes', 'no', 'good', 'bad', 'more', 'question', 'why', 'how', 'continue'
}

HEALTH_CONDITIONS = [
    'diabetes', 'heart disease', 'hypertension', 'high blood pressure',
    'obesity', 'celiac', 'lactose intolerant', 'gluten free', 'vegan',
    'vegetarian', 'allergic', 'allergy', 'asthma', 'thyroid', 'pcos',
    'cholesterol', 'kidney disease', 'liver disease', 'high cholesterol',
    'low sodium', 'low fat', 'low carb', 'keto', 'anemia', 'pregnant'
]

def validate_input(message: str, media_url=None) -> bool:
    """
    Validate input to ensure it's nutrition-related
    Returns: bool - True if valid, False otherwise
    """
    # If there's an image, it's likely a meal
    if media_url:
        return True
    
    # Check if message is not empty
    message = message.strip().lower()
    if not message or len(message) < 3:
        return False
    
    return True

def is_nutrition_related(message: str) -> bool:
    """
    Check if message is related to nutrition/meals
    Returns: bool - True if nutrition-related, False otherwise
    """
    message = message.lower().strip()
    
    # Remove common question words
    question_words = ['what', 'is', 'are', 'do', 'did', 'will', 'can', 'should', 'how', 'why', 'when', 'where']
    words = message.split()
    
    # Check for nutrition keywords
    nutrition_found = False
    for word in words:
        # Remove punctuation
        clean_word = re.sub(r'[^a-z0-9]', '', word)
        if clean_word in NUTRITION_KEYWORDS:
            nutrition_found = True
            break
    
    # Check for food items (very basic pattern for common foods)
    common_foods = [
        'rice', 'bread', 'chicken', 'beef', 'fish', 'salmon', 'egg', 'eggs',
        'milk', 'yogurt', 'cheese', 'apple', 'banana', 'orange', 'pasta',
        'pizza', 'burger', 'fries', 'salad', 'soup', 'curry', 'biryani',
        'dosa', 'idli', 'samosa', 'roti', 'naan', 'paratha', 'dal', 'lentil',
        'vegetable', 'vegetables', 'fruit', 'fruits', 'meat', 'seafood',
        'dessert', 'cake', 'cookies', 'chocolate', 'coffee', 'tea', 'juice',
        'smoothie', 'protein', 'carbohydrate', 'fat', 'sugar', 'salt'
    ]
    
    for food in common_foods:
        if food in message:
            nutrition_found = True
            break
    
    # Pattern matching for meal descriptions
    # E.g., "I ate...", "I had...", "I'm eating...", "for lunch I...", "contains..."
    meal_patterns = [
        r'i\s+(ate|had|eaten|eating|have|took)',
        r'(breakfast|lunch|dinner|snack)\s*:',
        r'(contains|has|with|made of|made from)\s+',
        r'how\s+(many|much)\s+(calories|macros|protein)',
        r'(calories|macros|nutrition)\s+(in|for)',
        r'is\s+\w+\s+(healthy|good|bad)',
        r'\d+\s*(calories|grams|kcal|mg|carbs)',
    ]
    
    for pattern in meal_patterns:
        if re.search(pattern, message):
            nutrition_found = True
            break
    
    return nutrition_found

def extract_health_conditions(message: str) -> List[str]:
    """
    Extract health conditions mentioned in the message
    Returns: List of health conditions found
    """
    message = message.lower()
    conditions = []
    
    for condition in HEALTH_CONDITIONS:
        if condition in message:
            conditions.append(condition)
    
    return list(set(conditions))  # Remove duplicates

def sanitize_input(text: str) -> str:
    """Remove potential injection attempts"""
    # Remove special characters except for meal-related ones
    sanitized = re.sub(r'[<>\"\'`]', '', text)
    return sanitized.strip()

def format_nutrition_response(calories: int, protein: float, carbs: float, fats: float) -> str:
    """Format nutrition data for display"""
    return f"""
📊 Nutritional Summary:
- Calories: {calories} kcal
- Protein: {protein}g
- Carbohydrates: {carbs}g
- Fats: {fats}g
"""

def split_long_message(message: str, max_length: int = 1600) -> List[str]:
    """Split long messages into chunks for WhatsApp"""
    if len(message) <= max_length:
        return [message]
    
    messages = []
    current = ""
    
    for paragraph in message.split('\n'):
        if len(current) + len(paragraph) + 1 > max_length:
            if current:
                messages.append(current)
            current = paragraph
        else:
            current += ('\n' if current else '') + paragraph
    
    if current:
        messages.append(current)
    
    return messages

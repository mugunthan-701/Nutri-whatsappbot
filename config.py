"""
Advanced configuration for WhatsApp Nutrition Bot
"""

# Nutrition Boundaries and Recommendations
NUTRITION_CONFIG = {
    # Daily caloric intake ranges (in kcal)
    "caloric_intake": {
        "sedentary_adult": {"min": 1800, "max": 2200},
        "moderate_activity": {"min": 2200, "max": 2800},
        "active": {"min": 2800, "max": 3500},
        "high_activity": {"min": 3000, "max": 4000},
    },
    
    # Macronutrient ratios (%)
    "macro_ratios": {
        "balanced": {"protein": 30, "carbs": 45, "fats": 25},
        "low_carb": {"protein": 35, "carbs": 25, "fats": 40},
        "high_protein": {"protein": 40, "carbs": 40, "fats": 20},
        "ketogenic": {"protein": 25, "carbs": 5, "fats": 70},
    },
    
    # Protein requirements (g per kg body weight)
    "protein_requirements": {
        "sedentary": 0.8,
        "moderate_activity": 1.2,
        "strength_training": 1.6,
        "athlete": 2.0,
    }
}

# Health Condition Specific Guidance
HEALTH_GUIDANCE = {
    "diabetes": {
        "avoid": ["high_sugar", "refined_carbs", "sugary_drinks"],
        "prefer": ["whole_grains", "vegetables", "lean_proteins"],
        "macros": "balanced",
        "fiber_min": 25,  # grams
        "note": "Monitor carb intake and choose complex carbs"
    },
    "heart_disease": {
        "avoid": ["saturated_fat", "trans_fats", "high_sodium"],
        "prefer": ["omega3", "whole_grains", "fruits", "vegetables"],
        "macros": "balanced",
        "saturated_fat_max": 5,  # % of calories
        "sodium_max": 2300,  # mg/day
        "note": "Focus on heart-healthy fats and limit sodium"
    },
    "hypertension": {
        "avoid": ["high_sodium", "processed_foods"],
        "prefer": ["potassium_rich", "magnesium_rich", "whole_grains"],
        "sodium_max": 2300,  # mg/day
        "potassium_target": 3500,  # mg/day
        "note": "Reduce salt intake and increase potassium"
    },
    "celiac": {
        "avoid": ["gluten"],
        "prefer": ["gluten_free_grains", "fruits", "vegetables", "meat"],
        "note": "Strictly avoid all wheat, barley, rye"
    },
    "lactose_intolerance": {
        "avoid": ["lactose"],
        "prefer": ["lactose_free", "dairy_alternatives", "fortified_foods"],
        "note": "Choose lactose-free products or dairy alternatives"
    },
    "vegetarian": {
        "avoid": ["meat"],
        "prefer": ["legumes", "nuts", "seeds", "dairy", "eggs"],
        "note": "Ensure adequate protein from plant sources"
    },
    "vegan": {
        "avoid": ["animal_products"],
        "prefer": ["legumes", "nuts", "seeds", "whole_grains"],
        "note": "Combine protein sources for complete amino acids"
    },
    "obesity": {
        "avoid": ["high_calorie", "processed_foods", "sugary_drinks"],
        "prefer": ["whole_foods", "vegetables", "lean_proteins"],
        "macros": "high_protein",
        "note": "Focus on whole foods and portion control"
    }
}

# Common Food Calorie Database (approximate)
FOOD_CALORIES = {
    # Grains and Carbs
    "rice": {"calories": 206, "protein": 4.3, "carbs": 45, "fats": 0.3, "unit": "100g"},
    "wheat_bread": {"calories": 265, "protein": 9, "carbs": 49, "fats": 3.2, "unit": "100g"},
    "pasta": {"calories": 131, "protein": 5, "carbs": 25, "fats": 1.1, "unit": "100g"},
    "potato": {"calories": 77, "protein": 2, "carbs": 17, "fats": 0.1, "unit": "100g"},
    
    # Proteins
    "chicken_breast": {"calories": 165, "protein": 31, "carbs": 0, "fats": 3.6, "unit": "100g"},
    "beef": {"calories": 250, "protein": 26, "carbs": 0, "fats": 15, "unit": "100g"},
    "fish_salmon": {"calories": 208, "protein": 20, "carbs": 0, "fats": 13, "unit": "100g"},
    "egg": {"calories": 155, "protein": 13, "carbs": 1.1, "fats": 11, "unit": "1 large"},
    "lentils": {"calories": 116, "protein": 9, "carbs": 20, "fats": 0.4, "unit": "100g"},
    
    # Vegetables
    "broccoli": {"calories": 34, "protein": 2.8, "carbs": 7, "fats": 0.4, "unit": "100g"},
    "spinach": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fats": 0.4, "unit": "100g"},
    "carrot": {"calories": 41, "protein": 0.9, "carbs": 10, "fats": 0.2, "unit": "100g"},
    
    # Fruits
    "banana": {"calories": 89, "protein": 1.1, "carbs": 23, "fats": 0.3, "unit": "100g"},
    "apple": {"calories": 52, "protein": 0.3, "carbs": 14, "fats": 0.2, "unit": "100g"},
    "orange": {"calories": 47, "protein": 0.9, "carbs": 12, "fats": 0.1, "unit": "100g"},
    
    # Dairy
    "milk": {"calories": 61, "protein": 3.2, "carbs": 4.8, "fats": 3.3, "unit": "100ml"},
    "yogurt": {"calories": 59, "protein": 3.5, "carbs": 3.3, "fats": 0.4, "unit": "100g"},
    
    # Oils and Fats
    "olive_oil": {"calories": 884, "protein": 0, "carbs": 0, "fats": 100, "unit": "100ml"},
    "butter": {"calories": 717, "protein": 0.9, "carbs": 0.1, "fats": 81, "unit": "100g"},
}

# API Rate Limiting
RATE_LIMITING = {
    "enabled": True,
    "requests_per_minute": 30,
    "requests_per_hour": 1000,
}

# Response Configuration
RESPONSE_CONFIG = {
    "max_message_length": 1600,  # WhatsApp limit
    "gemini_temperature": 0.3,  # Lower = less creative, more factual
    "gemini_top_p": 0.8,
    "gemini_top_k": 40,
}

# Data Retention
DATA_RETENTION = {
    "interaction_retention_days": 90,  # Delete after 90 days
    "auto_cleanup_enabled": True,
    "cleanup_check_interval_days": 7,
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "nutrition_bot.log",
    "max_file_size": 10485760,  # 10 MB
    "backup_count": 5,
}

# Feature Flags
FEATURES = {
    "image_analysis_enabled": True,
    "health_condition_tracking_enabled": True,
    "daily_summary_enabled": False,
    "weekly_report_enabled": False,
    "user_analytics_enabled": True,
}

# Validation Configuration
VALIDATION = {
    "min_message_length": 3,
    "max_message_length": 10000,
    "allowed_image_types": ["image/jpeg", "image/png", "image/webp"],
    "max_image_size": 5242880,  # 5 MB
}

# Gemini Safety Settings
GEMINI_SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

def get_health_guidance(condition: str) -> dict:
    """Get specific guidance for a health condition"""
    condition_lower = condition.lower().replace(" ", "_")
    return HEALTH_GUIDANCE.get(condition_lower, {})

def get_food_info(food_name: str) -> dict:
    """Get nutritional info for a food item"""
    food_lower = food_name.lower().replace(" ", "_")
    return FOOD_CALORIES.get(food_lower, {})

def get_caloric_recommendations(activity_level: str) -> dict:
    """Get caloric intake recommendations based on activity level"""
    return NUTRITION_CONFIG["caloric_intake"].get(activity_level, {})

import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
from utils import (
    validate_input, is_nutrition_related, extract_health_conditions,
    sanitize_input, format_nutrition_response, split_long_message
)
from database import Database
import tempfile
import os

class TestValidation(unittest.TestCase):
    """Test input validation functions"""
    
    def test_validate_input_with_text(self):
        """Test validation with text input"""
        self.assertTrue(validate_input("I ate rice and chicken"))
        self.assertFalse(validate_input(""))
        self.assertFalse(validate_input("ab"))
    
    def test_validate_input_with_image(self):
        """Test validation with image URL"""
        self.assertTrue(validate_input("", media_url="https://example.com/image.jpg"))
        self.assertTrue(validate_input("food image", media_url="https://example.com/image.jpg"))
    
    def test_nutrition_related_detection(self):
        """Test nutrition-related message detection"""
        nutrition_messages = [
            "I ate rice and chicken",
            "how many calories in pizza?",
            "I'm having breakfast",
            "what's the protein in eggs?",
            "I have diabetes, what should I eat?"
        ]
        
        for msg in nutrition_messages:
            self.assertTrue(is_nutrition_related(msg), f"Failed for message: {msg}")
    
    def test_non_nutrition_detection(self):
        """Test non-nutrition message detection"""
        non_nutrition = [
            "what's the weather?",
            "tell me a joke",
            "what time is it?",
            "hello how are you"
        ]
        
        for msg in non_nutrition:
            self.assertFalse(is_nutrition_related(msg), f"Failed for message: {msg}")
    
    def test_health_condition_extraction(self):
        """Test health condition extraction"""
        message = "I have diabetes and celiac disease, I ate rice"
        conditions = extract_health_conditions(message)
        
        self.assertIn("diabetes", conditions)
        self.assertIn("celiac", conditions)
        self.assertEqual(len(conditions), 2)
    
    def test_health_condition_extraction_empty(self):
        """Test extraction when no conditions mentioned"""
        message = "I ate rice for lunch"
        conditions = extract_health_conditions(message)
        
        self.assertEqual(len(conditions), 0)
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        unsafe = "<script>alert('xss')</script> I ate rice"
        safe = sanitize_input(unsafe)
        
        self.assertNotIn("<", safe)
        self.assertNotIn(">", safe)
        self.assertNotIn("script", safe)
        self.assertIn("rice", safe.lower())
    
    def test_nutrition_response_format(self):
        """Test nutrition response formatting"""
        response = format_nutrition_response(500, 25.5, 60.0, 15.3)
        
        self.assertIn("500", response)
        self.assertIn("25.5", response)
        self.assertIn("60", response)
        self.assertIn("15.3", response)
        self.assertIn("📊", response)
    
    def test_message_splitting(self):
        """Test long message splitting"""
        long_msg = "A" * 5000
        split = split_long_message(long_msg, max_length=1000)
        
        self.assertGreater(len(split), 1)
        for msg in split:
            self.assertLessEqual(len(msg), 1000)


class TestDatabase(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Create temporary database for testing"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
    
    def tearDown(self):
        """Clean up temporary database"""
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_create_user(self):
        """Test user creation"""
        user = self.db.create_user("whatsapp:+919876543210", "Test User")
        
        self.assertEqual(user['phone_number'], "whatsapp:+919876543210")
        self.assertEqual(user['name'], "Test User")
    
    def test_get_user(self):
        """Test user retrieval"""
        phone = "whatsapp:+919876543210"
        self.db.create_user(phone, "Test User")
        user = self.db.get_user(phone)
        
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], "Test User")
    
    def test_update_health_conditions(self):
        """Test updating user health conditions"""
        phone = "whatsapp:+919876543210"
        self.db.create_user(phone, "Test User")
        
        conditions = ["diabetes", "heart disease"]
        self.db.update_user_conditions(phone, conditions)
        
        user = self.db.get_user(phone)
        self.assertIn("diabetes", user['health_conditions'])
    
    def test_store_interaction(self):
        """Test storing interaction"""
        phone = "whatsapp:+919876543210"
        self.db.create_user(phone, "Test User")
        
        self.db.store_interaction(
            phone_number=phone,
            user_input="I ate rice",
            bot_response="Analysis...",
            health_conditions=["diabetes"],
            has_image=False,
            timestamp=datetime.now()
        )
        
        history = self.db.get_user_history(phone, limit=10)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['user_input'], "I ate rice")
    
    def test_get_statistics(self):
        """Test statistics retrieval"""
        phone1 = "whatsapp:+919876543210"
        phone2 = "whatsapp:+919876543211"
        
        self.db.create_user(phone1, "User 1")
        self.db.create_user(phone2, "User 2")
        
        self.db.store_interaction(
            phone_number=phone1,
            user_input="I ate rice",
            bot_response="Analysis",
            health_conditions=[],
            has_image=False,
            timestamp=datetime.now()
        )
        
        stats = self.db.get_statistics()
        
        self.assertEqual(stats['total_users'], 2)
        self.assertGreater(stats['total_interactions'], 0)


class TestMealAnalysisKeywords(unittest.TestCase):
    """Test various meal-related keywords"""
    
    def test_indian_food_keywords(self):
        """Test Indian food keywords"""
        meals = [
            "I had biryani for lunch",
            "I ate dosa and samosa",
            "I cooked dal and roti",
            "I had idli with chutney"
        ]
        
        for meal in meals:
            self.assertTrue(is_nutrition_related(meal), f"Failed: {meal}")
    
    def test_international_food_keywords(self):
        """Test international food keywords"""
        meals = [
            "I ate sushi for dinner",
            "I had pasta and pizza",
            "I cooked salmon with vegetables",
            "I had burger and fries"
        ]
        
        for meal in meals:
            self.assertTrue(is_nutrition_related(meal), f"Failed: {meal}")
    
    def test_health_condition_keywords(self):
        """Test disease/condition keywords"""
        messages = [
            "I'm vegetarian",
            "I'm vegan",
            "I have gluten allergy",
            "I'm lactose intolerant",
            "I'm diabetic"
        ]
        
        for msg in messages:
            self.assertTrue(is_nutrition_related(msg), f"Failed: {msg}")


class TestHallucinationPrevention(unittest.TestCase):
    """Test hallucination prevention"""
    
    def test_random_questions_rejected(self):
        """Test that random non-nutrition questions are rejected"""
        random_questions = [
            "Write me a poem",
            "What's 2+2?",
            "Tell me about Python programming",
            "Who is the president?",
            "What's the capital of France?",
            "Tell me a joke",
            "What's the weather today?"
        ]
        
        for question in random_questions:
            result = is_nutrition_related(question)
            self.assertFalse(result, f"Hallucination check failed for: {question}")


class TestImageAnalysisPrompt(unittest.TestCase):
    """Test image analysis prompt construction"""
    
    @patch('app.gemini_model')
    def test_image_only_prompt_includes_system_prompt(self, mock_model):
        """Test that image-only analysis includes system prompt and image instructions"""
        from app import analyze_meal_with_gemini, SYSTEM_PROMPT
        
        mock_response = MagicMock()
        mock_response.text = "• Rice and Curry\n• ~450 kcal | 15g protein | 60g carbs | 12g fat\nDecent balanced meal."
        mock_model.generate_content.return_value = mock_response
        
        # Simulate image data (small fake image bytes)
        fake_image_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        
        result = analyze_meal_with_gemini("", fake_image_data, "image/jpeg")
        
        # Verify generate_content was called
        mock_model.generate_content.assert_called_once()
        call_args = mock_model.generate_content.call_args
        content = call_args[0][0]
        
        # Content should be a list with prompt string + image part
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 2)
        
        # First element is the prompt text - should include system prompt
        prompt_text = content[0]
        self.assertIn("Calories", prompt_text)
        self.assertIn("Protein", prompt_text)
        self.assertIn("Carbs", prompt_text)
        self.assertIn("Fat", prompt_text)
        self.assertIn("nutrition assistant", prompt_text)
        
        # Second element should be the image part
        image_part = content[1]
        self.assertEqual(image_part["mime_type"], "image/jpeg")
        self.assertIn("data", image_part)
    
    @patch('app.gemini_model')
    def test_image_with_text_prompt(self, mock_model):
        """Test that image+text analysis includes both user text and image instructions"""
        from app import analyze_meal_with_gemini
        
        mock_response = MagicMock()
        mock_response.text = "• Biryani\n• ~500 kcal | 20g protein | 65g carbs | 15g fat"
        mock_model.generate_content.return_value = mock_response
        
        fake_image_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        
        result = analyze_meal_with_gemini("this is my lunch biryani", fake_image_data, "image/png")
        
        call_args = mock_model.generate_content.call_args
        content = call_args[0][0]
        
        # Prompt should mention user's text and image analysis
        prompt_text = content[0]
        self.assertIn("biryani", prompt_text)
        self.assertIn("image", prompt_text.lower())
        
        # Image part should use correct mime type
        image_part = content[1]
        self.assertEqual(image_part["mime_type"], "image/png")
    
    @patch('app.gemini_model')
    def test_health_conditions_in_prompt(self, mock_model):
        """Test that health conditions are included in the prompt"""
        from app import analyze_meal_with_gemini
        
        mock_response = MagicMock()
        mock_response.text = "Analysis with health conditions considered."
        mock_model.generate_content.return_value = mock_response
        
        result = analyze_meal_with_gemini(
            "I ate rice and chicken",
            health_conditions=["diabetes", "heart disease"]
        )
        
        call_args = mock_model.generate_content.call_args
        content = call_args[0][0]
        
        # Content should be a list with just the prompt (no image)
        prompt_text = content[0]
        self.assertIn("diabetes", prompt_text)
        self.assertIn("heart disease", prompt_text)
    
    @patch('app.gemini_model')
    def test_text_only_includes_system_prompt(self, mock_model):
        """Test that text-only analysis also includes system prompt"""
        from app import analyze_meal_with_gemini, SYSTEM_PROMPT
        
        mock_response = MagicMock()
        mock_response.text = "• 2 Eggs + Toast\n• ~350 kcal | 20g protein | 30g carbs | 15g fat"
        mock_model.generate_content.return_value = mock_response
        
        result = analyze_meal_with_gemini("I ate 2 eggs and toast")
        
        call_args = mock_model.generate_content.call_args
        content = call_args[0][0]
        
        # Text-only content should also include system prompt
        prompt_text = content[0]
        self.assertIn("nutrition assistant", prompt_text)
        self.assertIn("Calories", prompt_text)
    
    @patch('app.gemini_model')
    def test_webp_image_mime_type(self, mock_model):
        """Test that webp images are supported with correct MIME type"""
        from app import analyze_meal_with_gemini
        
        mock_response = MagicMock()
        mock_response.text = "• Salad\n• ~150 kcal | 5g protein | 20g carbs | 5g fat"
        mock_model.generate_content.return_value = mock_response
        
        fake_image_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        
        result = analyze_meal_with_gemini("salad", fake_image_data, "image/webp")
        
        call_args = mock_model.generate_content.call_args
        content = call_args[0][0]
        image_part = content[1]
        self.assertEqual(image_part["mime_type"], "image/webp")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestMealAnalysisKeywords))
    suite.addTests(loader.loadTestsFromTestCase(TestHallucinationPrevention))
    suite.addTests(loader.loadTestsFromTestCase(TestImageAnalysisPrompt))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)

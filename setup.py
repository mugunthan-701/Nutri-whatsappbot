#!/usr/bin/env python3
"""
WhatsApp Nutrition Bot - Quick Setup Script
This script helps you set up and test your WhatsApp nutrition bot
"""

import os
import sys
import subprocess
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def check_python():
    """Check Python version"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.9+ required (you have {version.major}.{version.minor})")
        return False

def create_venv():
    """Create virtual environment"""
    print_header("Creating Virtual Environment")
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print_success("Virtual environment created")
        return True
    except Exception as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False

def activate_venv():
    """Print activation instructions"""
    print_header("Activating Virtual Environment")
    
    if sys.platform == "win32":
        print("Run: venv\\Scripts\\activate")
    else:
        print("Run: source venv/bin/activate")
    
    input("\nPress Enter once you've activated the virtual environment...")
    return True

def install_requirements():
    """Install Python requirements"""
    print_header("Installing Dependencies")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=False)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print_success("All dependencies installed")
        return True
    except Exception as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def setup_env_file():
    """Setup .env file"""
    print_header("Setting Up Environment Variables")
    
    env_path = Path(".env")
    example_path = Path(".env.example")
    
    if env_path.exists():
        print_warning(".env file already exists")
        return True
    
    if example_path.exists():
        import shutil
        shutil.copy(example_path, env_path)
        print_success(".env file created from .env.example")
    else:
        # Create minimal .env
        with open(env_path, 'w') as f:
            f.write("""# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155552671

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Flask Configuration
DEBUG=False
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# Server Configuration
PORT=5000
HOST=0.0.0.0
""")
        print_success(".env file created")
    
    print_warning("⚠️  Edit .env file with your API credentials:")
    print(f"   - TWILIO_ACCOUNT_SID")
    print(f"   - TWILIO_AUTH_TOKEN")
    print(f"   - TWILIO_WHATSAPP_NUMBER")
    print(f"   - GEMINI_API_KEY")
    
    return True

def test_imports():
    """Test if all imports work"""
    print_header("Testing Imports")
    
    try:
        import flask
        print_success("Flask imported")
        
        import requests
        print_success("Requests imported")
        
        import google.generativeai
        print_success("Google Generative AI imported")
        
        import twilio
        print_success("Twilio imported")
        
        print_success("All imports successful!")
        return True
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return False

def test_database():
    """Test database"""
    print_header("Testing Database")
    
    try:
        from database import Database
        db = Database("test.db")
        print_success("Database initialized successfully")
        
        # Test user creation
        user = db.create_user("whatsapp:+919999999999", "Test User")
        print_success(f"Test user created: {user.get('phone_number')}")
        
        # Test user retrieval
        retrieved = db.get_user("whatsapp:+919999999999")
        if retrieved:
            print_success("Test user retrieved")
        
        # Cleanup
        os.remove("test.db")
        print_success("Test database cleaned up")
        return True
    
    except Exception as e:
        print_error(f"Database test failed: {e}")
        return False

def test_utils():
    """Test utility functions"""
    print_header("Testing Utility Functions")
    
    try:
        from utils import (
            validate_input, is_nutrition_related, 
            extract_health_conditions, sanitize_input
        )
        
        # Test nutrition detection
        if is_nutrition_related("I ate rice"):
            print_success("Nutrition detection working")
        else:
            print_error("Nutrition detection failed")
            return False
        
        # Test non-nutrition rejection
        if not is_nutrition_related("What's the weather?"):
            print_success("Non-nutrition rejection working")
        else:
            print_error("Non-nutrition detection failed")
            return False
        
        # Test health condition extraction
        conditions = extract_health_conditions("I'm diabetic and vegan")
        if "diabetes" in conditions and "vegan" in conditions:
            print_success("Health condition extraction working")
        else:
            print_error("Health condition extraction failed")
            return False
        
        print_success("All utility tests passed!")
        return True
    
    except Exception as e:
        print_error(f"Utility test failed: {e}")
        return False

def show_next_steps():
    """Show next steps"""
    print_header("Next Steps")
    
    print(f"""
{Colors.GREEN}✓ Setup Complete!{Colors.END}

Your WhatsApp Nutrition Bot is ready for development!

{Colors.YELLOW}REQUIRED BEFORE RUNNING:{Colors.END}
1. Get API Credentials:
   - Twilio: https://www.twilio.com/console
   - Gemini: https://makersuite.google.com/app/apikey

2. Update .env file with your credentials

3. For testing locally:
   - Install ngrok: https://ngrok.com
   - Run: ngrok http 5000
   - Add webhook to Twilio: https://your-ngrok-url/webhook

{Colors.YELLOW}TO RUN THE BOT:{Colors.END}
   python app.py

{Colors.YELLOW}TO RUN TESTS:{Colors.END}
   python test_bot.py

{Colors.YELLOW}FOR DOCKER DEPLOYMENT:{Colors.END}
   docker-compose up

{Colors.YELLOW}FOR PRODUCTION DEPLOYMENT:{Colors.END}
   See README.md for detailed deployment instructions

{Colors.BLUE}Happy Building! 🚀{Colors.END}
""")

def main():
    """Main setup flow"""
    print(f"\n{Colors.BLUE}")
    print(" " * 15 + "WhatsApp Nutrition Bot Setup")
    print(f"{Colors.END}")
    
    # Check Python
    if not check_python():
        sys.exit(1)
    
    # Create venv
    if not os.path.exists("venv"):
        if not create_venv():
            sys.exit(1)
    else:
        print_warning("Virtual environment already exists")
    
    print("\n" + "="*60)
    print("IMPORTANT: Virtual environment created!")
    print("="*60)
    if sys.platform == "win32":
        print("\nActivate it by running:")
        print(f"{Colors.YELLOW}venv\\Scripts\\activate{Colors.END}")
    else:
        print("\nActivate it by running:")
        print(f"{Colors.YELLOW}source venv/bin/activate{Colors.END}")
    
    response = input("\nHave you activated the virtual environment? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print_error("Please activate the virtual environment first")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Test database
    if not test_database():
        sys.exit(1)
    
    # Test utils
    if not test_utils():
        sys.exit(1)
    
    # Setup env file
    setup_env_file()
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)

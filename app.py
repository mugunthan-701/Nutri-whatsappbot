import os
import json
import base64
import requests
from datetime import datetime
from flask import Flask, request, Response
from flask_cors import CORS
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
from database import Database
from utils import validate_input, is_nutrition_related, extract_health_conditions
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

@app.before_request
def log_request_info():
    """Log EVERY request headers and body"""
    print(f"\n[REQUEST] {request.method} {request.url}", flush=True)
    # print(f"Headers: {request.headers}", flush=True) # Uncomment for detailed headers
    # print(f"Body: {request.get_data(as_text=True)[:200]}...", flush=True) # Log first 200 chars of body

@app.route('/', methods=['GET', 'POST'])
def index():
    """Root endpoint"""
    if request.method == 'POST':
        print("\n" + "!"*50)
        print("⚠️  WARNING: Request received at root URL (/)")
        print("    You likely forgot to add '/webhook' to your Twilio URL!")
        print(f"    Correct URL should be: {request.host_url}webhook")
        print("!"*50 + "\n")
        return "Please update your webhook URL to include /webhook", 200
        
    return {
        "message": "WhatsApp Nutrition Bot is Running! 🚀",
        "endpoints": {
            "health_check": "/health",
            "statistics": "/stats",
            "webhook": "/webhook (POST only)"
        },
        "status": "online"
    }, 200

# Initialize Twilio
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')

# Ensure whatsapp: prefix
if twilio_whatsapp_number and not twilio_whatsapp_number.startswith('whatsapp:'):
    twilio_whatsapp_number = f"whatsapp:{twilio_whatsapp_number}"
    logger.info(f"Fixed Twilio number format: {twilio_whatsapp_number}")

# Initialize Twilio client only if credentials exist
twilio_client = None
if twilio_account_sid and twilio_auth_token:
    try:
        twilio_client = Client(twilio_account_sid, twilio_auth_token)
        logger.info("Twilio client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Twilio client: {e}")
        twilio_client = None
else:
    logger.warning("Twilio credentials not found in environment variables")

# Initialize Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
# User requested "flash 2.5", using 'gemini-2.0-flash' which is the closest new version
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

# Initialize Database
# Use a local SQLite file - ignore MONGODB_URI if present as we use SQLite
db = Database(os.getenv('DATABASE_PATH', 'nutrition_bot.db'))

# System prompt to prevent hallucination
SYSTEM_PROMPT = """You are a helpful nutrition assistant with a mild, friendly personality.
Goal: Analyze hunger/food requests or chat briefly.

RULES:
1. **BE CONCISE**: Keep responses short (under 100 words).
2. **SIMPLE SARCASM**: You can add a *tiny* bit of dry humor or a single emoji, but don't overdo it.
3. **NO FLUFF**: Get straight to the point.
4. **FORMATTING**: Use bullets (•) for lists. No markdown headers.

IF FOOD/MEAL:
- Food Name
- Approx Calories | Protein | Carbs | Fat
- 1 sentence verdict.

IF CHAT:
- Reply in 1-2 sentences max.
"""

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    """Handle incoming WhatsApp messages from Twilio"""
    if request.method == 'GET':
        return "✅ Webhook is reachable! Set this URL (POST) in Twilio settings.", 200

    print("\n" + "="*50)
    print("📩 WEBHOOK RECEIVED!")
    print(f"Time: {datetime.now()}")
    print("="*50)
    
    try:
        incoming_msg = request.values.get('Body', '').strip()
        user_phone = request.values.get('From', '')
        user_name = request.values.get('ProfileName', 'User')
        
        print(f"👤 User: {user_name} ({user_phone})")
        print(f"💬 Message: {incoming_msg}")

        # Check for Greeting
        if incoming_msg.lower() in ['hello', 'hi', 'start', 'help', 'menu', 'join']:
            welcome_msg = (
                f"Hello {user_name}! 👋\n\n"
                "I am your Nutrition Bot.\n"
                "Send me what you ate (text or photo) and I'll count the calories! 🍎\n\n"
                "Example: *'I ate 2 eggs and toast'*"
            )
            logger.info(f"Sending welcome message to {user_phone}")
            send_whatsapp_message(user_phone, welcome_msg)
            return "<Response></Response>", 200, {'Content-Type': 'application/xml'}
        
        # Extract media (images)
        num_media = int(request.values.get('NumMedia', 0))
        media_url = None
        if num_media > 0:
            media_url = request.values.get('MediaUrl0')
            media_type = request.values.get('MediaContentType0')
            if not media_type.startswith('image/'):
                media_url = None
        
        logger.info(f"Message from {user_phone}: {incoming_msg}")

        # --- 1. GET USER CONTEXT FIRST ---
        # Get user profile or create new one
        user_profile = db.get_user(user_phone)
        if not user_profile:
            # Create user locally first
            user_profile = db.create_user(user_phone, user_name)
            
        # Determine if this continues an active conversation (Active if last msg < 10 mins ago)
        is_continuing_convo = False
        if user_profile and user_profile.get('last_interaction'):
            try:
                # Handle ISO format string
                last_time = datetime.fromisoformat(user_profile['last_interaction'])
                minutes_since = (datetime.now() - last_time).total_seconds() / 60
                if minutes_since < 10:
                    is_continuing_convo = True
                    print(f"🔄 Continuing active conversation ({int(minutes_since)}m ago)")
            except Exception as e:
                print(f"Error parsing date: {e}")

        # --- 2. VALIDATION ---
        # Basic check for empty content
        if not incoming_msg and not media_url:
            print("❌ Validation rejected (Empty message)")
            return "<Response></Response>", 200, {'Content-Type': 'application/xml'}
        
        # --- 3. PROCESSING ---
        print("✅ Message accepted for processing...")

        # Retrieve recent conversation history for memory (last 5 messages)
        history = db.get_user_history(user_phone, limit=5)

        # Extract health conditions if mentioned
        health_conditions = extract_health_conditions(incoming_msg)
        if health_conditions:
            db.update_user_conditions(user_phone, health_conditions)
        
        # Process image if provided
        image_data = None
        if media_url:
            image_data = download_media(media_url)
        
        # Analyze meal using Gemini
        response_text = analyze_meal_with_gemini(
            incoming_msg, 
            image_data, 
            user_profile.get('health_conditions', []),
            history # Pass history
        )
        
        # Store interaction in database
        # Note: Argument names must match database.py definition
        db.store_interaction(
            phone_number=user_phone,
            user_input=incoming_msg,
            bot_response=response_text,
            health_conditions=health_conditions or user_profile.get('health_conditions', []),
            has_image=media_url is not None,
            timestamp=datetime.now()
        )
        
        # Send response using Twilio Client (Explicit Send)
        # This is more robust against timeouts than TwiML
        logger.info(f"Generating Response Length: {len(response_text)}")
        print(f"🤖 BOT RESPONSE:\n{response_text[:200]}...\n")
        
        send_whatsapp_message(user_phone, response_text)
        
        # Return empty TwiML to satisfy the webhook
        return "<Response></Response>", 200, {'Content-Type': 'application/xml'}
        
    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}")
        send_whatsapp_message(user_phone, "Sorry, I encountered an error. Please try again.")
        return "<Response></Response>", 200, {'Content-Type': 'application/xml'}

def analyze_meal_with_gemini(meal_description, image_data=None, health_conditions=None, history=None):
    """Analyze meal using Gemini API"""
    try:
        # Format history context if available
        history_context = ""
        if history:
            history_context = "\nPREVIOUS CONVERSATION (Use for context):\n"
            for item in reversed(history):  # Reverse to get chronological order from older to newer
                history_context += f"User: {item['user_input']}\nBot: {item['bot_response']}\n"
        
        # Simplified prompt to save tokens (Consise & Low Cost)
        prompt = f"""{history_context}
        User Input: '{meal_description}'
        
        Task: Provide a very short, specific response.
        - If meal: Stats + 1 sentence verdict.
        - If chat: 1 sentence reply.
        - Humor: Subtle/Dry (optional).
        - Max Length: ~60 words.
        """
        
        # Prepare content for Gemini
        content = [prompt]
        
        if image_data:
            # Add image to analysis
            image_part = {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_data).decode()
            }
            content.append(image_part)
        
        # Call Gemini API with system context
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
        
        # Use a model that definitely exists
        try:
            response = gemini_model.generate_content(
                content if image_data else full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.8,
                    top_k=40,
                )
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                return "⚠️ Server is busy (Rate Limit Reached). Please wait 1 minute and try again."
                
            # Fallback for model name errors
            logger.warning(f"Gemini model error: {e}. Trying 'gemini-1.5-pro'...")
            try:
                fallback_model = genai.GenerativeModel('gemini-1.5-pro')
                response = fallback_model.generate_content(full_prompt)
                return response.text
            except Exception as fallback_error:
                 logger.error(f"Fallback model failed: {fallback_error}")
                 if "429" in str(fallback_error):
                    return "⚠️ Server is busy (Quota Exceeded). Please try again later."
                 return f"Error analyzing meal: {str(fallback_error)}"
    
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return f"I was unable to analyze this meal. Error: {str(e)}"

def download_media(media_url):
    """Download media from Twilio"""
    try:
        response = requests.get(
            media_url,
            auth=(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN')),
            timeout=10
        )
        response.raise_for_status()
        
        # Validate image
        image = Image.open(BytesIO(response.content))
        image.verify()
        
        return response.content
    
    except Exception as e:
        logger.error(f"Error downloading media: {str(e)}")
        return None

def send_whatsapp_message(to_phone, message):
    """Send message via WhatsApp"""
    try:
        if not twilio_client:
            logger.warning("Twilio client not initialized - message not sent (demo mode)")
            logger.info(f"[DEMO] Would send to {to_phone}: {message[:100]}...")
            return
        
        print(f"📤 Sending message via Client...")
        print(f"   From: {twilio_whatsapp_number}")
        print(f"   To:   {to_phone}")

        # Split message if too long (WhatsApp has message limits)
        max_length = 1600
        if len(message) > max_length:
            messages = [message[i:i+max_length] for i in range(0, len(message), max_length)]
        else:
            messages = [message]
        
        for msg in messages:
            message_sid = twilio_client.messages.create(
                from_=twilio_whatsapp_number,
                to=to_phone,
                body=msg
            )
            print(f"✅ Message queued! SID: {message_sid.sid}")
            logger.info(f"Message sent to {to_phone}")
    
    except Exception as e:
        print(f"❌ FAILED to send message: {e}")
        logger.error(f"Error sending message: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "bot": "running",
        "twilio": "configured" if twilio_client else "not configured",
        "gemini": "configured" if os.getenv('GEMINI_API_KEY') else "not configured",
        "database": "ready"
    }
    return status, 200

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get bot statistics"""
    try:
        stats = db.get_statistics()
        return stats, 200
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {"error": str(e)}, 500

@app.route('/user/<phone>/history', methods=['GET'])
def get_user_history(phone):
    """Get user interaction history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = db.get_user_history(phone, limit=limit)
        return {"history": history}, 200
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return {"error": str(e)}, 500

if __name__ == '__main__':
    # Print startup information
    print("\n" + "="*70)
    print("  WhatsApp Nutrition Bot - Starting")
    print("="*70)
    
    # Check configuration status
    missing_creds = []
    if not os.getenv('TWILIO_ACCOUNT_SID'):
        missing_creds.append("TWILIO_ACCOUNT_SID")
    if not os.getenv('TWILIO_AUTH_TOKEN'):
        missing_creds.append("TWILIO_AUTH_TOKEN")
    if not os.getenv('TWILIO_WHATSAPP_NUMBER'):
        missing_creds.append("TWILIO_WHATSAPP_NUMBER")
    if not os.getenv('GEMINI_API_KEY'):
        missing_creds.append("GEMINI_API_KEY")
    
    if missing_creds:
        print(f"\n⚠️  MISSING CREDENTIALS:\n")
        for cred in missing_creds:
            print(f"   - {cred}")
        print(f"\n📝 CONFIGURATION REQUIRED:")
        print(f"   1. Edit your .env file (copy from .env.example if needed)")
        print(f"   2. Add the missing credentials above")
        print(f"   3. Save the file")
        print(f"   4. Restart the app\n")
        print(f"📖 For detailed setup instructions, see QUICKSTART.md\n")
        print(f"🔗 API Credentials:")
        print(f"   - Twilio: https://www.twilio.com/console")
        print(f"   - Gemini: https://makersuite.google.com/app/apikey\n")
        print("✅ Running in DEMO MODE - Twilio integration disabled")
        print("   (Messages will be logged but not sent to WhatsApp)\n")
    else:
        print("\n✅ All credentials configured!")
        print(f"✅ Twilio: {twilio_client is not None}")
        print(f"✅ Gemini: {bool(os.getenv('GEMINI_API_KEY'))}\n")
    
    print(f"🚀 Server starting on http://127.0.0.1:{os.getenv('PORT', 5000)}")
    print(f"📊 Health Check: http://127.0.0.1:{os.getenv('PORT', 5000)}/health")
    print(f"📈 Stats: http://127.0.0.1:{os.getenv('PORT', 5000)}/stats")
    print("="*70 + "\n")
    
    app.run(debug=os.getenv('DEBUG', 'False') == 'True', port=5000)

# Quick Start Guide for WhatsApp Nutrition Bot

## 5-Minute Quick Start

### 1. **Prerequisites**
```bash
# Check Python version (3.9 or higher)
python --version
```

### 2. **Clone and Setup**
```bash
cd c:\Users\shnek\OneDrive\Desktop\Mugunthan\whatsapBot
python setup.py
```

### 3. **Get API Keys** (2 services required)

#### Twilio (for WhatsApp)
1. Go to https://www.twilio.com/console
2. Sign up for free account
3. Look for Account SID and Auth Token
4. Go to Messaging → WhatsApp → Sandbox
5. Copy WhatsApp Number (starts with `whatsapp:+...`)

#### Google Gemini (for meal analysis)
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the API key

### 4. **Configure .env**
```bash
# Edit .env file with your keys
TWILIO_ACCOUNT_SID=your_sid_here
TWILIO_AUTH_TOKEN=your_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155552671
GEMINI_API_KEY=your_key_here
DEBUG=False
```

### 5. **Install Dependencies**
```bash
# Make sure you've activated the virtual environment
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Install requirements (if not done by setup.py)
pip install -r requirements.txt
```

### 6. **Run the Bot**
```bash
python app.py
```

You'll see:
```
 * Running on http://127.0.0.1:5000
```

### 7. **Connect to WhatsApp (The Easy Way)**

We've included a script that automatically creates a public URL for you.

```bash
python run_with_tunnel.py
```

It will output something like:
```
🌍 PUBLIC URL GENERATED!
👉 COPY THIS URL: https://a1b2c3d4.ngrok-free.app/webhook
```

### 8. **Configure Twilio**

1. Go to Twilio Console → Messaging → WhatsApp
2. Find "When a message comes in"
3. Paste the URL from step 7
4. Save

### 9. **Test the Bot**

1. In Twilio console, find the WhatsApp join code (e.g., "join silly-dog")
2. Send the code from your WhatsApp phone
3. Start messaging:
   - "I had rice and chicken for lunch"
   - Send a food image
   - "I'm diabetic, should I eat cake?"

## Common Issues

### Bot not responding?
```bash
# Check if server is running
# Check ngrok tunnel is active
# Verify .env credentials
# Check console for errors
```

### Messages failing?
```bash
# Verify you joined the WhatsApp sandbox
# Check Twilio balance/limits
# Ensure webhook URL is correct
```

### API Key errors?
```bash
# Double-check keys in .env
# Make sure Gemini/Twilio APIs are enabled
# Verify API quotas aren't exceeded
```

## File Structure
```
whatsapBot/
├── app.py              # Main Flask app and message handler
├── database.py         # User data and interaction storage
├── utils.py           # Input validation and helpers
├── config.py          # Configuration and nutrition data
├── test_bot.py        # Unit tests
├── setup.py           # First-time setup script
├── requirements.txt   # Python dependencies
├── .env              # Your API keys (create from .env.example)
├── .env.example      # Example credentials
├── Dockerfile        # For containerized deployment
├── docker-compose.yml # Local development with Docker
└── nutrition_bot.db  # SQLite database (auto-created)
```

## Features Explained

### Input Validation
- Only answers nutrition/meal-related questions
- Rejects random queries ("tell me a joke" = rejected)

### Image Analysis
- Users can send meal photos
- AI analyzes what's in the image
- Calculates nutrition automatically

### Health Conditions
- Users mention diabetes, allergies, etc
- Bot remembers and personalizes responses
- Provides safe dietary recommendations

### Data Storage
- All interactions saved in SQLite database
- Used for user history and analytics
- Automatically cleaned after 90 days

## Example Conversations

### Text-based meal:
```
User: I had 2 eggs, toast, and 100g chicken
Bot: 📊 Your meal contains approximately:
     - Calories: 450 kcal
     - Protein: 40g
     - Carbs: 15g
     - Fats: 18g
     
     ✓ Good protein intake for muscle recovery
     ⚠ Consider adding vegetables for fiber
```

### Image-based meal:
```
User: [Sends photo of biryani]
Bot: [Analyzes image]
     I detect: Rice, chicken, onions, spices
     
     Estimated per serving (1 cup):
     - Calories: 380 kcal
     - Protein: 15g
     - Carbs: 38g
     - Fats: 16g
```

### With health condition:
```
User: I'm vegetarian and diabetic, I ate lentil curry
Bot: ✓ Great choice for diabetes management!
     Lentils have low glycemic index
     
     Fiber content helps control blood sugar
     ⚠ Watch portion size - still has carbs
     💡 Pair with vegetables for more nutrients
```

## Next Steps

- **Monitor**: Check `/stats` endpoint for bot analytics
- **Customize**: Edit `config.py` for nutrition thresholds
- **Deploy**: Follow README.md for production deployment
- **Enhance**: Add daily summaries, weekly reports, user analytics

## Need Help?

1. **Check logs**: Look at console output when running app.py
2. **Test webhook**: Use curl or Postman to test `/webhook` endpoint
3. **Review config**: Ensure credentials in .env are correct
4. **Run tests**: `python test_bot.py` to verify installation

## Security Notes

🔒 API keys are stored in `.env` (never commit to git)
🔒 Database is local SQLite (no cloud needed)
🔒 Messages validated before processing
🔒 Only nutrition questions answered

---

**You're all set! Start analyzing meals with AI! 🥗🤖**

# WhatsApp Nutrition Bot - Setup Guide

A WhatsApp bot that analyzes meals (via text or images), calculates calories, macronutrients, and provides personalized dietary recommendations based on health conditions.

## Features

✅ **Meal Analysis**: Users send meal photos or descriptions  
✅ **Nutrition Calculation**: Automatic calorie and macro (protein, carbs, fats) estimation  
✅ **Health Condition Support**: Personalized feedback based on user's health conditions  
✅ **Data Storage**: All interactions stored for historical reference and analytics  
✅ **Image Recognition**: AI-powered meal detection from photos  
✅ **Hallucination Prevention**: Strict filtering to answer only nutrition-related questions  
✅ **Multi-language Support**: Works with various meal names and descriptions  

## Prerequisites

- **Python 3.9+**
- **Twilio Account** (WhatsApp Business API)
- **Google Gemini API Key**
- **Internet Connection**
- **SQLite3** (included with Python)

## Installation

### 1. Clone/Download the Project

```bash
cd c:\Users\shnek\OneDrive\Desktop\Mugunthan\whatsapBot
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env with your credentials
# For Windows: notepad .env
# For Linux/Mac: nano .env
```

### 5. Get API Credentials

#### Twilio Setup:
1. Go to https://www.twilio.com
2. Sign up for a free account
3. Navigate to WhatsApp Sandbox (Console -> Messaging -> Whatsapp)
4. Copy your:
   - Account SID
   - Auth Token
   - WhatsApp Sandbox Number
5. Add these to your `.env` file

#### Google Gemini API Setup:
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the API key
4. Add to your `.env` file as `GEMINI_API_KEY`

### 6. Update .env File

```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155552671
GEMINI_API_KEY=your_gemini_key
DEBUG=False
```

## Running the Bot

### Local Development:

```bash
python app.py
```

The Flask server will start on `http://localhost:5000`

### With Gunicorn (Production):

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Setting Up WhatsApp Webhook

Your Twilo needs to know where to send messages. You need to:

1. **Get a Public URL**:
   - Use **ngrok** for local testing:
   ```bash
   ngrok http 5000
   ```
   - Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
   
   - For production, use your server's domain

2. **Configure Twilio Webhook**:
   - Go to Twilio Console → Messaging → WhatsApp
   - Under "When a message comes in", set the webhook to:
     ```
     https://your-domain.com/webhook
     ```
   - Method: POST
   - Save

3. **Test on Your Phone**:
   - In Twilio WhatsApp Sandbox, find the joining code
   - Send the code from your WhatsApp phone (e.g., "join silly-dog")
   - Start sending meal descriptions or images!

## Usage Examples

### Text Messages:
```
User: I had rice and chicken curry for lunch
Bot: [Analysis with calories, macros, and health suggestions]

User: I'm diabetic, I ate 2 slices of bread with peanut butter
Bot: [Diabetic-friendly analysis with recommendations]

User: Is pizza healthy?
Bot: I can only help with meal analysis. Please describe your pizza...
```

### Image Messages:
```
User: [Sends photo of a meal]
Bot: [Analyzes image and provides nutrition facts]
```

## API Endpoints

### Health Check
```
GET /health
```

### Get Bot Statistics
```
GET /stats
```

### Get User History
```
GET /user/<phone>/history?limit=10
```

### Webhook (for Twilio)
```
POST /webhook
```

## Security Features

🔒 **Input Validation**: Only nutrition-related questions are answered  
🔒 **Hallucination Prevention**: Strict prompt engineering  
🔒 **No PII Storage**: Only phone numbers and meals are stored  
🔒 **Auto-Cleanup**: Old interactions deleted after 90 days  
🔒 **Rate Limiting**: Can be added for production

## Database Schema

### Users Table
- phone_number (PK)
- name
- health_conditions (JSON)
- created_at
- last_interaction
- total_interactions

### Interactions Table
- id (PK)
- phone_number (FK)
- user_input
- bot_response
- health_conditions
- has_image
- timestamp

## Troubleshooting

### Bot not responding?
- Check `.env` file credentials
- Verify ngrok/webhook URL is active
- Check Flask is running on port 5000
- Look at console logs for errors

### Inaccurate nutrition data?
- More detailed meal descriptions help
- Images provide better analysis
- Mention portion sizes for accuracy

### Messages not being sent?
- Verify Twilio rate limits not exceeded
- Check phone number format (should include country code)
- Ensure authentication tokens are valid

## Production Deployment

### Option 1: Heroku
```bash
# Install Heroku CLI
# Login and create app
heroku login
heroku create your-app-name

# Deploy
git push heroku main

# Set environment variables
heroku config:set TWILIO_ACCOUNT_SID=xxx
# ... set other variables
```

### Option 2: AWS EC2
1. Launch Ubuntu instance
2. SSH into instance
3. Clone repository
4. Install Python and dependencies
5. Run with Gunicorn
6. Setup with Nginx as reverse proxy
7. Install SSL certificate

### Option 3: Google Cloud Run
```bash
# Create Dockerfile (provided)
# Build and deploy
gcloud run deploy nutrition-bot --source .
```

## Privacy & Data Retention

- User data is stored in SQLite database
- Interactions older than 90 days are automatically deleted
- No sensitive health information is shared with third parties
- Data is used only for improving meal analysis

## Limitations

⚠️ Estimates are NOT medical advice  
⚠️ AI-based calculations may vary from actual values  
⚠️ Always consult a nutritionist for medical conditions  
⚠️ Image analysis works best with clear, well-lit photos  

## Monitoring & Analytics

Check bot performance:

```bash
curl http://localhost:5000/stats
```

View user interaction history:

```bash
curl http://localhost:5000/user/whatsapp:+91XXXXXXXXXX/history
```

## Support & Issues

For bugs or questions:
1. Check logs in console
2. Review .env configuration
3. Test webhook URL with curl
4. Verify API credentials are active

## License

This project is provided as-is for educational purposes.

---

**Happy meal tracking! 🥗📱**

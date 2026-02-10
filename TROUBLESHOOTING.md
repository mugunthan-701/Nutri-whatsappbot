# WhatsApp Nutrition Bot - Troubleshooting Guide

## Common Issues & Solutions

---

## Setup Issues

### 1. Python Version Error
**Error:** `Python 3.9+ required`

**Solution:**
```bash
# Check Python version
python --version

# If outdated, download from https://www.python.org
# Then verify installation
python --version
```

### 2. Virtual Environment Not Activating
**Error:** Command not found or environment not activated

**Windows:**
```bash
# Make sure you're in the correct directory
cd c:\Users\shnek\OneDrive\Desktop\Mugunthan\whatsapBot

# Activate venv
venv\Scripts\activate

# You should see (venv) in your prompt
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Dependencies Installation Fails
**Error:** `pip: command not found` or permission denied

**Solution:**
```bash
# Ensure pip is upgraded
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# If still fails, try with --user flag
pip install --user -r requirements.txt
```

### 4. Requirements Installation Hangs
**Error:** Installation takes too long or freezes

**Solution:**
```bash
# Clear pip cache
pip cache purge

# Install with timeout
pip install --default-timeout=1000 -r requirements.txt

# Or install packages one by one
pip install Flask==2.3.0
pip install Flask-CORS==4.0.0
# ... continue for other packages
```

---

## API Key Issues

### 1. Twilio Keys Not Working
**Error:** `TwilioRestException: [31001] Authentication required`

**Solution:**
1. Verify credentials in `.env` file:
```bash
# Check these values
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_actual_token_here
```

2. Test credentials:
```python
from twilio.rest import Client
import os

client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
print(client.api.accounts.get())  # Should return account info
```

3. Re-generate keys if unsure:
   - Go to https://www.twilio.com/console
   - Copy fresh credentials

### 2. Gemini API Key Invalid
**Error:** `google.auth.exceptions.DefaultCredentialsError`

**Solution:**
1. Verify `GEMINI_API_KEY` in `.env`
2. Check API is enabled: https://makersuite.google.com/app/apikey
3. Create new key if needed
4. Test API:
```python
import google.generativeai as genai
genai.configure(api_key="your_key")
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("test")
print(response.text)
```

### 3. API Keys in Wrong Format
**Error:** 401 Unauthorized errors

**Solution:**
- Remove quotes from `.env` if present:
```bash
# WRONG:
TWILIO_ACCOUNT_SID="ACxxxxx"

# RIGHT:
TWILIO_ACCOUNT_SID=ACxxxxx
```

---

## Bot Not Responding

### 1. Flask Not Running
**Error:** Connection refused on `http://localhost:5000`

**Solution:**
```bash
# Make sure you're in the correct directory
cd c:\Users\shnek\OneDrive\Desktop\Mugunthan\whatsapBot

# Ensure virtual environment is activated
venv\Scripts\activate

# Start Flask
python app.py

# Should see: * Running on http://127.0.0.1:5000
```

### 2. Webhook Not Configured
**Error:** Bot receives nothing from WhatsApp

**Solution:**
1. Get ngrok URL:
```bash
ngrok http 5000
# You'll see: Forwarding    https://abc123.ngrok.io -> http://localhost:5000
```

2. Update Twilio Webhook:
   - Go to Twilio Console → Messaging → WhatsApp
   - Find "When a message comes in"
   - Set URL to: `https://abc123.ngrok.io/webhook`
   - Method: POST
   - Save

3. Verify webhook is live:
```bash
curl https://abc123.ngrok.io/health
```

### 3. Messages Not Reaching Twilio
**Error:** User message, but no bot response

**Solution:**
1. Check user joined sandbox:
   - Send "join [join-word]" from WhatsApp (e.g., "join silly-dog")
   - Wait for confirmation

2. Check Twilio logs:
   - Console → Messaging → WhatsApp → Logs
   - Look for your message

3. Test webhook manually:
```bash
curl -X POST http://localhost:5000/webhook \
  -d "Body=test&From=whatsapp:+919876543210&ProfileName=Test&NumMedia=0"
```

### 4. Port 5000 Already in Use
**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 5000
# Windows
netstat -ano | findstr :5000
# Kill the process
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Or use different port
flask run --port 5001
```

---

## Image Processing Issues

### 1. Images Not Being Analyzed
**Error:** Image sent but bot ignores it

**Solution:**
1. Check image format:
   - Supported: JPEG, PNG, WebP
   - File size: < 5 MB
   - Quality: Clear and well-lit

2. Verify Gemini handles images:
```python
import google.generativeai as genai
from PIL import Image
import io

genai.configure(api_key="your_key")
model = genai.GenerativeModel('gemini-1.5-flash')

# Test with local image
img = Image.open('test_meal.jpg')
response = model.generate_content([
    "Analyze this meal",
    img
])
print(response.text)
```

### 2. Image Download Fails
**Error:** `Error downloading media`

**Solution:**
1. Check Twilio credits (required for media)
2. Ensure image URL is accessible:
```bash
curl -v <image_url> \
  --basic --user <ACCOUNT_SID>:<AUTH_TOKEN>
```

3. Check internet connection
4. Verify file permissions

---

## Database Issues

### 1. Database Locked
**Error:** `database is locked`

**Solution:**
```bash
# SQLite doesn't support concurrent access well
# Add timeout to connection
# In database.py, modify connection:

conn = sqlite3.connect(self.db_path, timeout=10.0)
```

### 2. Database Corrupted
**Error:** `database disk image is malformed`

**Solution:**
```bash
# Backup and recreate
cp nutrition_bot.db nutrition_bot.db.backup
rm nutrition_bot.db

# Restart app - will create fresh database
python app.py
```

### 3. Out of Disk Space
**Error:** `No space left on device`

**Solution:**
```bash
# Check disk usage
df -h

# Clean old interactions (keep last 30 days)
python -c "from database import Database; db = Database(); db.delete_old_interactions(30)"

# Delete old log files
rm *.log
```

---

## Performance Issues

### 1. Slow Response Time
**Error:** Bot takes >10 seconds to respond

**Solution:**
1. Check Gemini API limits:
   - Free tier: 60 requests per minute
   - Paid: Higher limits

2. Add caching:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def analyze_common_meals(meal):
    # Cache results for frequent meals
    pass
```

3. Increase workers:
```bash
gunicorn -w 8 -b 0.0.0.0:5000 app:app
```

### 2. High CPU Usage
**Error:** CPU running at 100%

**Solution:**
1. Check for infinite loops in code
2. Monitor logs for errors
3. Use fewer workers:
```bash
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

### 3. Memory Leaks
**Error:** Memory keeps increasing

**Solution:**
```python
# Monitor memory usage
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024} MB")

# Restart app periodically
# Add to crontab: 0 */6 * * * systemctl restart nutrition-bot
```

---

## Gemini AI Issues

### 1. Hallucination (Wrong Answers)
**Error:** Bot makes up information

**Solution:**
1. Review system prompt in `app.py`:
```python
SYSTEM_PROMPT = """You are a nutrition and meal analysis assistant..."""
```

2. Lower temperature (more conservative):
```python
generation_config=genai.types.GenerationConfig(
    temperature=0.1,  # Lower = less creative
    top_p=0.8,
    top_k=40,
)
```

3. Add explicit instructions:
```python
prompt = """Only analyze meals and nutrition.
Do NOT answer non-nutrition questions.
If unsure, say "I cannot determine this."
"""
```

### 2. Bot Answers Non-Nutrition Questions
**Error:** "Tell me a joke" → bot responds

**Solution:**
1. Check `is_nutrition_related()` function
2. Add person's name filtering:
```python
if not is_nutrition_related(message):
    send_whatsapp_message(user_phone, "I only help with meals")
    return
```

3. Test validation:
```bash
python test_bot.py
```

### 3. API Rate Limit Exceeded
**Error:** `429 Too Many Requests`

**Solution:**
1. Implement exponential backoff:
```python
import time
import random

def call_gemini_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
```

2. Cache common meals:
```python
MEAL_CACHE = {
    "rice and chicken": "Calories: ~450, Protein: 25g...",
}
```

---

## Twilio Issues

### 1. WhatsApp Sandbox Expired
**Error:** Messages don't go through after 72 hours inactivity

**Solution:**
1. Rejoin sandbox: Send "join [word]"
2. Or set up production account with Business API

### 2. Message Rate Limited
**Error:** Too many messages sent quickly

**Solution:**
1. Check Twilio account status
2. Upgrade account tier
3. Add message queue:
```python
from queue import Queue
import threading

msg_queue = Queue()

def send_messages():
    while True:
        msg = msg_queue.get()
        send_whatsapp_message(msg['to'], msg['body'])
        time.sleep(1)  # One per second
```

### 3. Webhook Signature Invalid
**Error:** `Invalid request signature`

**Solution:**
1. Verify X-Twilio-Signature header
2. Add validation:
```python
from twilio.request_validator import RequestValidator

validator = RequestValidator(os.getenv('TWILIO_AUTH_TOKEN'))
if not validator.validate(request.url, request.form, 
                         request.headers.get('X-Twilio-Signature')):
    return "Forbidden", 403
```

---

## Deployment Issues

### 1. Heroku Deployment Fails
**Error:** Build error

**Solution:**
1. Check Procfile exists
2. Ensure requirements.txt is up to date
3. Check for Python syntax errors
4. View Heroku logs: `heroku logs --tail`

### 2. Docker Build Fails
**Error:** `failed to solve with frontend dockerfile`

**Solution:**
```bash
# Check Dockerfile syntax
docker build -t nutrition-bot .

# If error, remove cached build
docker build --no-cache -t nutrition-bot .

# Test locally
docker run -p 5000:5000 nutrition-bot
```

### 3. SSL Certificate Issues
**Error:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Solution:**
```python
import ssl
import urllib.request

ssl._create_default_https_context = ssl._create_unverified_context

# Or for requests library
import requests
requests.get(url, verify=False)
```

---

## Testing & Validation

### 1. Test All Functionality
```bash
# Run unit tests
python test_bot.py

# Test webhook manually
curl -X POST http://localhost:5000/webhook \
  -d "Body=I+ate+rice&From=whatsapp:+919876543210&ProfileName=Test&NumMedia=0"

# Test health endpoint
curl http://localhost:5000/health

# Test stats endpoint
curl http://localhost:5000/stats
```

### 2. Validate Configuration
```bash
# Check .env file
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('TWILIO_ACCOUNT_SID'))"

# Verify database
python -c "from database import Database; db = Database(); print(db.get_statistics())"
```

---

## Getting Help

### 1. Enable Debug Logging
```bash
# In .env
DEBUG=True
LOG_LEVEL=DEBUG

# Or in app.py
logging.basicConfig(level=logging.DEBUG)
```

### 2. Check Logs
```bash
# View application logs
tail -f nutrition_bot.log

# View specific errors
grep ERROR nutrition_bot.log

# View Twilio logs
# Go to Twilio Console → Logs
```

### 3. Test with Postman
1. Download Postman
2. Create POST request to `http://localhost:5000/webhook`
3. Add form data:
   - Body: `I ate rice`
   - From: `whatsapp:+919876543210`
   - ProfileName: `Test`
   - NumMedia: `0`

### 4. Contact Support
- Twilio Support: https://www.twilio.com/help
- Google Support: https://support.google.com
- GitHub Issues: Check repository issues

---

## Quick Diagnostic Commands

```bash
# Check Python
python --version

# Check Flask
pip show Flask

# Check Twilio connectivity
python -c "from twilio.rest import Client; print('OK')"

# Check Gemini connectivity
python -c "import google.generativeai; print('OK')"

# Check database
python -c "from database import Database; Database()"

# Check port usage
netstat -ano | findstr :5000  # Windows
lsof -i :5000  # Linux/Mac

# Test webhook
curl http://localhost:5000/health
```

---

## Still Having Issues?

1. **Check README.md** - General information
2. **Check API.md** - API endpoint details
3. **Run QUICKSTART.md** - Step-by-step setup
4. **Run tests** - `python test_bot.py`
5. **Check logs** - Look for error messages
6. **Enable debug** - Set DEBUG=True in .env

---

**Still stuck? Enable full debug logging and check the console output carefully. Most issues are API key or configuration-related! 🔍**

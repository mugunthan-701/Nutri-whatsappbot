# WhatsApp Nutrition Bot - API Documentation

## Base URL
```
http://localhost:5000
```

---

## Endpoints

### 1. Webhook (Message Handler)

**Endpoint:** `POST /webhook`

**Purpose:** Receives incoming WhatsApp messages from Twilio

**Parameters:**
- `Body` (string): User's message text
- `From` (string): User's WhatsApp phone (format: `whatsapp:+<country_code><number>`)
- `ProfileName` (string): User's WhatsApp display name
- `NumMedia` (integer): Number of media files attached
- `MediaUrl0` (string): URL of first media file
- `MediaContentType0` (string): MIME type of media

**Response:**
```json
{
  "status": "OK"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/webhook \
  -d "Body=I+ate+rice&From=whatsapp:+919876543210&ProfileName=User&NumMedia=0"
```

**Status Codes:**
- `200`: Message processed successfully
- `400`: Invalid input
- `500`: Server error

---

### 2. Health Check

**Endpoint:** `GET /health`

**Purpose:** Verify bot is running

**Response:**
```json
{
  "status": "healthy"
}
```

**Example:**
```bash
curl http://localhost:5000/health
```

---

### 3. Bot Statistics

**Endpoint:** `GET /stats`

**Purpose:** Get overall bot metrics

**Response:**
```json
{
  "total_users": 150,
  "total_interactions": 2500,
  "active_users_7d": 45,
  "avg_interactions_per_user": 16.67,
  "timestamp": "2026-02-09T15:30:00"
}
```

**Example:**
```bash
curl http://localhost:5000/stats
```

---

### 4. User History

**Endpoint:** `GET /user/<phone>/history`

**Parameters:**
- `phone` (path): User's WhatsApp number (format: `whatsapp:+919876543210`)
- `limit` (query, optional): Number of interactions to return (default: 10, max: 100)

**Response:**
```json
{
  "history": [
    {
      "id": 1,
      "user_input": "I ate rice and chicken",
      "bot_response": "📊 Nutritional Summary: ...",
      "has_image": false,
      "timestamp": "2026-02-09T14:20:00",
      "health_conditions": ["diabetes"]
    },
    {
      "id": 2,
      "user_input": "[Image of meal]",
      "bot_response": "Analysis of meal: ...",
      "has_image": true,
      "timestamp": "2026-02-09T13:15:00",
      "health_conditions": []
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:5000/user/whatsapp:+919876543210/history?limit=20
```

**Status Codes:**
- `200`: Success
- `404`: User not found
- `500`: Server error

---

## WebHook Format Details

### Incoming Message Format
Twilio sends the following POST data:

```
MessageSid=SM...
AccountSid=AC...
From=whatsapp:+919876543210
To=whatsapp:+14155552671
Body=I+ate+rice+for+lunch
NumMedia=0
MessageStatus=received
ProfileName=Rohit
MediaContentType0=image/jpeg
MediaUrl0=https://media.twiliocdn.com/...
```

### Response Format
Your webhook should always respond with `OK` status 200. If error, respond with 500 to trigger Twilio retry.

---

## Data Models

### User Profile
```json
{
  "phone_number": "whatsapp:+919876543210",
  "name": "Rohit",
  "health_conditions": ["diabetes", "vegan"],
  "created_at": "2026-02-01T10:30:00",
  "last_interaction": "2026-02-09T14:20:00",
  "total_interactions": 45
}
```

### Interaction Record
```json
{
  "id": 1,
  "phone_number": "whatsapp:+919876543210",
  "user_input": "I ate rice and curry",
  "bot_response": "Your meal contains approximately...",
  "health_conditions": ["diabetes"],
  "has_image": false,
  "calories": 450,
  "protein": 25.5,
  "carbs": 60.0,
  "fats": 15.3,
  "timestamp": "2026-02-09T14:20:00"
}
```

### Nutrition Analysis Response
```json
{
  "meal_items": ["rice", "chicken curry"],
  "total_calories": 450,
  "nutrients": {
    "protein_g": 25.5,
    "carbohydrates_g": 60.0,
    "fats_g": 15.3,
    "fiber_g": 2.0,
    "sodium_mg": 800
  },
  "health_assessment": {
    "is_healthy": true,
    "notes": "Good protein content for diabetes management",
    "recommendations": ["Add vegetables for more fiber", "Watch portion size"]
  }
}
```

---

## Error Responses

### Invalid Input
```json
{
  "error": "Please provide meal details (text or image) for analysis.",
  "code": "INVALID_INPUT"
}
```

### Non-Nutrition Question
```json
{
  "error": "I can only help with meal analysis and nutrition advice. Please describe your meal or ask about your diet.",
  "code": "OFF_TOPIC"
}
```

### API Error
```json
{
  "error": "Failed to analyze meal",
  "code": "ANALYSIS_ERROR"
}
```

---

## Authentication

**Note:** Currently, the webhook does not require API key authentication (assumes Twilio provides security). For production, add Bearer token:

```python
@app.route('/webhook', methods=['POST'])
def webhook():
    auth_header = request.headers.get('Authorization')
    if not auth_header.startswith('Bearer '):
        return "Unauthorized", 401
    
    token = auth_header[7:]
    if token != os.getenv('API_KEY'):
        return "Forbidden", 403
```

---

## Rate Limiting

Current Implementation:
- 20 requests per minute per phone number (configurable in `config.py`)
- 1000 requests per hour per service

Future: Add Redis for distributed rate limiting

---

## Pagination

Use `limit` parameter to paginate results:

```bash
# Get first 10 interactions
curl http://localhost:5000/user/whatsapp:+919876543210/history?limit=10

# Get more recent interactions
curl http://localhost:5000/user/whatsapp:+919876543210/history?limit=20
```

---

## Response Headers

```
Content-Type: application/json
Access-Control-Allow-Origin: *
X-Request-ID: unique-request-id
Cache-Control: no-cache
```

---

## Webhook Testing

### Using cURL
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Body=I+had+rice+for+lunch&From=whatsapp:+919876543210&ProfileName=TestUser&NumMedia=0"
```

### Using Postman
1. Set method to POST
2. URL: `http://localhost:5000/webhook`
3. Body (form-data):
   - `Body`: `I ate rice`
   - `From`: `whatsapp:+919876543210`
   - `ProfileName`: `TestUser`
   - `NumMedia`: `0`

### Using Python
```python
import requests

url = "http://localhost:5000/webhook"
data = {
    "Body": "I ate chicken and rice",
    "From": "whatsapp:+919876543210",
    "ProfileName": "TestUser",
    "NumMedia": "0"
}

response = requests.post(url, data=data)
print(response.status_code, response.text)
```

---

## Async Operations

To handle heavy image processing, consider using Celery:

```python
from celery import Celery

celery = Celery(app.name)

@celery.task
def analyze_meal_async(image_data, user_phone):
    # Heavy processing
    result = analyze_meal_with_gemini(image_data, [])
    send_whatsapp_message(user_phone, result)
```

---

## Database Queries

### SQL for Custom Reports

```sql
-- Top meals analyzed
SELECT user_input, COUNT(*) as frequency 
FROM interactions 
GROUP BY user_input 
ORDER BY frequency DESC 
LIMIT 10;

-- Average calories per user
SELECT phone_number, AVG(calories) as avg_calories 
FROM interactions 
WHERE calories IS NOT NULL 
GROUP BY phone_number;

-- Health condition distribution
SELECT health_conditions, COUNT(*) as count 
FROM interactions 
GROUP BY health_conditions;
```

---

## Webhook Security

### Twilio Request Validation
```python
from twilio.request_validator import RequestValidator

@app.route('/webhook', methods=['POST'])
def webhook():
    validator = RequestValidator(os.getenv('TWILIO_AUTH_TOKEN'))
    
    if not validator.validate(
        request.url,
        request.form,
        request.headers.get('x-twilio-signature')
    ):
        return "Forbidden", 403
```

### Rate Limiting with Flask-Limiter
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.form.get('From'))

@app.route('/webhook', methods=['POST'])
@limiter.limit("20 per minute")
def webhook():
    pass
```

---

## Extending the API

### Add Custom Endpoint
```python
@app.route('/meal-analysis', methods=['POST'])
def custom_meal_analysis():
    data = request.get_json()
    meal = data.get('meal')
    conditions = data.get('health_conditions', [])
    
    result = analyze_meal_with_gemini(meal, None, conditions)
    return {"analysis": result}, 200
```

### Add Database Query Endpoint
```python
@app.route('/user/<phone>/stats', methods=['GET'])
def get_user_stats(phone):
    stats = db.get_user_stats(phone, days=7)
    return stats, 200
```

---

## Version Management

Current Version: `1.0.0`

For future versions:
```
/api/v1/webhook
/api/v1/stats
/api/v2/webhook (with new features)
```

---

## Support & Debugging

### Enable Debug Mode
```python
# In app.py
app.run(debug=True)

# Or in .env
DEBUG=True
```

### Check Logs
```bash
# Real-time logs
tail -f nutrition_bot.log

# All errors
grep ERROR nutrition_bot.log
```

### Test Endpoint Availability
```bash
curl -v http://localhost:5000/health
```

---

**API Documentation Complete! 📚**

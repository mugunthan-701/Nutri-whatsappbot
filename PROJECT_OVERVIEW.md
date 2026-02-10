# WhatsApp Nutrition Bot - Complete Project Overview

## 📱 Project Summary

A WhatsApp bot powered by Google Gemini AI that analyzes meals (via text or images), calculates nutritional information, and provides personalized dietary recommendations based on user health conditions.

**Key Features:**
- 🤖 AI-powered meal analysis using Google Gemini
- 📸 Image recognition for meal detection
- 📊 Automatic calorie and macro calculation
- 🏥 Health condition-aware recommendations
- 💾 Complete user data persistence
- 🔒 Hallucination prevention (nutrition-only responses)
- 📈 User analytics and tracking

---

## 🏗️ Project Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   WhatsApp User                         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ (WhatsApp Message)
                       ↓
        ┌──────────────────────────────┐
        │    Twilio WhatsApp API       │
        │  (Message Relay Service)     │
        └──────────────┬───────────────┘
                       │
                       │ (HTTP POST)
                       ↓
        ┌──────────────────────────────┐
        │   Flask Web Application      │
        │  (app.py - Main Handler)     │
        │  - Message validation        │
        │  - Input sanitization        │
        │  - User management           │
        └──────────────┬───────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
          ↓            ↓            ↓
    ┌──────────┐  ┌────────────┐  ┌─────────────┐
    │ Database │  │ Gemini API │  │   Utils &   │
    │(SQLite)  │  │  (AI Core) │  │   Helpers   │
    │- Users   │  │- Analysis  │  │- Validation │
    │- History │  │- Image ML  │  │- Filtering  │
    └──────────┘  └────────────┘  └─────────────┘
          │            │            │
          └────────────┼────────────┘
                       │
                       ↓
        ┌──────────────────────────────┐
        │  Response Message            │
        └──────────────┬───────────────┘
                       │
                       ↓
        ┌──────────────────────────────┐
        │    Twilio WhatsApp API       │
        └──────────────┬───────────────┘
                       │
                       ↓
                   WhatsApp User
```

---

## 📁 File Structure & Description

```
whatsapBot/
│
├── app.py                          # Main Flask application
│   ├── Webhook handler
│   ├── Message processor
│   ├── Image handler
│   ├── Gemini integration
│   └── WhatsApp response sender
│
├── database.py                     # SQLite database layer
│   ├── User profile management
│   ├── Interaction storage
│   ├── Analytics queries
│   └── Data retention policies
│
├── utils.py                        # Utility functions
│   ├── Input validation
│   ├── Nutrition keyword detection
│   ├── Health condition extraction
│   ├── Input sanitization
│   └── Message formatting
│
├── config.py                       # Configuration & constants
│   ├── Nutrition lookup tables
│   ├── Health condition guidance
│   ├── Gemini parameters
│   └── Feature flags
│
├── test_bot.py                     # Unit tests
│   ├── Validation tests
│   ├── Database tests
│   ├── Nutrition detection tests
│   └── Hallucination prevention tests
│
├── setup.py                        # First-time setup script
│   ├── Environment check
│   ├── Dependency installation
│   ├── Configuration validation
│   └── Test execution
│
├── Dockerfile                      # Container configuration
├── docker-compose.yml              # Local development stack
│
├── requirements.txt                # Python dependencies
├── .env.example                    # Example environment variables
├── .gitignore                      # Git ignore patterns
│
├── README.md                       # Main documentation
├── QUICKSTART.md                   # 5-minute setup guide
├── DEPLOYMENT.md                   # Cloud deployment guide
├── API.md                          # API documentation
├── TROUBLESHOOTING.md              # Common issues & solutions
│
└── nutrition_bot.db                # SQLite database (auto-created)
    └── Queries: users, interactions, daily_intake
```

---

## 🔄 Message Flow

### 1. User Sends Text Message
```
User: "I ate rice and chicken for lunch"
         │
         ↓
   Twilio Receives
         │
         ↓
   POST /webhook (Flask app)
         │
         ├→ Extract message & user info
         ├→ Validate input (not empty)
         ├→ Check if nutrition-related
         ├→ Extract health conditions mentioned
         ├→ Query Gemini AI for analysis
         ├→ Store interaction in database
         └→ Send response via WhatsApp
         ↓
   Bot: "📊 Nutritional Summary:
         - Calories: 450 kcal
         - Protein: 25g
         - Carbs: 45g
         - Fats: 15g"
```

### 2. User Sends Image
```
User: [Food photo]
         │
         ↓
   Twilio Receives
         │
         ↓
   POST /webhook (Flask app)
         │
         ├→ Download image from Twilio
         ├→ Validate image (type, size)
         ├→ Send to Gemini for analysis
         ├→ Extract nutrition info
         ├→ Store with user profile
         └→ Send analysis response
         ↓
   Bot: "I detected: Samosa (fried)
         Approximate: 270 cal, 5g protein..."
```

### 3. Hallucination Prevention
```
User: "Tell me a joke"
         │
         ↓
   /webhook processes
         │
         ├→ Check if nutrition-related
         └→ NOT nutrition → REJECT
         ↓
   Bot: "I can only help with meal analysis.
         Please describe your meal..."
```

---

## 🧠 Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Framework | Flask 2.3.0 | Web server & webhook handler |
| AI/ML | Google Gemini | Meal analysis & recommendations |
| WhatsApp | Twilio SDK | Message routing & delivery |
| Database | SQLite3 | User data persistence |
| Image Processing | Pillow | Image validation & handling |
| HTTP | Requests | API communication |
| Validation | Custom filters | Input validation & hallucination prevention |

---

## 🔐 Security Measures

1. **Input Validation**
   - Only nutrition-related questions answered
   - Injection prevention via sanitization
   - Message length limits enforced

2. **API Security**
   - Credentials in .env (not in code)
   - Webhook validation (Twilio signature)
   - Rate limiting on requests

3. **Data Security**
   - Local SQLite (no cloud exposure)
   - Auto-deletion of old data (90 days)
   - No sensitive medical data stored
   - HTTPS-only on production

4. **AI Safety**
   - System prompt restricts responses
   - Low temperature setting (less creative, more factual)
   - Explicit instruction to refuse non-nutrition questions

---

## 📊 Data Models

### User Table
```sql
CREATE TABLE users (
    phone_number TEXT PRIMARY KEY,
    name TEXT,
    health_conditions TEXT,  -- JSON array
    created_at TIMESTAMP,
    last_interaction TIMESTAMP,
    total_interactions INTEGER
)
```

### Interactions Table
```sql
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY,
    phone_number TEXT,
    user_input TEXT,
    bot_response TEXT,
    health_conditions TEXT,  -- JSON array
    has_image BOOLEAN,
    calories REAL,
    protein REAL,
    carbs REAL,
    fats REAL,
    timestamp TIMESTAMP
)
```

---

## 🚀 Quick Start (for developers)

### 1. Setup
```bash
cd c:\Users\shnek\OneDrive\Desktop\Mugunthan\whatsapBot
python setup.py
```

### 2. Configure
```bash
cp .env.example .env
# Add your API keys
```

### 3. Run
```bash
venv\Scripts\activate
python app.py
```

### 4. Test
```bash
python test_bot.py
```

---

## 🌐 Deployment Options

| Platform | Cost | Setup Time | Recommended |
|----------|------|-----------|-------------|
| Heroku | $50+/mo | 5 min | Quick testing |
| Google Cloud Run | Pay-per-use | 10 min | ⭐ Best for this project |
| Docker VPS | $5-20/mo | 20 min | Full control |
| AWS Lambda | Pay-per-use | 15 min | High traffic |
| Azure | $13+/mo | 10 min | Enterprise |

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides.

---

## 📈 Analytics

The bot tracks:
- Total users
- Total interactions
- Active users (7-day window)
- Average interactions per user
- User nutrition patterns
- Health condition distribution

Access via:
```bash
curl http://localhost:5000/stats
curl http://localhost:5000/user/<phone>/history
```

---

## 🧪 Testing Coverage

Tests include:
- ✅ Input validation
- ✅ Nutrition keyword detection
- ✅ Health condition extraction
- ✅ Database operations
- ✅ Message sanitization
- ✅ Hallucination prevention
- ✅ Response formatting

Run: `python test_bot.py`

---

## 🔧 Configuration Options

Edit `config.py` to customize:
- Caloric intake recommendations
- Macro nutrient ratios
- Health condition guidance
- Gemini AI parameters
- Data retention policies
- Feature flags

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Main documentation & setup |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute quick start |
| [API.md](API.md) | API endpoints & data models |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Cloud deployment guides |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues & solutions |

---

## 🎯 Use Cases

### 1. Personal Health Tracking
Users monitor their daily nutrition intake and receive personalized feedback

### 2. Dietary Management
Support for diabetes, heart disease, celiac, veganism, etc.

### 3. Fitness Tracking
Track macro intake for muscle building or weight loss

### 4. Health Education
Learn about nutrition as you eat

### 5. Family Wellness
Parents monitor children's eating habits

---

## 🛣️ Future Enhancements

Potential features to add:
- [ ] Daily/weekly nutrition summaries
- [ ] Goal setting (calorie/macro targets)
- [ ] Meal planning recommendations
- [ ] Integration with fitness apps
- [ ] Multi-language support
- [ ] Voice commands
- [ ] Recipe suggestions
- [ ] Barcode scanning
- [ ] Grocery list generation
- [ ] Community sharing (anonymized)

---

## 📞 Support & Contact

### Getting Help
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) first
2. Review logs: `nutrition_bot.log`
3. Run tests: `python test_bot.py`
4. Enable debug: `DEBUG=True` in `.env`

### API Support
- Twilio: https://www.twilio.com/help
- Google Gemini: https://support.google.com

---

## 📝 License

This project is provided as-is for educational purposes.

---

## 🙏 Acknowledgments

- **Twilio** - WhatsApp messaging platform
- **Google** - Gemini AI API
- **Flask** - Web framework
- **Python** - Programming language

---

## 📊 Project Statistics

- **Lines of Code**: ~2000+
- **Test Coverage**: 15+ test cases
- **API Endpoints**: 4 main endpoints
- **Database Tables**: 3 tables
- **Documentation**: 5 guides
- **Configuration Options**: 50+ settings

---

## 🚦 Getting Started

### For Users:
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Get API keys
3. Run setup.py
4. Start analyzing meals!

### For Developers:
1. Review project structure above
2. Read [API.md](API.md)
3. Check test_bot.py for examples
4. Run tests and start extending!

### For DevOps:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md)
2. Choose deployment platform
3. Follow platform-specific guide
4. Monitor with provided endpoints

---

**Project created with ❤️ for nutrition tracking on WhatsApp**

---

## 📋 Checklist Before Launch

- [ ] API keys obtained (Twilio, Gemini)
- [ ] .env file configured
- [ ] Setup script completed
- [ ] Unit tests passing
- [ ] Bot responds to test messages
- [ ] Images are being analyzed correctly
- [ ] Database is storing interactions
- [ ] Webhook is receiving messages
- [ ] Health condition filtering works
- [ ] Hallucination prevention active

---

**Ready to launch! 🚀🥗📱**

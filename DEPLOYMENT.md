# Deployment Guide - WhatsApp Nutrition Bot

## Overview

This guide covers deploying your WhatsApp nutrition bot to various cloud platforms.

---

## 1. Heroku Deployment (Easiest)

### Prerequisites
- Heroku Account (free tier available)
- Heroku CLI installed
- Git installed

### Steps

1. **Create Heroku App**
```bash
heroku login
heroku create your-nutrition-bot
```

2. **Add Procfile** (create file `Procfile`)
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
```

3. **Add runtime.txt** (create file `runtime.txt`)
```
python-3.11.7
```

4. **Set Environment Variables**
```bash
heroku config:set TWILIO_ACCOUNT_SID=your_sid
heroku config:set TWILIO_AUTH_TOKEN=your_token
heroku config:set TWILIO_WHATSAPP_NUMBER=whatsapp:+...
heroku config:set GEMINI_API_KEY=your_key
heroku config:set FLASK_ENV=production
```

5. **Deploy**
```bash
git push heroku main
```

6. **Update Twilio Webhook**
```
https://your-nutrition-bot.herokuapp.com/webhook
```

### Monitor
```bash
heroku logs --tail
```

---

## 2. Google Cloud Run (Recommended)

### Prerequisites
- Google Cloud Account
- gcloud CLI installed
- Docker installed

### Steps

1. **Create Dockerfile** (already provided)

2. **Build Image**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/nutrition-bot
```

3. **Deploy**
```bash
gcloud run deploy nutrition-bot \
  --image gcr.io/YOUR_PROJECT_ID/nutrition-bot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

4. **Set Environment Variables**
```bash
gcloud run services update nutrition-bot \
  --set-env-vars TWILIO_ACCOUNT_SID=xxx,TWILIO_AUTH_TOKEN=yyy...
```

5. **Get URL**
```bash
gcloud run services describe nutrition-bot --region us-central1
```

6. **Update Twilio Webhook**
```
https://your-service-url/webhook
```

### Monitor
```bash
gcloud run services describe nutrition-bot
gcloud logging read "resource.type=cloud_run_revision"
```

---

## 3. AWS Lambda + API Gateway

### Prerequisites
- AWS Account
- AWS CLI configured
- SAM CLI (optional)

### Steps

1. **Create Lambda Function**
   - Runtime: Python 3.11
   - Handler: app.app

2. **Package Dependencies**
```bash
pip install -r requirements.txt -t package
cp app.py database.py utils.py config.py package/
cd package && zip -r ../lambda_function.zip . && cd ..
```

3. **Upload to Lambda**
```bash
aws lambda update-function-code \
  --function-name nutrition-bot \
  --zip-file fileb://lambda_function.zip
```

4. **Add API Gateway Trigger**
   - Create HTTP API
   - Set POST method for `/webhook`

5. **Set Environment Variables**
```bash
aws lambda update-function-configuration \
  --function-name nutrition-bot \
  --environment Variables={TWILIO_ACCOUNT_SID=xxx,...}
```

6. **Update Twilio Webhook**
```
https://your-api-gateway-url/webhook
```

---

## 4. Azure App Service

### Prerequisites
- Azure Account
- Azure CLI installed

### Steps

1. **Create Resource Group**
```bash
az group create --name nutrition-bot-rg --location eastus
```

2. **Create App Service Plan**
```bash
az appservice plan create \
  --name nutrition-bot-plan \
  --resource-group nutrition-bot-rg \
  --sku B1 \
  --is-linux
```

3. **Create Web App**
```bash
az webapp create \
  --resource-group nutrition-bot-rg \
  --plan nutrition-bot-plan \
  --name nutrition-bot-app \
  --runtime "PYTHON|3.11"
```

4. **Deploy Code**
```bash
az webapp up --name nutrition-bot-app --resource-group nutrition-bot-rg
```

5. **Set Environment Variables**
```bash
az webapp config appsettings set \
  --resource-group nutrition-bot-rg \
  --name nutrition-bot-app \
  --settings \
    TWILIO_ACCOUNT_SID=xxx \
    TWILIO_AUTH_TOKEN=yyy \
    GEMINI_API_KEY=zzz
```

6. **Get URL and Update Twilio**
```
https://nutrition-bot-app.azurewebsites.net/webhook
```

---

## 5. DigitalOcean App Platform

### Prerequisites
- DigitalOcean Account
- GitHub repository

### Steps

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Create App on DigitalOcean**
   - Go to App Platform
   - Select GitHub repository
   - Choose Python as runtime
   - Set HTTP port to 5000

3. **Add Environment Variables**
   - TWILIO_ACCOUNT_SID
   - TWILIO_AUTH_TOKEN
   - TWILIO_WHATSAPP_NUMBER
   - GEMINI_API_KEY

4. **Deploy**
   - Click "Create App"
   - Wait for deployment

5. **Get URL and Update Twilio**
```
https://your-app.ondigitalocean.app/webhook
```

---

## 6. Docker Deployment (Any VPS)

### Prerequisites
- Server with Docker installed (Ubuntu/CentOS)
- SSH access to server

### Steps

1. **Build Image**
```bash
docker build -t nutrition-bot:latest .
```

2. **Push to Docker Registry** (optional)
```bash
docker tag nutrition-bot:latest your-username/nutrition-bot:latest
docker push your-username/nutrition-bot:latest
```

3. **Run on Server**
```bash
docker run -d \
  -p 5000:5000 \
  -e TWILIO_ACCOUNT_SID=xxx \
  -e TWILIO_AUTH_TOKEN=yyy \
  -e TWILIO_WHATSAPP_NUMBER=whatsapp:+... \
  -e GEMINI_API_KEY=zzz \
  --restart always \
  --name nutrition-bot nutrition-bot:latest
```

4. **Setup Nginx Reverse Proxy**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

5. **Add SSL with Let's Encrypt**
```bash
sudo certbot certonly --standalone -d your-domain.com
```

6. **Update Twilio Webhook**
```
https://your-domain.com/webhook
```

---

## 7. Render.com (Simple & Free)

### Prerequisites
- Render Account
- GitHub repository

### Steps

1. **Create Web Service**
   - Connect GitHub repo
   - Runtime: Python 3.11
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

2. **Add Environment Variables**
   - TWILIO_ACCOUNT_SID
   - TWILIO_AUTH_TOKEN
   - TWILIO_WHATSAPP_NUMBER
   - GEMINI_API_KEY

3. **Deploy**
   - Click Deploy

4. **Get URL and Update Twilio**
```
https://your-service.onrender.com/webhook
```

---

## Comparison Table

| Platform | Cost | Setup Time | Scaling | Database | Monitoring |
|----------|------|-----------|---------|----------|------------|
| Heroku | $50+/month | 5 min | Easy | PostgreSQL | Built-in |
| Google Cloud Run | $0.40/1M | 10 min | Auto | Firestore | Cloud Logging |
| AWS Lambda | $0.20/1M | 15 min | Auto | DynamoDB | CloudWatch |
| Azure | $13-50/month | 10 min | Easy | Cosmos DB | Application Insights |
| DigitalOcean | $6-12/month | 10 min | Manual | Managed DB | Simple |
| Docker VPS | $5-20/month | 20 min | Manual | SQLite | SSH logs |
| Render | Free (limited) | 5 min | Easy | Cloud Storage | Built-in |

---

## Monitoring Your Deployment

### Health Checks
```bash
curl https://your-deployed-url/health
```

### View Logs
- Heroku: `heroku logs --tail`
- Google Cloud: `gcloud logging read`
- AWS: CloudWatch console
- Azure: App Service logs
- Docker: `docker logs nutrition-bot`

### Monitor Webhook Calls
```bash
curl -X POST https://your-url/webhook \
  -d "Body=I+ate+rice&From=whatsapp:+919999999999&ProfileName=Test"
```

---

## Scaling Considerations

### Database Scaling
- SQLite: Works for <1000 users
- PostgreSQL: 1000-100k users
- MongoDB: 100k+ users

### Performance Tuning
```python
# In app.py, increase workers for production
gunicorn -w 8 -b 0.0.0.0:5000 app:app
```

### Rate Limiting (Add to app.py)
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/webhook', methods=['POST'])
@limiter.limit("20 per minute")
def webhook():
    # ... code
```

---

## Cost Optimization

### Free Tier Options
- **Google Cloud Run**: 2M invocations free/month
- **AWS Lambda**: 1M free/month
- **Render**: Limited free tier
- **Heroku**: No free tier (discontinued)

### Budget Alerts
Set up budget alerts on:
- Google Cloud
- AWS
- Azure

---

## Backup & Disaster Recovery

### Database Backups
```bash
# SQLite backup
sqlite3 nutrition_bot.db ".backup nutrition_bot_backup.db"

# Automated daily backups
0 2 * * * sqlite3 /path/to/nutrition_bot.db ".backup /backups/nutrition_bot_$(date +\%Y\%m\%d).db"
```

### Application Backup
- Keep Git repository up to date
- Tag releases: `git tag v1.0.0`

---

## SSL/TLS Certificate

### Auto-Renew (Let's Encrypt)
```bash
# Certbot (automatic renewal)
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com
sudo systemctl enable certbot.timer
```

---

## Security Best Practices

1. **Never commit .env** - Use `.gitignore`
2. **Rotate API keys** periodically
3. **Enable HTTPS only**
4. **Monitor logs** for suspicious activity
5. **Use strong database passwords**
6. **Enable WAF** (Web Application Firewall)

---

## Troubleshooting Deployment

### Bot not receiving messages
- Verify webhook URL is correct
- Check Twilio sending logs
- Ensure HTTPS is used
- Verify firewall allows traffic

### High latency
- Check worker count
- Monitor CPU/memory usage
- Enable caching for health checks
- Consider CDN for static assets

### Database errors
- Check disk space
- Verify connection string
- Monitor for long-running queries

---

## Next Steps

1. Choose a platform above
2. Follow deployment instructions
3. Test the bot
4. Monitor logs
5. Set up automated backups
6. Add monitoring/alerting

---

**Your bot is production-ready! 🚀**

import os
import sys
import threading
import time
from pyngrok import ngrok
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_tunnel():
    """Start ngrok tunnel and print the public URL"""
    try:
        # Open a HTTP tunnel on the default port 5000
        public_url = ngrok.connect(5000).public_url
        
        print("\n" + "="*70)
        print("🌍 PUBLIC URL GENERATED!")
        print("="*70)
        print(f"\n👉 COPY THIS URL: {public_url}/webhook")
        print("\n📝 STEPS TO CONNECT WHATSAPP:")
        print("1. Go to Twilio Console > Messaging > WhatsApp > Sandbox Settings")
        print(f"2. Paste the URL above into 'When a message comes in'")
        print("3. Save settings")
        print("4. Send 'join <your-sandbox-keyword>' from your phone to the number")
        print("\n" + "="*70 + "\n")
        
        return public_url
    except Exception as e:
        print(f"Error starting tunnel: {e}")
        return None

if __name__ == "__main__":
    # Force unbuffered output for Windows
    sys.stdout.reconfigure(encoding='utf-8')
    
    # authentication
    token = os.getenv('NGROK_AUTH_TOKEN')
    if token:
        print(f"Setting ngrok auth token: {token[:4]}...", flush=True)
        ngrok.set_auth_token(token)
    else:
        print("⚠️  Warning: NGROK_AUTH_TOKEN not found in .env", flush=True)
        print("   If you see an authentication error, get your token from: https://dashboard.ngrok.com/get-started/your-authtoken", flush=True)
        print("   Then add NGROK_AUTH_TOKEN=your_token to your .env file\n", flush=True)
    
    print("Starting tunnel...", flush=True)
    url = start_tunnel()
    
    if url:
        print("Starting Flask app...", flush=True)
        # We import app here to avoid circular imports or early init
        from app import app
        # Disable debug mode to prevent threading issues/output capturing
        app.run(port=5000, debug=False, use_reloader=False)
    else:
        print("Failed to start tunnel.", flush=True)

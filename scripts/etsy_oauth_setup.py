"""
Etsy OAuth 2.0 Setup Script

This script helps you obtain access and refresh tokens for Etsy API v3.
Run this script once to authenticate and get tokens, then store them in local.env
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from etsy_python import EtsyOAuth
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser
import threading

# Load environment
BASE_DIR = Path(__file__).parent.parent
ENV_PATH = BASE_DIR / "config" / "local.env"
load_dotenv(ENV_PATH)

# Get credentials
API_KEY = os.getenv("ETSY_API_KEY")
SHARED_SECRET = os.getenv("ETSY_SHARED_SECRET")
REDIRECT_URI = "http://localhost:8080/callback"

if not API_KEY or not SHARED_SECRET:
    print("ERROR: ETSY_API_KEY and ETSY_SHARED_SECRET must be set in config/local.env")
    sys.exit(1)

# Global to store auth code from callback
auth_code = None
server_should_stop = False

class CallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from Etsy"""
    
    def do_GET(self):
        global auth_code, server_should_stop
        
        # Parse URL
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if '/callback' in self.path:
            if 'code' in params:
                auth_code = params['code'][0]
                
                # Send success page
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = """
                <html>
                <body style="font-family: Arial; text-align: center; margin-top: 100px;">
                    <h1 style="color: green;">✓ Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
                """
                self.wfile.write(message.encode())
                server_should_stop = True
            else:
                # Error
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = """
                <html>
                <body style="font-family: Arial; text-align: center; margin-top: 100px;">
                    <h1 style="color: red;">✗ Authorization Failed</h1>
                    <p>No authorization code received.</p>
                </body>
                </html>
                """
                self.wfile.write(message.encode())
        
    def log_message(self, format, *args):
        # Suppress log messages
        pass

def run_oauth_flow():
    """Execute OAuth flow"""
    global auth_code
    
    print("\n" + "="*60)
    print("ETSY API OAUTH 2.0 SETUP")
    print("="*60)
    print(f"\nAPI Key: {API_KEY[:10]}...")
    print(f"Redirect URI: {REDIRECT_URI}")
    
    # Initialize OAuth client
    oauth = EtsyOAuth(
        api_key=API_KEY,
        shared_secret=SHARED_SECRET,
        redirect_uri=REDIRECT_URI,
        scopes=['listings_r', 'listings_w', 'shops_r', 'transactions_r']
    )
    
    # Step 1: Get authorization URL
    auth_url, state, code_verifier = oauth.get_authorization_url()
    
    print(f"\n[Step 1] Opening browser for authorization...")
    print(f"Authorization URL: {auth_url}\n")
    
    # Start local server for callback
    server = HTTPServer(('localhost', 8080), CallbackHandler)
    
    def run_server():
        while not server_should_stop:
            server.handle_request()
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Open browser
    webbrowser.open(auth_url)
    
    print("[Step 2] Waiting for authorization...")
    print("(Please grant access in your browser)")
    
    # Wait for callback
    import time
    timeout = 300  # 5 minutes
    elapsed = 0
    while auth_code is None and elapsed < timeout:
        time.sleep(1)
        elapsed += 1
    
    if auth_code is None:
        print("\n✗ Timeout: No authorization code received.")
        print("Please try again and complete the authorization in your browser.")
        sys.exit(1)
    
    print(f"\n✓ Authorization code received!")
    
    # Step 3: Exchange code for tokens
    print("\n[Step 3] Exchanging code for access tokens...")
    
    try:
        tokens = oauth.get_access_token(auth_code, code_verifier)
        
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        expires_in = tokens.get('expires_in', 3600)
        
        print("\n" + "="*60)
        print("✓ SUCCESS! Tokens obtained.")
        print("="*60)
        print(f"\nAccess Token: {access_token[:20]}...")
        print(f"Refresh Token: {refresh_token[:20]}...")
        print(f"Expires in: {expires_in} seconds ({expires_in/3600:.1f} hours)")
        
        # Update local.env
        print("\n[Step 4] Updating config/local.env with tokens...")
        update_env_file(access_token, refresh_token, expires_in)
        
        print("\n" + "="*60)
        print("✓ SETUP COMPLETE!")
        print("="*60)
        print("\nYour Etsy API credentials are now configured.")
        print("You can now use the Etsy API in your application.")
        print("\nNote: Access tokens expire in 1 hour.")
        print("The application will automatically refresh them using the refresh token.")
        
    except Exception as e:
        print(f"\n✗ Error exchanging code for tokens: {e}")
        sys.exit(1)

def update_env_file(access_token, refresh_token, expires_in):
    """Update local.env with new tokens"""
    import time
    
    # Calculate expiry timestamp
    expires_at = int(time.time()) + expires_in
    
    # Read current env file
    with open(ENV_PATH, 'r') as f:
        lines = f.readlines()
    
    # Remove old token lines
    lines = [l for l in lines if not any(l.startswith(key) for key in [
        'ETSY_ACCESS_TOKEN=',
        'ETSY_REFRESH_TOKEN=',
        'ETSY_TOKEN_EXPIRES_AT=',
        'ETSY_REDIRECT_URI='
    ])]
    
    # Add new tokens
    lines.append(f"\n# Etsy OAuth Tokens (auto-generated)\n")
    lines.append(f"ETSY_ACCESS_TOKEN={access_token}\n")
    lines.append(f"ETSY_REFRESH_TOKEN={refresh_token}\n")
    lines.append(f"ETSY_TOKEN_EXPIRES_AT={expires_at}\n")
    lines.append(f"ETSY_REDIRECT_URI={REDIRECT_URI}\n")
    
    # Write back
    with open(ENV_PATH, 'w') as f:
        f.writelines(lines)
    
    print(f"✓ Tokens saved to {ENV_PATH}")

if __name__ == "__main__":
    run_oauth_flow()

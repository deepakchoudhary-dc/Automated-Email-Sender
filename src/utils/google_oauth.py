import os
import secrets
from dotenv import load_dotenv

# Optional Google OAuth imports
try:
    from google.oauth2 import credentials
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    GOOGLE_OAUTH_AVAILABLE = True
except ImportError:
    GOOGLE_OAUTH_AVAILABLE = False
    print("Warning: Google OAuth libraries not available. Google authentication will be disabled.")

load_dotenv()

class GoogleOAuth:
    """Google OAuth handler for authentication"""
    
    def __init__(self):
        if not GOOGLE_OAUTH_AVAILABLE:
            print("Google OAuth not available - functionality will be limited")
            self.client_id = None
            self.client_secret = None
            self.redirect_uri = None
            self.scopes = []
            return
            
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8501/auth/callback')
        
        self.scopes = [
            'openid',
            'email',            'profile',
            'https://www.googleapis.com/auth/gmail.send'
        ]
    
    def get_auth_url(self) -> str:
        """Get Google OAuth authorization URL"""
        
        if not GOOGLE_OAUTH_AVAILABLE:
            raise ValueError("Google OAuth libraries not available")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials not configured")
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        
        flow.redirect_uri = self.redirect_uri
          # Generate state parameter for security
        state = secrets.token_urlsafe(32)
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state
        )
        
        return auth_url
    
    def handle_callback(self, authorization_code: str) -> dict:
        """Handle OAuth callback and get user info"""
        
        if not GOOGLE_OAUTH_AVAILABLE:
            raise ValueError("Google OAuth libraries not available")
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        
        flow.redirect_uri = self.redirect_uri
        
        # Fetch token
        flow.fetch_token(code=authorization_code)
        
        # Get user info
        user_info = self._get_user_info(flow.credentials)
        
        return {
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'picture': user_info.get('picture'),
            'credentials': flow.credentials
        }
    
    def _get_user_info(self, creds) -> dict:
        """Get user information from Google"""
        
        import requests
        
        # Use the credentials to make an API call
        headers = {'Authorization': f'Bearer {creds.token}'}
        response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get user info: {response.status_code}")
    
    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh OAuth token"""
        
        creds = credentials.UserAccessTokenCredentials(
            token=None,
            refresh_token=refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        request = Request()
        creds.refresh(request)
        
        return {
            'access_token': creds.token,
            'refresh_token': creds.refresh_token,
            'expires_at': creds.expiry
        }

import os
import secrets
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import hashlib
import jwt
from datetime import datetime, timedelta
import bcrypt

load_dotenv()

class SecurityManager:
    """Handles security operations for the application"""
    
    def __init__(self):
        self._secret_key = os.getenv('SECRET_KEY', self._generate_secret_key())
        encryption_key = os.getenv('ENCRYPTION_KEY')
        
        if encryption_key:
            # If key exists, validate and use it
            try:
                self._cipher_suite = Fernet(encryption_key.encode())
                self._encryption_key = encryption_key
            except Exception:
                # If key is invalid, generate a new one
                self._encryption_key = self._generate_encryption_key()
                self._cipher_suite = Fernet(self._encryption_key.encode())
        else:
            # Generate new key if not exists
            self._encryption_key = self._generate_encryption_key()
            self._cipher_suite = Fernet(self._encryption_key.encode())
    
    def get_secret_key(self) -> str:
        """Get the application secret key"""
        return self._secret_key
    
    def get_encryption_key(self) -> str:
        """Get the encryption key"""
        return self._encryption_key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted_data = self._cipher_suite.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decrypted_data = self._cipher_suite.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def verify_api_key(self, api_key: str, hashed_key: str) -> bool:
        """Verify API key against hash"""
        return hashlib.sha256(api_key.encode()).hexdigest() == hashed_key
    
    def generate_api_key(self) -> str:
        """Generate a new API key"""
        return secrets.token_urlsafe(32)
    
    def create_jwt_token(self, payload: dict, expires_hours: int = 24) -> str:
        """Create JWT token"""
        payload['exp'] = datetime.utcnow() + timedelta(hours=expires_hours)
        return jwt.encode(payload, self._secret_key, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            return jwt.decode(token, self._secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    def sanitize_input(self, input_string: str) -> str:
        """Sanitize user input to prevent XSS"""
        import bleach
        
        allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
        allowed_attributes = {}
        
        return bleach.clean(input_string, tags=allowed_tags, attributes=allowed_attributes)
    
    def validate_email_content(self, content: str) -> bool:
        """Validate email content for security"""
        dangerous_patterns = [
            '<script',
            'javascript:',
            'onload=',
            'onerror=',
            'onclick=',
            'eval(',
            'document.cookie'
        ]
        
        content_lower = content.lower()
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                return False
        
        return True
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    def verify_csrf_token(self, token: str, session_token: str) -> bool:
        """Verify CSRF token"""
        return secrets.compare_digest(token, session_token)
    
    @staticmethod
    def _generate_secret_key() -> str:
        """Generate a new secret key"""
        return secrets.token_urlsafe(64)
    
    @staticmethod
    def _generate_encryption_key() -> str:
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()
    
    def rate_limit_check(self, identifier: str, limit: int, window_minutes: int = 60) -> bool:
        """Check if rate limit is exceeded"""
        # This would typically use Redis or another cache
        # For now, returning True (not rate limited)
        return True
    
    def validate_file_upload(self, filename: str, file_content: bytes, 
                           allowed_extensions: list = None) -> bool:
        """Validate file upload for security"""
        
        if allowed_extensions is None:
            allowed_extensions = ['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif']
        
        # Check file extension
        file_ext = filename.lower().split('.')[-1]
        if file_ext not in allowed_extensions:
            return False
        
        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(file_content) > max_size:
            return False
        
        # Check for malicious content
        dangerous_signatures = [
            b'<script',
            b'javascript:',
            b'<?php',
            b'<%',
            b'<iframe'
        ]
        
        content_lower = file_content.lower()
        for signature in dangerous_signatures:
            if signature in content_lower:
                return False
        
        return True

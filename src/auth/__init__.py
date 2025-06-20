import streamlit as st
import logging
from datetime import datetime, timedelta
import jwt
import bcrypt
import re
from typing import Optional, Dict, Any
from src.database.models import User, db_session
try:
    from src.utils.google_oauth import GoogleOAuth, GOOGLE_OAUTH_AVAILABLE
except ImportError:
    GOOGLE_OAUTH_AVAILABLE = False
    GoogleOAuth = None
from src.utils.security import SecurityManager

logger = logging.getLogger(__name__)

class Authentication:
    """Handles user authentication and session management"""
    
    def __init__(self):
        self.security_manager = SecurityManager()
        if GOOGLE_OAUTH_AVAILABLE and GoogleOAuth:
            self.google_oauth = GoogleOAuth()
        else:
            self.google_oauth = None
        
    def show_login_page(self):
        """Display the login/register page"""
        
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1>🔐 Welcome to Automated Email Sender</h1>
            <p style="font-size: 1.2rem; color: #666;">
                Professional email marketing and automation platform
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create tabs for login and register
        tab1, tab2 = st.tabs(["🔑 Login", "👤 Register"])
        
        with tab1:
            self._show_login_form()
            
        with tab2:
            self._show_register_form()
            
        # Google OAuth login
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Continue with Google", use_container_width=True):
                self._handle_google_login()
    
    def _show_login_form(self):
        """Display login form"""
        
        with st.form("login_form"):
            st.subheader("Login to Your Account")
            
            email = st.text_input("📧 Email", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            remember_me = st.checkbox("Remember me")
            
            col1, col2 = st.columns(2)
            with col1:
                login_submitted = st.form_submit_button("Login", use_container_width=True)
            with col2:
                if st.form_submit_button("Forgot Password?", use_container_width=True):
                    self._show_forgot_password(email)
            
            if login_submitted:
                self._handle_login(email, password, remember_me)
    
    def _show_register_form(self):
        """Display registration form"""
        
        with st.form("register_form"):
            st.subheader("Create New Account")
            
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("👤 First Name", placeholder="First name")
            with col2:
                last_name = st.text_input("👤 Last Name", placeholder="Last name")
            
            email = st.text_input("📧 Email", placeholder="Enter your email")
            
            col1, col2 = st.columns(2)
            with col1:
                password = st.text_input("🔒 Password", type="password", placeholder="Create password")
            with col2:
                confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm password")
            
            company = st.text_input("🏢 Company (Optional)", placeholder="Company name")
            
            agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            register_submitted = st.form_submit_button("Create Account", use_container_width=True)
            
            if register_submitted:
                self._handle_registration(
                    first_name, last_name, email, password, confirm_password, company, agree_terms
                )
    
    def _handle_login(self, email: str, password: str, remember_me: bool = False):
        """Handle user login"""
        
        if not email or not password:
            st.error("Please enter both email and password")
            return
        
        if not self._validate_email(email):
            st.error("Please enter a valid email address")
            return
        
        try:
            with db_session() as session:
                user = session.query(User).filter(User.email == email.lower()).first()
                
                if user and self._verify_password(password, user.password_hash):
                    # Successful login
                    self._create_session(user, remember_me)
                    st.success("Login successful! Welcome back!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
                    logger.warning(f"Failed login attempt for email: {email}")
        
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            st.error("An error occurred during login. Please try again.")
    
    def _handle_registration(self, first_name: str, last_name: str, email: str, 
                           password: str, confirm_password: str, company: str, agree_terms: bool):
        """Handle user registration"""
        
        # Validation
        if not all([first_name, last_name, email, password, confirm_password]):
            st.error("Please fill in all required fields")
            return
        
        if not self._validate_email(email):
            st.error("Please enter a valid email address")
            return
        
        if password != confirm_password:
            st.error("Passwords do not match")
            return
        
        if not self._validate_password(password):
            st.error("Password must be at least 8 characters with uppercase, lowercase, and number")
            return
        
        if not agree_terms:
            st.error("You must agree to the Terms of Service and Privacy Policy")
            return
        
        try:
            with db_session() as session:
                # Check if user already exists
                existing_user = session.query(User).filter(User.email == email.lower()).first()
                if existing_user:
                    st.error("An account with this email already exists")
                    return
                
                # Create new user
                password_hash = self._hash_password(password)
                new_user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email.lower(),
                    password_hash=password_hash,
                    company=company,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                session.add(new_user)
                session.commit()
                
                st.success("Account created successfully! You can now login.")
                logger.info(f"New user registered: {email}")
        
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            st.error("An error occurred during registration. Please try again.")
    
    def _handle_google_login(self):
        """Handle Google OAuth login"""
        try:
            # This would integrate with Google OAuth
            # For now, showing placeholder
            st.info("Google OAuth integration coming soon!")
            
            # In a real implementation:
            # auth_url = self.google_oauth.get_auth_url()
            # st.markdown(f"[Click here to login with Google]({auth_url})")
            
        except Exception as e:
            logger.error(f"Google OAuth error: {str(e)}")
            st.error("Google login is temporarily unavailable")
    
    def _show_forgot_password(self, email: str):
        """Show forgot password dialog"""
        if email and self._validate_email(email):
            st.info(f"Password reset instructions will be sent to {email}")
            # In a real implementation, send password reset email
        else:
            st.error("Please enter a valid email address")
    
    def _create_session(self, user: User, remember_me: bool = False):
        """Create user session"""
        
        # Set session state
        st.session_state.authenticated = True
        st.session_state.user_id = user.id
        st.session_state.user_email = user.email
        st.session_state.user_name = f"{user.first_name} {user.last_name}"
        st.session_state.user_role = user.role
        st.session_state.company = user.company
        
        # Create JWT token for session management
        payload = {
            'user_id': user.id,
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(days=30 if remember_me else 1)
        }
        
        token = jwt.encode(payload, self.security_manager.get_secret_key(), algorithm='HS256')
        st.session_state.auth_token = token
        
        # Update last login
        try:
            with db_session() as session:
                user_to_update = session.query(User).filter(User.id == user.id).first()
                user_to_update.last_login = datetime.utcnow()
                session.commit()
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
    
    def logout(self):
        """Logout user and clear session"""
        
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        st.session_state.authenticated = False
        st.success("You have been logged out successfully")
        st.rerun()
    
    def verify_session(self) -> bool:
        """Verify if user session is valid"""
        
        if not st.session_state.get('authenticated', False):
            return False
        
        token = st.session_state.get('auth_token')
        if not token:
            return False
        
        try:
            payload = jwt.decode(token, self.security_manager.get_secret_key(), algorithms=['HS256'])
            return True
        except jwt.ExpiredSignatureError:
            self.logout()
            return False
        except jwt.InvalidTokenError:
            self.logout()
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current user information"""
        
        if not self.verify_session():
            return None
        
        return {
            'id': st.session_state.get('user_id'),
            'email': st.session_state.get('user_email'),
            'name': st.session_state.get('user_name'),
            'role': st.session_state.get('user_role'),
            'company': st.session_state.get('company')
        }
    
    @staticmethod
    def _validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def _validate_password(password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

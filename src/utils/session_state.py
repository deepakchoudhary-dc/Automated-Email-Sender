import streamlit as st
from datetime import datetime

def initialize_session_state():
    """Initialize session state variables"""
    
    # Authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    
    if 'user_role' not in st.session_state:
        st.session_state.user_role = 'user'
    
    if 'company' not in st.session_state:
        st.session_state.company = None
    
    # Navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Dashboard'
    
    # Campaign management
    if 'selected_campaign' not in st.session_state:
        st.session_state.selected_campaign = None
    
    if 'edit_campaign' not in st.session_state:
        st.session_state.edit_campaign = None
    
    if 'campaign_analytics' not in st.session_state:
        st.session_state.campaign_analytics = None
    
    # Template management
    if 'selected_template' not in st.session_state:
        st.session_state.selected_template = None
    
    if 'edit_template' not in st.session_state:
        st.session_state.edit_template = None
    
    if 'preview_template' not in st.session_state:
        st.session_state.preview_template = None
    
    if 'create_from_template' not in st.session_state:
        st.session_state.create_from_template = None
    
    # Contact management
    if 'selected_contacts' not in st.session_state:
        st.session_state.selected_contacts = []
    
    if 'contact_filters' not in st.session_state:
        st.session_state.contact_filters = {}
    
    # Quick stats for sidebar
    if 'quick_stats' not in st.session_state:
        st.session_state.quick_stats = {
            'campaigns': 0,
            'contacts': 0,
            'templates': 0,
            'emails_sent': 0
        }
    
    # Recent activities
    if 'recent_activities' not in st.session_state:
        st.session_state.recent_activities = [
            "Welcome to Email Sender!",
            "Set up your first campaign",
            "Import your contacts"
        ]
    
    # Form states
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    # File uploads
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}
    
    # Notifications
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    
    # Settings
    if 'user_settings' not in st.session_state:
        st.session_state.user_settings = {
            'theme': 'light',
            'timezone': 'UTC',
            'email_notifications': True,
            'default_from_name': '',
            'default_from_email': ''
        }
    
    # Analytics filters
    if 'analytics_filters' not in st.session_state:
        st.session_state.analytics_filters = {
            'date_range': '30_days',
            'campaign_status': 'all',
            'email_provider': 'all'
        }
    
    # Campaign builder state
    if 'campaign_builder' not in st.session_state:
        st.session_state.campaign_builder = {
            'step': 1,
            'campaign_data': {},
            'selected_template': None,
            'selected_contacts': [],
            'schedule_type': 'immediate'
        }
    
    # Template editor state
    if 'template_editor' not in st.session_state:
        st.session_state.template_editor = {
            'template_data': {},
            'preview_mode': False,
            'unsaved_changes': False
        }
    
    # Email composer state
    if 'email_composer' not in st.session_state:
        st.session_state.email_composer = {
            'subject': '',
            'html_content': '',
            'text_content': '',
            'attachments': [],
            'variables': {}
        }
    
    # A/B testing state
    if 'ab_test' not in st.session_state:
        st.session_state.ab_test = {
            'test_type': 'subject',
            'variant_a': {},
            'variant_b': {},
            'split_percentage': 50,
            'test_duration': 24
        }
    
    # Automation state
    if 'automation' not in st.session_state:
        st.session_state.automation = {
            'trigger_type': 'contact_added',
            'conditions': [],
            'actions': [],
            'is_active': False
        }
    
    # Drip campaign state
    if 'drip_campaign' not in st.session_state:
        st.session_state.drip_campaign = {
            'name': '',
            'emails': [],
            'trigger_conditions': {},
            'target_audience': []
        }
    
    # Error tracking
    if 'errors' not in st.session_state:
        st.session_state.errors = []
    
    # Success messages
    if 'success_messages' not in st.session_state:
        st.session_state.success_messages = []
    
    # Loading states
    if 'loading_states' not in st.session_state:
        st.session_state.loading_states = {}
    
    # Modal states
    if 'modal_open' not in st.session_state:
        st.session_state.modal_open = False
    
    if 'modal_content' not in st.session_state:
        st.session_state.modal_content = None
    
    # Cache management
    if 'cache_timestamps' not in st.session_state:
        st.session_state.cache_timestamps = {}
    
    # API rate limiting
    if 'api_calls' not in st.session_state:
        st.session_state.api_calls = {}
    
    # Feature flags
    if 'feature_flags' not in st.session_state:
        st.session_state.feature_flags = {
            'ai_content_generation': True,
            'advanced_analytics': True,
            'automation_builder': True,
            'ab_testing': True,
            'drip_campaigns': True,
            'team_collaboration': False
        }

def reset_session_state():
    """Reset all session state variables"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()

def add_notification(message: str, type: str = 'info'):
    """Add a notification to session state"""
    notification = {
        'message': message,
        'type': type,
        'timestamp': datetime.now()
    }
    
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    
    st.session_state.notifications.append(notification)
    
    # Keep only last 10 notifications
    if len(st.session_state.notifications) > 10:
        st.session_state.notifications = st.session_state.notifications[-10:]

def clear_notifications():
    """Clear all notifications"""
    st.session_state.notifications = []

def set_loading_state(key: str, loading: bool):
    """Set loading state for a specific component"""
    if 'loading_states' not in st.session_state:
        st.session_state.loading_states = {}
    
    st.session_state.loading_states[key] = loading

def get_loading_state(key: str) -> bool:
    """Get loading state for a specific component"""
    return st.session_state.get('loading_states', {}).get(key, False)

def update_user_activity(activity: str):
    """Update user activity log"""
    if 'recent_activities' not in st.session_state:
        st.session_state.recent_activities = []
    
    activity_entry = f"{datetime.now().strftime('%H:%M')} - {activity}"
    st.session_state.recent_activities.insert(0, activity_entry)
    
    # Keep only last 10 activities
    if len(st.session_state.recent_activities) > 10:
        st.session_state.recent_activities = st.session_state.recent_activities[:10]

def save_form_data(form_name: str, data: dict):
    """Save form data to session state"""
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    st.session_state.form_data[form_name] = data

def get_form_data(form_name: str) -> dict:
    """Get form data from session state"""
    return st.session_state.get('form_data', {}).get(form_name, {})

def clear_form_data(form_name: str):
    """Clear specific form data"""
    if 'form_data' in st.session_state and form_name in st.session_state.form_data:
        del st.session_state.form_data[form_name]

def cache_data(key: str, data: any, ttl_minutes: int = 30):
    """Cache data with TTL"""
    if 'cached_data' not in st.session_state:
        st.session_state.cached_data = {}
    
    if 'cache_timestamps' not in st.session_state:
        st.session_state.cache_timestamps = {}
    
    st.session_state.cached_data[key] = data
    st.session_state.cache_timestamps[key] = datetime.now()

def get_cached_data(key: str, ttl_minutes: int = 30):
    """Get cached data if not expired"""
    if key not in st.session_state.get('cached_data', {}):
        return None
    
    timestamp = st.session_state.get('cache_timestamps', {}).get(key)
    if not timestamp:
        return None
    
    # Check if cache is expired
    if (datetime.now() - timestamp).total_seconds() > (ttl_minutes * 60):
        # Remove expired cache
        if key in st.session_state.cached_data:
            del st.session_state.cached_data[key]
        if key in st.session_state.cache_timestamps:
            del st.session_state.cache_timestamps[key]
        return None
    
    return st.session_state.cached_data[key]

def clear_cache():
    """Clear all cached data"""
    st.session_state.cached_data = {}
    st.session_state.cache_timestamps = {}

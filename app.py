import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Automated Email Sender",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import custom modules
from src.auth.authentication import Authentication
from src.ui.dashboard import Dashboard
from src.ui.sidebar_working import Sidebar
from src.utils.session_state import initialize_session_state
from src.utils.logger import setup_logging
from src.utils.logger import setup_logging

# Initialize logging
setup_logging()

def main():
    """Main application entry point"""
    
    # Initialize session state
    initialize_session_state()
    
    # Custom CSS for better UI
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .sidebar-content {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .success-message {
        background: #d1edff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .warning-message {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .campaign-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    .stats-container {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-item {
        flex: 1;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
    }
    
    .template-preview {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        background: white;
        max-height: 400px;
        overflow-y: auto;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Authentication check
    auth = Authentication()
    
    if not st.session_state.authenticated:
        auth.show_login_page()
    else:
        # Show main application
        show_main_app()

def show_main_app():
    """Display the main application interface"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📧 Automated Email Sender</h1>
        <p>Professional email marketing and automation platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize sidebar
    sidebar = Sidebar()
    selected_page = sidebar.render()
    
    # Initialize dashboard
    dashboard = Dashboard()
    
    # Route to selected page
    if selected_page == "Dashboard":
        dashboard.show_dashboard()
    elif selected_page == "Campaigns":
        dashboard.show_campaigns()
    elif selected_page == "Templates":
        dashboard.show_templates()
    elif selected_page == "Contacts":
        dashboard.show_contacts()
    elif selected_page == "Analytics":
        dashboard.show_analytics()
    elif selected_page == "Settings":
        dashboard.show_settings()
    elif selected_page == "Drip Campaigns":
        dashboard.show_drip_campaigns()
    elif selected_page == "A/B Testing":
        dashboard.show_ab_testing()
    elif selected_page == "Automation":
        dashboard.show_automation()
    elif selected_page == "Reports":
        dashboard.show_reports()

if __name__ == "__main__":
    main()

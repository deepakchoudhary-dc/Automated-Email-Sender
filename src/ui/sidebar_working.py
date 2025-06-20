import streamlit as st
from typing import Optional

class Sidebar:
    """Sidebar navigation component"""
    
    def __init__(self):
        self.navigation_items = [
            {"name": "Dashboard", "icon": "📊"},
            {"name": "Campaigns", "icon": "📧"},
            {"name": "Templates", "icon": "📝"},
            {"name": "Contacts", "icon": "👥"},
            {"name": "Analytics", "icon": "📊"},
            {"name": "Drip Campaigns", "icon": "🔄"},
            {"name": "A/B Testing", "icon": "🧪"},
            {"name": "Automation", "icon": "🤖"},
            {"name": "Reports", "icon": "📈"},
            {"name": "Settings", "icon": "⚙️"}
        ]
    
    def render(self) -> Optional[str]:
        """Render sidebar navigation"""
        
        with st.sidebar:
            st.title("📨 Email Marketing")
            st.markdown("---")
            
            # Navigation menu using selectbox
            selected_page = st.selectbox(
                "Navigate to:",
                [item['name'] for item in self.navigation_items],
                index=0,
                key="navigation_select"
            )
            
            st.markdown("---")
            
            # User info section
            if 'user_email' in st.session_state:
                st.write(f"👤 **{st.session_state.user_email}**")
                
                if st.button("🚪 Logout", use_container_width=True):
                    # Clear session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
            else:
                st.write("👤 **Guest User**")
            
            # Quick stats
            st.markdown("---")
            st.markdown("### 📈 Quick Stats")
            
            # Sample stats - replace with real data
            st.metric("Active Campaigns", "3")
            st.metric("Total Contacts", "1,234")
            st.metric("This Month", "567 emails")
            
            return selected_page

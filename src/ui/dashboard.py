import streamlit as st
import pandas as pd
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    px = None
    go = None
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any

from src.database.models import Campaign, Contact, EmailLog, User, db_session
from src.services.email_service import EmailService
from src.services.analytics_service import AnalyticsService
from src.services.template_service import TemplateService
from src.services.contact_service import ContactService
from src.ui.components.campaign_builder import CampaignBuilder
from src.ui.components.template_editor import TemplateEditor
from src.ui.components.contact_manager import ContactManager
from src.ui.components.analytics_dashboard import AnalyticsDashboard
from src.ui.components.automation_builder import AutomationBuilder

class Dashboard:
    """Main dashboard controller"""
    
    def __init__(self):
        self.email_service = EmailService()
        self.analytics_service = AnalyticsService()
        self.template_service = TemplateService()
        self.contact_service = ContactService()
    
    def show_dashboard(self):
        """Show main dashboard"""
        
        st.title("📊 Dashboard Overview")
        
        # Key metrics
        self._render_key_metrics()
        
        # Charts and analytics
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_recent_campaigns()
            self._render_email_performance()
        
        with col2:
            self._render_activity_chart()
            self._render_quick_actions()
    
    def show_campaigns(self):
        """Show campaigns page"""
        
        st.title("📧 Email Campaigns")
        
        # Tabs for different campaign views
        tab1, tab2, tab3 = st.tabs(["📋 All Campaigns", "➕ Create Campaign", "📈 Performance"])
        
        with tab1:
            campaign_builder = CampaignBuilder()
            campaign_builder.render_campaign_management()
        
        with tab2:
            campaign_builder = CampaignBuilder()
            campaign_builder.render()
        
        with tab3:
            analytics_dashboard = AnalyticsDashboard()
            analytics_dashboard._render_campaign_analytics({}, datetime.now().date() - timedelta(days=30), datetime.now().date())
    
    def show_templates(self):
        """Show templates page"""
        
        st.title("📝 Email Templates")
        tab1, tab2, tab3 = st.tabs(["🗂️ My Templates", "➕ Create Template", "🎨 Template Gallery"])
        
        with tab1:
            self._render_templates_list()
        
        with tab2:
            template_editor = TemplateEditor()
            template_editor.render()
        
        with tab3:
            self._render_template_gallery()
    
    def show_contacts(self):
        """Show contacts page"""
        
        st.title("👥 Contact Management")
        
        contact_manager = ContactManager()
        contact_manager.render()
    
    def show_analytics(self):
        """Show analytics page"""
        
        st.title("📊 Email Analytics")
        
        analytics_dashboard = AnalyticsDashboard()
        analytics_dashboard.render()
    
    def show_drip_campaigns(self):
        """Show drip campaigns page"""
        
        st.title("🔄 Drip Campaigns")
          # Use the campaign builder for drip campaigns
        campaign_builder = CampaignBuilder()
        
        tab1, tab2 = st.tabs(["📋 Active Campaigns", "➕ Create Drip Campaign"])
        
        with tab1:
            # Filter to show only drip campaigns
            campaign_builder.render_campaign_management()
        
        with tab2:
            # Set default to drip campaign mode            st.selectbox("Campaign Type", ["Drip Campaign"], disabled=True, key="drip_default")
            campaign_builder._render_drip_campaign()
    
    def show_ab_testing(self):
        """Show A/B testing page"""
        
        st.title("🧪 A/B Testing")
        
        tab1, tab2, tab3 = st.tabs(["📊 Test Results", "➕ Create Test", "📈 Insights"])
        
        with tab1:
            analytics_dashboard = AnalyticsDashboard()
            analytics_dashboard._render_ab_test_analytics({}, datetime.now().date() - timedelta(days=30), datetime.now().date())
        
        with tab2:
            campaign_builder = CampaignBuilder()
            st.selectbox("Campaign Type", ["A/B Test Campaign"], disabled=True, key="ab_default")
            campaign_builder._render_ab_test_campaign()
        
        with tab3:
            analytics_dashboard = AnalyticsDashboard()
            analytics_dashboard._render_ab_test_analytics({}, datetime.now().date() - timedelta(days=90), datetime.now().date())
    
    def show_automation(self):
        """Show automation page"""
        
        st.title("🤖 Email Automation")
        
        automation_builder = AutomationBuilder()
        
        tab1, tab2, tab3 = st.tabs(["⚡ Active Automations", "➕ Create Automation", "📊 Performance"])
        
        with tab1:
            automation_builder.render_automation_management()
        
        with tab2:
            automation_builder.render()
        
        with tab3:
            analytics_dashboard = AnalyticsDashboard()
            analytics_dashboard._render_performance_analytics({}, datetime.now().date() - timedelta(days=30), datetime.now().date())
    
    def show_reports(self):
        """Show reports page"""
        
        st.title("📈 Reports & Insights")
        
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "📧 Email Reports", "👥 Audience Insights"])
        
        with tab1:
            self._render_overview_report()
        
        with tab2:
            self._render_email_reports()
        
        with tab3:
            self._render_audience_insights()
    
    def show_settings(self):
        """Show settings page"""
        
        st.title("⚙️ Settings")
        
        tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "🔧 Email Setup", "🔐 Security", "🔗 Integrations"])
        
        with tab1:
            self._render_profile_settings()
        
        with tab2:
            self._render_email_settings()
        
        with tab3:
            self._render_security_settings()
        
        with tab4:            self._render_integrations_settings()
    
    def _render_key_metrics(self):
        """Render key performance metrics"""
        
        # Get metrics data with date range
        from datetime import datetime, timedelta
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        try:
            metrics = self.analytics_service.get_dashboard_metrics(
                st.session_state.get('user_id', 1), 
                start_date, 
                end_date
            )
        except Exception as e:
            # Fallback to sample data if service fails
            metrics = {
                'total_campaigns': 5,
                'emails_sent': 1250,
                'open_rate': 24.5,
                'click_rate': 3.2,
                'campaigns_delta': 2,
                'emails_delta': 150,
                'open_rate_delta': 1.2,
                'click_rate_delta': 0.3
            }
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📧 Total Campaigns",
                value=metrics.get('total_campaigns', 0),
                delta=metrics.get('campaigns_delta', 0)
            )
        
        with col2:
            st.metric(
                label="📮 Emails Sent",
                value=f"{metrics.get('emails_sent', 0):,}",
                delta=metrics.get('emails_delta', 0)
            )
        
        with col3:
            st.metric(
                label="📊 Open Rate",
                value=f"{metrics.get('open_rate', 0):.1f}%",
                delta=f"{metrics.get('open_rate_delta', 0):.1f}%"
            )
        
        with col4:
            st.metric(
                label="🎯 Click Rate",
                value=f"{metrics.get('click_rate', 0):.1f}%",
                delta=f"{metrics.get('click_rate_delta', 0):.1f}%"
            )
    
    def _render_recent_campaigns(self):
        """Render recent campaigns"""
        
        st.subheader("🚀 Recent Campaigns")
        
        # Get recent campaigns
        recent_campaigns = self.analytics_service.get_recent_campaigns(
            st.session_state.get('user_id', 1), limit=5
        )
        
        if recent_campaigns:
            for campaign in recent_campaigns:
                with st.expander(f"📧 {campaign['name']}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Sent", campaign.get('sent_count', 0))
                    with col2:
                        st.metric("Opens", f"{campaign.get('open_rate', 0):.1f}%")
                    with col3:
                        st.metric("Clicks", f"{campaign.get('click_rate', 0):.1f}%")
                    
                    if st.button(f"View Details", key=f"view_{campaign['id']}"):
                        st.session_state.selected_campaign = campaign['id']
                        st.rerun()
        else:
            st.info("No campaigns yet. Create your first campaign to get started!")
    
    def _render_email_performance(self):
        """Render email performance chart"""
        
        st.subheader("📈 Email Performance Trend")
        
        # Get performance data
        performance_data = self.analytics_service.get_performance_trend(
            st.session_state.get('user_id', 1), days=30
        )
        
        if performance_data and PLOTLY_AVAILABLE:
            df = pd.DataFrame(performance_data)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['sent'],
                mode='lines+markers',
                name='Emails Sent',
                line=dict(color='#667eea')
            ))
            
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['opened'],
                mode='lines+markers',
                name='Opened',
                line=dict(color='#28a745')
            ))
            
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['clicked'],
                mode='lines+markers',
                name='Clicked',
                line=dict(color='#ffc107')
            ))
            
            fig.update_layout(
                title="Email Performance (Last 30 Days)",
                xaxis_title="Date",
                yaxis_title="Count",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No performance data available yet or Plotly not installed.")
    
    def _render_activity_chart(self):
        """Render activity chart"""
        
        st.subheader("🎯 Activity Overview")
        
        # Sample data - replace with real data
        activities = {
            'Campaigns Created': 12,
            'Emails Sent': 1250,
            'Templates Created': 8,
            'Contacts Added': 340
        }
        
        if PLOTLY_AVAILABLE:
            fig = px.pie(
                values=list(activities.values()),
                names=list(activities.keys()),
                title="Activity Distribution"
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=300)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("**Activity Distribution:**")
            for activity, count in activities.items():
                st.write(f"• {activity}: {count}")
    
    def _render_quick_actions(self):
        """Render quick action buttons"""
        
        st.subheader("⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📧 New Campaign", use_container_width=True):
                st.session_state.current_page = "Campaigns"
                st.rerun()
            
            if st.button("👥 Import Contacts", use_container_width=True):
                st.session_state.current_page = "Contacts"
                st.rerun()
        
        with col2:
            if st.button("📝 New Template", use_container_width=True):
                st.session_state.current_page = "Templates"
                st.rerun()
            
            if st.button("📊 View Analytics", use_container_width=True):
                st.session_state.current_page = "Analytics"
                st.rerun()
    
    def _render_campaigns_list(self):
        """Render campaigns list"""
        
        # Campaign filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox(
                "Status",
                ["All", "Draft", "Scheduled", "Sending", "Sent", "Paused"]
            )
        
        with col2:
            date_filter = st.selectbox(
                "Date Range",
                ["All Time", "Last 7 days", "Last 30 days", "Last 90 days"]
            )
        
        with col3:
            search_term = st.text_input("🔍 Search campaigns", placeholder="Search...")
        
        # Get campaigns data
        campaigns = self.analytics_service.get_campaigns_list(
            st.session_state.user_id,
            status_filter=status_filter.lower() if status_filter != "All" else None,
            search_term=search_term
        )
        
        if campaigns:
            # Display campaigns in a table format
            for campaign in campaigns:
                with st.container():
                    st.markdown(f"""
                    <div class="campaign-card">
                        <h4>{campaign['name']}</h4>
                        <p><strong>Subject:</strong> {campaign['subject']}</p>
                        <p><strong>Status:</strong> <span style="color: {'green' if campaign['status'] == 'sent' else 'orange'}">{campaign['status'].title()}</span></p>
                        <p><strong>Created:</strong> {campaign['created_at']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Sent", campaign.get('sent_count', 0))
                    with col2:
                        st.metric("Delivered", campaign.get('delivered_count', 0))
                    with col3:
                        st.metric("Opened", campaign.get('opened_count', 0))
                    with col4:
                        st.metric("Clicked", campaign.get('clicked_count', 0))
                    
                    # Action buttons
                    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
                    
                    with action_col1:
                        if st.button("👁️ View", key=f"view_{campaign['id']}"):
                            st.session_state.selected_campaign = campaign['id']
                    
                    with action_col2:
                        if st.button("✏️ Edit", key=f"edit_{campaign['id']}"):
                            st.session_state.edit_campaign = campaign['id']
                    
                    with action_col3:
                        if st.button("📊 Analytics", key=f"analytics_{campaign['id']}"):
                            st.session_state.campaign_analytics = campaign['id']
                    
                    with action_col4:
                        if campaign['status'] == 'draft':
                            if st.button("🚀 Send", key=f"send_{campaign['id']}"):
                                self._send_campaign(campaign['id'])
                    
                    st.markdown("---")
        else:
            st.info("No campaigns found. Create your first campaign to get started!")
    
    def _render_campaign_performance(self):
        """Render campaign performance analytics"""
        
        st.subheader("📈 Campaign Performance Analysis")
        
        # Performance metrics
        performance_data = self.analytics_service.get_campaign_performance(st.session_state.user_id)
        
        if performance_data:
            # Performance overview
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_open_rate = performance_data.get('avg_open_rate', 0)
                st.metric("Avg Open Rate", f"{avg_open_rate:.1f}%")
            
            with col2:
                avg_click_rate = performance_data.get('avg_click_rate', 0)
                st.metric("Avg Click Rate", f"{avg_click_rate:.1f}%")
            
            with col3:
                avg_bounce_rate = performance_data.get('avg_bounce_rate', 0)
                st.metric("Avg Bounce Rate", f"{avg_bounce_rate:.1f}%")
            
            with col4:
                total_revenue = performance_data.get('total_revenue', 0)
                st.metric("Total Revenue", f"${total_revenue:,.2f}")
            
            # Performance comparison chart
            st.subheader("📊 Campaign Comparison")
            
            campaigns_df = pd.DataFrame(performance_data.get('campaigns', []))
            
            if not campaigns_df.empty:
                fig = px.scatter(
                    campaigns_df,
                    x='open_rate',
                    y='click_rate',
                    size='sent_count',
                    hover_data=['name', 'sent_count'],
                    title="Campaign Performance: Open Rate vs Click Rate"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No performance data available yet.")
    
    def _render_templates_list(self):
        """Render templates list"""
        
        st.subheader("📝 My Templates")
        
        # Template filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category_filter = st.selectbox(
                "Category",
                ["All", "Marketing", "Newsletter", "Transactional", "Welcome", "Other"]
            )
        
        with col2:
            template_type = st.selectbox(
                "Type",
                ["All", "Custom", "Predefined"]
            )
        
        with col3:
            search_term = st.text_input("🔍 Search templates", placeholder="Search...")
        
        # Get templates
        templates = self.template_service.get_templates_list(
            st.session_state.get('user_id', 1),
            category=category_filter.lower() if category_filter != "All" else None,
            template_type=template_type.lower() if template_type != "All" else None,
            search_term=search_term
        )
        
        if templates:
            # Display templates in grid
            cols = st.columns(3)
            
            for idx, template in enumerate(templates):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                        <h5>{template['name']}</h5>
                        <p><strong>Category:</strong> {template.get('category', 'General')}</p>
                        <p><strong>Created:</strong> {template['created_at']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("👁️ Preview", key=f"preview_{template['id']}"):
                            st.session_state.preview_template = template['id']
                    
                    with col2:
                        if st.button("✏️ Edit", key=f"edit_template_{template['id']}"):
                            st.session_state.edit_template = template['id']
        else:
            st.info("No templates found. Create your first template to get started!")
    
    def _render_template_gallery(self):
        """Render template gallery with predefined templates"""
        
        st.subheader("🎨 Template Gallery")
        st.info("Browse our collection of professionally designed email templates")
        
        # Predefined template categories
        categories = [
            {
                "name": "Welcome Series",
                "templates": [
                    {"name": "Simple Welcome", "description": "Clean and simple welcome email"},
                    {"name": "Product Welcome", "description": "Welcome with product highlights"},
                    {"name": "Service Welcome", "description": "Service-focused welcome email"}
                ]
            },
            {
                "name": "Newsletter",
                "templates": [
                    {"name": "Modern Newsletter", "description": "Contemporary newsletter design"},
                    {"name": "Corporate Newsletter", "description": "Professional corporate style"},
                    {"name": "Creative Newsletter", "description": "Creative and colorful design"}
                ]
            },
            {
                "name": "Promotional",
                "templates": [
                    {"name": "Sale Announcement", "description": "Eye-catching sale promotion"},
                    {"name": "Product Launch", "description": "New product announcement"},
                    {"name": "Event Invitation", "description": "Professional event invite"}
                ]
            }
        ]
        
        for category in categories:
            st.subheader(f"📁 {category['name']}")
            
            cols = st.columns(3)
            
            for idx, template in enumerate(category['templates']):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                        <h6>{template['name']}</h6>
                        <p>{template['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Use Template", key=f"use_{category['name']}_{idx}"):
                        # Create new template based on predefined template
                        st.session_state.create_from_template = template['name']
                        st.info(f"Creating new template based on '{template['name']}'...")
    
    def _render_overview_report(self):
        """Render overview report"""
        
        st.subheader("📊 Overview Report")
        
        # Date range selector
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        # Overview metrics
        st.markdown("### Key Metrics")
        
        metrics = {
            "Total Campaigns": 25,
            "Emails Sent": 12500,
            "Average Open Rate": "24.5%",
            "Average Click Rate": "3.2%",
            "Total Revenue": "$15,750"
        }
        
        cols = st.columns(len(metrics))
        for i, (metric, value) in enumerate(metrics.items()):
            with cols[i]:
                st.metric(metric, value)
        
        st.info("Detailed reports coming soon!")
    
    def _render_email_reports(self):
        """Render email reports"""
        
        st.subheader("📧 Email Reports")
        st.info("Email-specific reports coming soon!")
    
    def _render_audience_insights(self):
        """Render audience insights"""
        
        st.subheader("👥 Audience Insights")
        st.info("Audience insights coming soon!")
    
    def _render_profile_settings(self):
        """Render profile settings"""
        
        st.subheader("👤 Profile Settings")
        
        # Profile form
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name", value="John")
                email = st.text_input("Email", value="john@example.com")
            
            with col2:
                last_name = st.text_input("Last Name", value="Doe")
                company = st.text_input("Company", value="Acme Corp")
            
            timezone = st.selectbox("Timezone", ["UTC", "EST", "PST", "GMT"])
            
            if st.form_submit_button("Update Profile"):
                st.success("Profile updated successfully!")
    
    def _render_email_settings(self):
        """Render email settings"""
        
        st.subheader("🔧 Email Configuration")
        
        # Email provider settings
        tab1, tab2, tab3 = st.tabs(["SendGrid", "Amazon SES", "SMTP"])
        
        with tab1:
            st.text_input("SendGrid API Key", type="password")
            st.text_input("From Email")
            st.text_input("From Name")
        
        with tab2:
            st.text_input("AWS Access Key", type="password")
            st.text_input("AWS Secret Key", type="password")
            st.text_input("AWS Region")
        
        with tab3:
            st.text_input("SMTP Server")
            st.number_input("Port", value=587)
            st.text_input("Username")
            st.text_input("Password", type="password")
        
        if st.button("Save Email Settings"):
            st.success("Email settings saved successfully!")
    
    def _render_security_settings(self):
        """Render security settings"""
        
        st.subheader("🔐 Security Settings")
        
        # Password change
        with st.form("password_form"):
            st.text_input("Current Password", type="password")
            st.text_input("New Password", type="password")
            st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Change Password"):
                st.success("Password changed successfully!")
        
        st.markdown("---")
        
        # Two-factor authentication
        st.subheader("Two-Factor Authentication")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Enable 2FA")
        
        with col2:
            if st.button("Setup 2FA"):
                st.info("2FA setup coming soon!")
    
    def _render_integrations_settings(self):
        """Render integrations settings"""
        
        st.subheader("🔗 Third-Party Integrations")
        
        # Available integrations
        integrations = [
            {"name": "Google Analytics", "status": "Connected", "icon": "📊"},
            {"name": "Zapier", "status": "Not Connected", "icon": "⚡"},
            {"name": "Webhooks", "status": "Configured", "icon": "🔗"},
            {"name": "API Access", "status": "Enabled", "icon": "🔑"}
        ]
        
        for integration in integrations:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"{integration['icon']} **{integration['name']}**")
            
            with col2:
                status_color = "green" if integration['status'] == "Connected" or integration['status'] == "Enabled" else "orange"
                st.markdown(f"<span style='color: {status_color}'>{integration['status']}</span>", unsafe_allow_html=True)
            
            with col3:
                if st.button("Configure", key=f"config_{integration['name']}"):
                    st.info(f"Configuring {integration['name']}...")
        
        st.markdown("---")
        
        # API Keys
        st.subheader("API Keys")
        
        with st.expander("API Key Management"):
            st.text_input("API Key Name")
            st.selectbox("Permissions", ["Read Only", "Read/Write", "Full Access"])
            
            if st.button("Generate API Key"):
                st.code("api_key_example_12345", language="text")
                st.success("API key generated successfully!")

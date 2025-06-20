"""
Campaign Builder Component for creating and managing email campaigns.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.services.email_service import EmailService
from src.services.contact_service import ContactService
from src.services.template_service import TemplateService
from src.utils.session_state import initialize_session_state
from src.utils.logger import get_logger

logger = get_logger(__name__)

class CampaignBuilder:
    def __init__(self):
        self.email_service = EmailService()
        self.contact_service = ContactService()
        self.template_service = TemplateService()
    
    def render(self):
        """Render the campaign builder interface."""
        st.header("📧 Campaign Builder")
        
        # Campaign type selection
        campaign_type = st.selectbox(
            "Campaign Type",
            ["One-time Campaign", "Drip Campaign", "A/B Test Campaign"],
            help="Choose the type of email campaign to create"
        )
        
        if campaign_type == "One-time Campaign":
            self._render_one_time_campaign()
        elif campaign_type == "Drip Campaign":
            self._render_drip_campaign()
        elif campaign_type == "A/B Test Campaign":
            self._render_ab_test_campaign()
    
    def _render_one_time_campaign(self):
        """Render one-time campaign builder."""
        with st.form("one_time_campaign"):
            st.subheader("Create One-Time Campaign")
            
            # Campaign details
            col1, col2 = st.columns(2)
            with col1:
                campaign_name = st.text_input("Campaign Name*", key="campaign_name")
                subject_line = st.text_input("Subject Line*", key="subject_line")
            
            with col2:
                sender_name = st.text_input("Sender Name", value="Your Company")
                reply_to = st.text_input("Reply-To Email", key="reply_to")
            
            # Template selection
            templates = self.template_service.get_user_templates(st.session_state.user_id)
            template_options = ["None"] + [t["name"] for t in templates]
            selected_template = st.selectbox("Email Template", template_options)
            
            # Email content
            if selected_template != "None":
                template_data = next((t for t in templates if t["name"] == selected_template), None)
                if template_data:
                    st.info(f"Using template: {selected_template}")
                    email_content = st.text_area(
                        "Email Content (HTML)",
                        value=template_data.get("content", ""),
                        height=200
                    )
                else:
                    email_content = st.text_area("Email Content (HTML)", height=200)
            else:
                email_content = st.text_area("Email Content (HTML)", height=200)
            
            # Contact list selection
            contact_lists = self.contact_service.get_contact_lists(st.session_state.user_id)
            selected_lists = st.multiselect(
                "Contact Lists",
                [cl["name"] for cl in contact_lists],
                help="Select contact lists for this campaign"
            )
            
            # Scheduling options
            st.subheader("Scheduling")
            send_option = st.radio(
                "When to send",
                ["Send now", "Schedule for later"],
                horizontal=True
            )
            
            scheduled_time = None
            if send_option == "Schedule for later":
                col1, col2 = st.columns(2)
                with col1:
                    send_date = st.date_input("Send Date", min_value=datetime.now().date())
                with col2:
                    send_time = st.time_input("Send Time")
                scheduled_time = datetime.combine(send_date, send_time)
            
            # Preview and send
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Preview Campaign", type="secondary"):
                    self._show_campaign_preview(
                        campaign_name, subject_line, email_content, selected_lists
                    )
            
            with col2:
                if st.form_submit_button("Create Campaign", type="primary"):
                    if campaign_name and subject_line and email_content and selected_lists:
                        self._create_one_time_campaign(
                            campaign_name, subject_line, email_content,
                            selected_lists, sender_name, reply_to, scheduled_time                        )
                    else:
                        st.error("Please fill in all required fields")
    
    def _render_drip_campaign(self):
        """Render drip campaign builder."""
        
        # Email sequence management (outside form)
        st.subheader("📧 Drip Email Sequence Management")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ Add Email to Sequence"):
                if 'drip_emails' not in st.session_state:
                    st.session_state.drip_emails = []
                # Get current form values (simplified)
                st.session_state.drip_emails.append({
                    "subject": f"Email {len(st.session_state.drip_emails) + 1}",
                    "delay_days": len(st.session_state.drip_emails),
                    "template": "None",
                    "content": "",
                    "order": len(st.session_state.drip_emails) + 1                })
                st.success("Empty email added to sequence! Configure it in the form below.")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Remove Last Email") and 'drip_emails' in st.session_state and st.session_state.drip_emails:
                st.session_state.drip_emails.pop()
                st.success("Last email removed from sequence!")
                st.rerun()
        
        # Display current sequence (outside form for proper button handling)
        if st.session_state.get('drip_emails'):
            st.subheader("Current Email Sequence")
            for i, email in enumerate(st.session_state.drip_emails):
                col1, col2 = st.columns([4, 1])
                with col1:
                    with st.expander(f"Email {i+1}: {email['subject']} (Day {email['delay_days']})"):
                        st.text(f"Subject: {email['subject']}")
                        st.text(f"Send after: {email['delay_days']} days")
                        st.text(f"Template: {email['template']}")
                with col2:
                    if st.button(f"🗑️", key=f"remove_{i}", help=f"Remove Email {i+1}"):
                        st.session_state.drip_emails.pop(i)
                        st.success(f"Email {i+1} removed from sequence!")
                        st.rerun()
        
        st.markdown("---")
        
        with st.form("drip_campaign"):
            st.subheader("Create Drip Campaign")
            
            # Campaign details
            campaign_name = st.text_input("Drip Campaign Name*")
            description = st.text_area("Campaign Description")
            
            # Trigger settings
            st.subheader("Trigger Settings")
            trigger_type = st.selectbox(
                "Trigger Event",
                ["Contact Added", "Date/Time", "Contact Action", "Custom Event"]
            )
            
            # Email sequence
            st.subheader("Email Sequence")
            if "drip_emails" not in st.session_state:
                st.session_state.drip_emails = []
            
            # Add email to sequence
            with st.expander("Add Email to Sequence"):
                email_subject = st.text_input("Email Subject")
                email_delay = st.number_input("Send after (days)", min_value=0, value=0)
                
                templates = self.template_service.get_user_templates(st.session_state.user_id)
                template_options = ["None"] + [t["name"] for t in templates]
                email_template = st.selectbox("Template", template_options, key="drip_template")                
                email_content = st.text_area("Email Content", height=150)
                
                # Note: Use the buttons above the form to manage the email sequence
                st.info("💡 Use the 'Add Email to Sequence' button above to add emails, and individual remove buttons next to each email")
            
            # Target audience
            contact_lists = self.contact_service.get_contact_lists(st.session_state.user_id)
            target_lists = st.multiselect(
                "Target Contact Lists",
                [cl["name"] for cl in contact_lists]
            )
            
            # Create campaign
            if st.form_submit_button("Create Drip Campaign", type="primary"):
                if campaign_name and st.session_state.drip_emails and target_lists:
                    self._create_drip_campaign(
                        campaign_name, description, trigger_type,
                        st.session_state.drip_emails, target_lists
                    )
                    st.session_state.drip_emails = []  # Clear the sequence
                else:
                    st.error("Please fill in all required fields and add at least one email")
    
    def _render_ab_test_campaign(self):
        """Render A/B test campaign builder."""
        with st.form("ab_test_campaign"):
            st.subheader("Create A/B Test Campaign")
            
            # Campaign details
            campaign_name = st.text_input("A/B Test Campaign Name*")
            test_description = st.text_area("Test Description")
            
            # Test configuration
            st.subheader("Test Configuration")
            test_variable = st.selectbox(
                "What to test",
                ["Subject Line", "Email Content", "Send Time", "Sender Name"]
            )
            
            test_split = st.slider("Test Split (%)", 10, 50, 20)
            st.info(f"Version A: {test_split}%, Version B: {test_split}%, Winner: {100 - (test_split * 2)}%")
            
            # Version A
            st.subheader("Version A")
            if test_variable == "Subject Line":
                subject_a = st.text_input("Subject Line A*")
                subject_b = st.text_input("Subject Line B*")
                email_content = st.text_area("Email Content (shared)", height=200)
            elif test_variable == "Email Content":
                subject_line = st.text_input("Subject Line (shared)*")
                content_a = st.text_area("Email Content A*", height=150)
                content_b = st.text_area("Email Content B*", height=150)
            elif test_variable == "Sender Name":
                sender_a = st.text_input("Sender Name A*")
                sender_b = st.text_input("Sender Name B*")
                subject_line = st.text_input("Subject Line (shared)*")
                email_content = st.text_area("Email Content (shared)", height=200)
            
            # Test duration and winner criteria
            col1, col2 = st.columns(2)
            with col1:
                test_duration = st.number_input("Test Duration (hours)", min_value=1, value=24)
            with col2:
                winner_metric = st.selectbox(
                    "Winner Criteria",
                    ["Open Rate", "Click Rate", "Conversion Rate"]
                )
              # Target audience
            contact_lists = self.contact_service.get_contact_lists(st.session_state.user_id)
            
            # Handle case where contact_lists might not be a list
            if isinstance(contact_lists, list) and contact_lists:
                target_lists = st.multiselect(
                    "Target Contact Lists",
                    [cl["name"] for cl in contact_lists if isinstance(cl, dict) and "name" in cl]
                )
            else:
                st.info("No contact lists available. Please create contact lists first.")
                target_lists = []
            
            # Create A/B test
            if st.form_submit_button("Create A/B Test Campaign", type="primary"):
                if campaign_name and target_lists:
                    self._create_ab_test_campaign(
                        campaign_name, test_description, test_variable,
                        test_split, test_duration, winner_metric, target_lists
                    )
                else:
                    st.error("Please fill in all required fields")
    
    def _show_campaign_preview(self, name: str, subject: str, content: str, lists: List[str]):
        """Show campaign preview."""
        st.subheader("Campaign Preview")
        
        # Calculate recipient count
        total_contacts = 0
        for list_name in lists:
            contacts = self.contact_service.get_contacts_by_list(list_name, st.session_state.user_id)
            total_contacts += len(contacts)
        
        # Preview details
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Campaign Name", name)
            st.metric("Total Recipients", total_contacts)
        
        with col2:
            st.metric("Subject Line", subject)
            st.metric("Contact Lists", len(lists))
        
        # Content preview
        st.subheader("Email Content Preview")
        st.components.v1.html(content, height=400, scrolling=True)
    
    def _create_one_time_campaign(
        self, name: str, subject: str, content: str, lists: List[str],
        sender_name: str, reply_to: str, scheduled_time: Optional[datetime]
    ):
        """Create a one-time email campaign."""
        try:
            campaign_data = {
                "name": name,
                "subject": subject,
                "content": content,
                "contact_lists": lists,
                "sender_name": sender_name,
                "reply_to": reply_to,
                "scheduled_time": scheduled_time,
                "type": "one_time",
                "user_id": st.session_state.user_id
            }
            
            # Save campaign to database
            campaign_id = self.email_service.create_campaign(campaign_data)
            
            if scheduled_time:
                st.success(f"Campaign '{name}' scheduled for {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
            else:
                # Send immediately
                result = self.email_service.send_campaign(campaign_id)
                if result["success"]:
                    st.success(f"Campaign '{name}' sent successfully to {result['sent_count']} recipients!")
                else:
                    st.error(f"Campaign failed: {result['error']}")
            
            logger.info(f"One-time campaign created: {name}")
            
        except Exception as e:
            st.error(f"Failed to create campaign: {str(e)}")
            logger.error(f"Campaign creation failed: {str(e)}")
    
    def _create_drip_campaign(
        self, name: str, description: str, trigger_type: str,
        email_sequence: List[Dict], target_lists: List[str]
    ):
        """Create a drip email campaign."""
        try:
            campaign_data = {
                "name": name,
                "description": description,
                "trigger_type": trigger_type,
                "email_sequence": email_sequence,
                "target_lists": target_lists,
                "type": "drip",
                "user_id": st.session_state.user_id,
                "status": "active"
            }
            
            campaign_id = self.email_service.create_drip_campaign(campaign_data)
            st.success(f"Drip campaign '{name}' created successfully with {len(email_sequence)} emails!")
            
            logger.info(f"Drip campaign created: {name}")
            
        except Exception as e:
            st.error(f"Failed to create drip campaign: {str(e)}")
            logger.error(f"Drip campaign creation failed: {str(e)}")
    
    def _create_ab_test_campaign(
        self, name: str, description: str, test_variable: str,
        test_split: int, test_duration: int, winner_metric: str, target_lists: List[str]
    ):
        """Create an A/B test campaign."""
        try:
            campaign_data = {
                "name": name,
                "description": description,
                "test_variable": test_variable,
                "test_split": test_split,
                "test_duration": test_duration,
                "winner_metric": winner_metric,
                "target_lists": target_lists,
                "type": "ab_test",
                "user_id": st.session_state.user_id,
                "status": "active"
            }
            
            campaign_id = self.email_service.create_ab_test_campaign(campaign_data)
            st.success(f"A/B test campaign '{name}' created successfully!")
            
            logger.info(f"A/B test campaign created: {name}")
            
        except Exception as e:
            st.error(f"Failed to create A/B test campaign: {str(e)}")
            logger.error(f"A/B test campaign creation failed: {str(e)}")
    
    def render_campaign_management(self):
        """Render campaign management interface."""
        st.header("📊 Campaign Management")
        
        # Get user campaigns
        campaigns = self.email_service.get_user_campaigns(st.session_state.user_id)
        
        if not campaigns:
            st.info("No campaigns found. Create your first campaign above!")
            return
        
        # Campaign filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Paused", "Completed"])
        with col2:
            type_filter = st.selectbox("Filter by Type", ["All", "One-time", "Drip", "A/B Test"])
        with col3:
            sort_by = st.selectbox("Sort by", ["Created Date", "Name", "Status"])
        
        # Display campaigns
        for campaign in campaigns:
            if self._filter_campaign(campaign, status_filter, type_filter):
                self._render_campaign_card(campaign)
    
    def _filter_campaign(self, campaign: Dict, status_filter: str, type_filter: str) -> bool:
        """Filter campaigns based on status and type."""
        if status_filter != "All" and campaign.get("status", "").lower() != status_filter.lower():
            return False
        if type_filter != "All" and campaign.get("type", "").lower() != type_filter.lower().replace("-", "_"):
            return False
        return True
    
    def _render_campaign_card(self, campaign: Dict):
        """Render a campaign card."""
        with st.expander(f"{campaign['name']} ({campaign['type'].replace('_', ' ').title()})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Status", campaign.get("status", "Unknown"))
                st.metric("Type", campaign.get("type", "Unknown").replace("_", " ").title())
            
            with col2:
                st.metric("Recipients", campaign.get("recipient_count", 0))
                st.metric("Sent", campaign.get("sent_count", 0))
            
            with col3:
                st.metric("Opens", campaign.get("open_count", 0))
                st.metric("Clicks", campaign.get("click_count", 0))
            
            # Campaign actions
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("View Details", key=f"view_{campaign['id']}"):
                    self._show_campaign_details(campaign)
            
            with col2:
                if campaign.get("status") == "active":
                    if st.button("Pause", key=f"pause_{campaign['id']}"):
                        self._pause_campaign(campaign['id'])
                else:
                    if st.button("Resume", key=f"resume_{campaign['id']}"):
                        self._resume_campaign(campaign['id'])
            
            with col3:
                if st.button("Duplicate", key=f"duplicate_{campaign['id']}"):
                    self._duplicate_campaign(campaign['id'])
            
            with col4:
                if st.button("Delete", key=f"delete_{campaign['id']}"):
                    self._delete_campaign(campaign['id'])
    
    def _show_campaign_details(self, campaign: Dict):
        """Show detailed campaign information."""
        st.subheader(f"Campaign Details: {campaign['name']}")
        
        # Basic information
        col1, col2 = st.columns(2)
        with col1:
            st.text(f"Type: {campaign.get('type', 'Unknown').replace('_', ' ').title()}")
            st.text(f"Status: {campaign.get('status', 'Unknown')}")
            st.text(f"Created: {campaign.get('created_at', 'Unknown')}")
        
        with col2:
            st.text(f"Recipients: {campaign.get('recipient_count', 0)}")
            st.text(f"Sent: {campaign.get('sent_count', 0)}")
            st.text(f"Open Rate: {campaign.get('open_rate', 0):.1f}%")
        
        # Performance metrics
        if campaign.get('type') == 'ab_test':
            st.subheader("A/B Test Results")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Version A Open Rate", f"{campaign.get('version_a_open_rate', 0):.1f}%")
                st.metric("Version A Click Rate", f"{campaign.get('version_a_click_rate', 0):.1f}%")
            with col2:
                st.metric("Version B Open Rate", f"{campaign.get('version_b_open_rate', 0):.1f}%")
                st.metric("Version B Click Rate", f"{campaign.get('version_b_click_rate', 0):.1f}%")
    
    def _pause_campaign(self, campaign_id: str):
        """Pause a campaign."""
        try:
            self.email_service.pause_campaign(campaign_id)
            st.success("Campaign paused successfully!")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Failed to pause campaign: {str(e)}")
    
    def _resume_campaign(self, campaign_id: str):
        """Resume a campaign."""
        try:
            self.email_service.resume_campaign(campaign_id)
            st.success("Campaign resumed successfully!")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Failed to resume campaign: {str(e)}")
    
    def _duplicate_campaign(self, campaign_id: str):
        """Duplicate a campaign."""
        try:
            new_campaign_id = self.email_service.duplicate_campaign(campaign_id)
            st.success("Campaign duplicated successfully!")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Failed to duplicate campaign: {str(e)}")
    
    def _delete_campaign(self, campaign_id: str):
        """Delete a campaign."""
        if st.button("Confirm Delete", key=f"confirm_delete_{campaign_id}"):
            try:
                self.email_service.delete_campaign(campaign_id)
                st.success("Campaign deleted successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to delete campaign: {str(e)}")

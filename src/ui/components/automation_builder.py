"""
Automation Builder Component for creating email automation workflows.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from src.services.email_service import EmailService
from src.services.contact_service import ContactService
from src.services.template_service import TemplateService
from src.utils.session_state import initialize_session_state
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AutomationBuilder:
    def __init__(self):
        self.email_service = EmailService()
        self.contact_service = ContactService()
        self.template_service = TemplateService()
    
    def render(self):
        """Render the automation builder interface."""
        st.header("🤖 Email Automation Builder")
          # Automation type selection
        automation_type = st.selectbox(
            "Automation Type",
            ["Welcome Series", "Abandoned Cart", "Re-engagement", "Birthday/Anniversary", "Custom Workflow"],
            help="Choose the type of automation to create"
        )
        
        if automation_type == "Welcome Series":
            self._render_welcome_series()
        elif automation_type == "Abandoned Cart":
            self._render_abandoned_cart()
        elif automation_type == "Re-engagement":
            self._render_reengagement()
        elif automation_type == "Birthday/Anniversary":
            self._render_birthday_automation()
        elif automation_type == "Custom Workflow":
            self._render_custom_workflow()
    
    def _render_welcome_series(self):
        """Render welcome series automation builder."""
        
        # Email sequence management (outside form)
        st.subheader("📧 Email Sequence Management")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ Add Email to Sequence"):
                if 'welcome_emails' not in st.session_state:
                    st.session_state.welcome_emails = []
                st.session_state.welcome_emails.append({
                    "name": f"Email {len(st.session_state.welcome_emails) + 1}",
                    "delay": len(st.session_state.welcome_emails),
                    "subject": "",
                    "template": ""
                })
                st.rerun()
        
        with col2:
            if st.button("🗑️ Remove Last Email") and 'welcome_emails' in st.session_state and st.session_state.welcome_emails:
                st.session_state.welcome_emails.pop()
                st.rerun()
        
        st.markdown("---")
        
        with st.form("welcome_series"):
            st.subheader("Welcome Series Automation")
            
            # Basic settings
            col1, col2 = st.columns(2)
            with col1:
                automation_name = st.text_input("Automation Name*", value="Welcome Series")
                trigger_event = st.selectbox("Trigger Event", ["Contact Subscribes", "Contact Added to List"])
            
            with col2:
                active_status = st.checkbox("Active", value=True)
                delay_between_emails = st.number_input("Days between emails", min_value=1, value=3)
            
            # Welcome email sequence
            st.subheader("Welcome Email Sequence")
            
            if "welcome_emails" not in st.session_state:
                st.session_state.welcome_emails = [
                    {"name": "Welcome Email", "delay": 0, "subject": "Welcome to our newsletter!", "template": ""},
                    {"name": "Getting Started", "delay": 3, "subject": "Getting started guide", "template": ""},
                    {"name": "Tips & Tricks", "delay": 5, "subject": "Pro tips for success", "template": ""}
                ]
            
            # Display and edit email sequence
            for i, email in enumerate(st.session_state.welcome_emails):
                with st.expander(f"Email {i+1}: {email['name']} (Day {email['delay']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        email['name'] = st.text_input(f"Email Name {i+1}", value=email['name'], key=f"welcome_name_{i}")
                        email['subject'] = st.text_input(f"Subject Line {i+1}", value=email['subject'], key=f"welcome_subject_{i}")
                    
                    with col2:
                        email['delay'] = st.number_input(f"Send after (days) {i+1}", min_value=0, value=email['delay'], key=f"welcome_delay_{i}")                        
                        templates = self.template_service.get_user_templates(st.session_state.user_id)
                        template_options = ["None"] + [t["name"] for t in templates]
                        email['template'] = st.selectbox(f"Template {i+1}", template_options, key=f"welcome_template_{i}")
                    
                    # Note: Email management is handled through form submission
                    st.info(f"Email {i+1} configured - Use form submission to save changes")
              # Note about adding emails
            st.info("💡 To add more emails to the sequence, use the form submit button below and then return to edit")
            # Removed dynamic add/remove buttons as they cannot be used within forms
            
            # Target audience
            contact_lists = self.contact_service.get_contact_lists(st.session_state.user_id)
            target_lists = st.multiselect(
                "Apply to Contact Lists",
                [cl["name"] for cl in contact_lists],
                help="Select which contact lists this automation applies to"
            )
            
            # Advanced settings
            with st.expander("Advanced Settings"):
                send_time = st.time_input("Preferred Send Time", value=datetime.strptime("09:00", "%H:%M").time())
                timezone = st.selectbox("Timezone", ["UTC", "US/Eastern", "US/Pacific", "Europe/London"])
                stop_on_reply = st.checkbox("Stop automation if recipient replies", value=True)
                stop_on_unsubscribe = st.checkbox("Stop automation if recipient unsubscribes", value=True)
            
            # Create automation
            if st.form_submit_button("Create Welcome Series", type="primary"):
                if automation_name and st.session_state.welcome_emails and target_lists:
                    self._create_welcome_series(
                        automation_name, st.session_state.welcome_emails, target_lists,
                        trigger_event, active_status, send_time, timezone, stop_on_reply, stop_on_unsubscribe
                    )
                else:
                    st.error("Please fill in all required fields")
    
    def _render_abandoned_cart(self):
        """Render abandoned cart automation builder."""
        with st.form("abandoned_cart"):
            st.subheader("Abandoned Cart Recovery")
            
            # Basic settings
            col1, col2 = st.columns(2)
            with col1:
                automation_name = st.text_input("Automation Name*", value="Abandoned Cart Recovery")
                cart_timeout = st.number_input("Cart abandoned after (hours)", min_value=1, value=24)
            
            with col2:
                active_status = st.checkbox("Active", value=True)
                max_emails = st.number_input("Maximum emails to send", min_value=1, max_value=5, value=3)
            
            # Recovery email sequence
            st.subheader("Recovery Email Sequence")
            
            if "cart_emails" not in st.session_state:
                st.session_state.cart_emails = [
                    {"name": "Cart Reminder", "delay": 1, "subject": "You forgot something in your cart", "discount": 0},
                    {"name": "Special Offer", "delay": 24, "subject": "10% off your cart items", "discount": 10},
                    {"name": "Last Chance", "delay": 72, "subject": "Last chance - your cart expires soon", "discount": 15}
                ]
            
            for i, email in enumerate(st.session_state.cart_emails):
                with st.expander(f"Email {i+1}: {email['name']} (After {email['delay']} hours)"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        email['name'] = st.text_input(f"Email Name {i+1}", value=email['name'], key=f"cart_name_{i}")
                        email['subject'] = st.text_input(f"Subject Line {i+1}", value=email['subject'], key=f"cart_subject_{i}")
                    
                    with col2:
                        email['delay'] = st.number_input(f"Send after (hours) {i+1}", min_value=1, value=email['delay'], key=f"cart_delay_{i}")
                        email['discount'] = st.number_input(f"Discount % {i+1}", min_value=0, max_value=50, value=email['discount'], key=f"cart_discount_{i}")
                    
                    with col3:
                        templates = self.template_service.get_user_templates(st.session_state.user_id)
                        template_options = ["None"] + [t["name"] for t in templates]
                        email['template'] = st.selectbox(f"Template {i+1}", template_options, key=f"cart_template_{i}")
            
            # Integration settings
            st.subheader("E-commerce Integration")
            platform = st.selectbox("E-commerce Platform", ["Shopify", "WooCommerce", "Magento", "Custom API"])
            api_key = st.text_input("API Key", type="password")
            webhook_url = st.text_input("Webhook URL", help="URL to receive cart abandonment events")
            
            # Create automation
            if st.form_submit_button("Create Abandoned Cart Automation", type="primary"):
                if automation_name and st.session_state.cart_emails:
                    self._create_abandoned_cart_automation(
                        automation_name, st.session_state.cart_emails, cart_timeout,
                        active_status, platform, api_key, webhook_url
                    )
                else:
                    st.error("Please fill in all required fields")
    
    def _render_reengagement(self):
        """Render re-engagement automation builder."""
        with st.form("reengagement"):
            st.subheader("Re-engagement Campaign")
            
            # Basic settings
            col1, col2 = st.columns(2)
            with col1:
                automation_name = st.text_input("Automation Name*", value="Re-engagement Campaign")
                inactive_period = st.number_input("Inactive period (days)", min_value=30, value=90)
            
            with col2:
                active_status = st.checkbox("Active", value=True)
                cleanup_after = st.number_input("Remove non-responsive contacts after (days)", min_value=30, value=180)
            
            # Re-engagement sequence
            st.subheader("Re-engagement Email Sequence")
            
            if "reengagement_emails" not in st.session_state:
                st.session_state.reengagement_emails = [
                    {"name": "We Miss You", "delay": 0, "subject": "We miss you! Here's what you've been missing", "incentive": ""},
                    {"name": "Special Offer", "delay": 7, "subject": "Exclusive offer just for you", "incentive": "20% Discount"},
                    {"name": "Final Goodbye", "delay": 14, "subject": "Is this goodbye?", "incentive": ""}
                ]
            
            for i, email in enumerate(st.session_state.reengagement_emails):
                with st.expander(f"Email {i+1}: {email['name']} (Day {email['delay']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        email['name'] = st.text_input(f"Email Name {i+1}", value=email['name'], key=f"reeng_name_{i}")
                        email['subject'] = st.text_input(f"Subject Line {i+1}", value=email['subject'], key=f"reeng_subject_{i}")
                    
                    with col2:
                        email['delay'] = st.number_input(f"Send after (days) {i+1}", min_value=0, value=email['delay'], key=f"reeng_delay_{i}")
                        email['incentive'] = st.text_input(f"Incentive/Offer {i+1}", value=email['incentive'], key=f"reeng_incentive_{i}")
            
            # Segmentation
            st.subheader("Audience Segmentation")
            engagement_criteria = st.multiselect(
                "Include contacts who haven't:",
                ["Opened any email", "Clicked any link", "Visited website", "Made a purchase"],
                default=["Opened any email"]
            )
            
            exclude_lists = st.multiselect(
                "Exclude contact lists",
                [cl["name"] for cl in self.contact_service.get_contact_lists(st.session_state.user_id)]
            )
            
            # Create automation
            if st.form_submit_button("Create Re-engagement Campaign", type="primary"):
                if automation_name and st.session_state.reengagement_emails:
                    self._create_reengagement_automation(
                        automation_name, st.session_state.reengagement_emails, inactive_period,
                        cleanup_after, engagement_criteria, exclude_lists, active_status
                    )
                else:
                    st.error("Please fill in all required fields")
    
    def _render_birthday_automation(self):
        """Render birthday/anniversary automation builder."""
        with st.form("birthday_automation"):
            st.subheader("Birthday & Anniversary Automation")
            
            # Basic settings
            col1, col2 = st.columns(2)
            with col1:
                automation_name = st.text_input("Automation Name*", value="Birthday Campaign")
                automation_type = st.selectbox("Occasion Type", ["Birthday", "Anniversary", "Custom Date"])
            
            with col2:
                active_status = st.checkbox("Active", value=True)
                send_days_before = st.number_input("Send days before occasion", min_value=0, value=0)
            
            # Email content
            st.subheader("Birthday Email")
            col1, col2 = st.columns(2)
            with col1:
                email_subject = st.text_input("Subject Line", value="Happy Birthday! 🎉")
                sender_name = st.text_input("Sender Name", value="Your Company")
            
            with col2:
                birthday_discount = st.number_input("Birthday Discount (%)", min_value=0, max_value=50, value=15)
                discount_expires = st.number_input("Discount expires after (days)", min_value=1, value=7)
            
            # Template selection
            templates = self.template_service.get_user_templates(st.session_state.user_id)
            template_options = ["None"] + [t["name"] for t in templates]
            selected_template = st.selectbox("Email Template", template_options)
            
            # Personalization options
            st.subheader("Personalization")
            include_age = st.checkbox("Include age in email (if available)")
            include_name = st.checkbox("Include name in subject line", value=True)
            custom_message = st.text_area("Custom birthday message")
            
            # Target audience
            contact_lists = self.contact_service.get_contact_lists(st.session_state.user_id)
            target_lists = st.multiselect(
                "Target Contact Lists",
                [cl["name"] for cl in contact_lists],
                help="Only contacts with birthday data will receive emails"
            )
            
            # Create automation
            if st.form_submit_button("Create Birthday Automation", type="primary"):
                if automation_name and email_subject and target_lists:
                    self._create_birthday_automation(
                        automation_name, automation_type, email_subject, sender_name,
                        birthday_discount, discount_expires, selected_template,
                        include_age, include_name, custom_message, target_lists,
                        active_status, send_days_before
                    )
                else:
                    st.error("Please fill in all required fields")
    
    def _render_custom_workflow(self):
        """Render custom workflow builder."""
        st.subheader("Custom Workflow Builder")
        
        # Initialize workflow state
        if "workflow_steps" not in st.session_state:
            st.session_state.workflow_steps = []
        
        # Workflow settings
        col1, col2 = st.columns(2)
        with col1:
            workflow_name = st.text_input("Workflow Name*")
            workflow_description = st.text_area("Description")
        
        with col2:
            active_status = st.checkbox("Active")
            trigger_type = st.selectbox("Trigger", ["Contact Action", "Date/Time", "External Event", "Manual"])
        
        # Workflow builder interface
        st.subheader("Workflow Steps")
        
        # Add step interface
        with st.expander("Add New Step"):
            step_type = st.selectbox("Step Type", ["Send Email", "Wait", "Condition", "Update Contact", "Add Tag", "Remove Tag"])
            
            if step_type == "Send Email":
                self._render_email_step()
            elif step_type == "Wait":
                self._render_wait_step()
            elif step_type == "Condition":
                self._render_condition_step()
            elif step_type == "Update Contact":
                self._render_update_contact_step()
            elif step_type in ["Add Tag", "Remove Tag"]:
                self._render_tag_step(step_type)
        
        # Display current workflow steps
        if st.session_state.workflow_steps:
            st.subheader("Current Workflow")
            for i, step in enumerate(st.session_state.workflow_steps):
                self._render_workflow_step_card(i, step)
        
        # Save workflow
        if st.button("Save Custom Workflow", type="primary"):
            if workflow_name and st.session_state.workflow_steps:
                self._save_custom_workflow(workflow_name, workflow_description, trigger_type, active_status)
            else:
                st.error("Please provide a workflow name and add at least one step")
    
    def _render_email_step(self):
        """Render email step configuration."""
        col1, col2 = st.columns(2)
        with col1:
            email_subject = st.text_input("Email Subject")
            sender_name = st.text_input("Sender Name")
        
        with col2:
            templates = self.template_service.get_user_templates(st.session_state.user_id)
            template_options = ["None"] + [t["name"] for t in templates]
            email_template = st.selectbox("Template", template_options)
        
        if st.button("Add Email Step"):
            step = {
                "type": "Send Email",
                "subject": email_subject,
                "sender_name": sender_name,
                "template": email_template,
                "order": len(st.session_state.workflow_steps)
            }
            st.session_state.workflow_steps.append(step)
            st.success("Email step added!")
    
    def _render_wait_step(self):
        """Render wait step configuration."""
        col1, col2 = st.columns(2)
        with col1:
            wait_duration = st.number_input("Wait Duration", min_value=1, value=1)
            wait_unit = st.selectbox("Time Unit", ["Minutes", "Hours", "Days", "Weeks"])
        
        with col2:
            wait_condition = st.selectbox("Wait Until", ["Time Passes", "Contact Opens Email", "Contact Clicks Link"])
        
        if st.button("Add Wait Step"):
            step = {
                "type": "Wait",
                "duration": wait_duration,
                "unit": wait_unit,
                "condition": wait_condition,
                "order": len(st.session_state.workflow_steps)
            }
            st.session_state.workflow_steps.append(step)
            st.success("Wait step added!")
    
    def _render_condition_step(self):
        """Render condition step configuration."""
        condition_field = st.selectbox("Condition Field", ["Email Opened", "Link Clicked", "Tag", "Custom Field"])
        condition_operator = st.selectbox("Operator", ["Equals", "Not Equals", "Contains", "Greater Than", "Less Than"])
        condition_value = st.text_input("Value")
        
        if st.button("Add Condition Step"):
            step = {
                "type": "Condition",
                "field": condition_field,
                "operator": condition_operator,
                "value": condition_value,
                "order": len(st.session_state.workflow_steps)
            }
            st.session_state.workflow_steps.append(step)
            st.success("Condition step added!")
    
    def _render_workflow_step_card(self, index: int, step: Dict):
        """Render a workflow step card."""
        with st.container():
            col1, col2, col3 = st.columns([6, 1, 1])
            
            with col1:
                st.write(f"**Step {index + 1}: {step['type']}**")
                if step['type'] == "Send Email":
                    st.write(f"Subject: {step.get('subject', 'N/A')}")
                elif step['type'] == "Wait":
                    st.write(f"Duration: {step.get('duration', 'N/A')} {step.get('unit', 'N/A')}")
                elif step['type'] == "Condition":
                    st.write(f"Condition: {step.get('field', 'N/A')} {step.get('operator', 'N/A')} {step.get('value', 'N/A')}")
            
            with col2:
                if st.button("↑", key=f"up_{index}") and index > 0:
                    st.session_state.workflow_steps[index], st.session_state.workflow_steps[index-1] = \
                        st.session_state.workflow_steps[index-1], st.session_state.workflow_steps[index]
                    st.experimental_rerun()
            
            with col3:
                if st.button("🗑️", key=f"delete_{index}"):
                    st.session_state.workflow_steps.pop(index)
                    st.experimental_rerun()
            
            st.divider()
    
    def render_automation_management(self):
        """Render automation management interface."""
        st.header("⚡ Active Automations")
        
        # Get user automations
        automations = self.email_service.get_user_automations(st.session_state.user_id)
        
        if not automations:
            st.info("No automations found. Create your first automation above!")
            return
        
        # Automation filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Paused", "Draft"])
        with col2:
            type_filter = st.selectbox("Filter by Type", ["All", "Welcome Series", "Abandoned Cart", "Re-engagement", "Birthday", "Custom"])
        with col3:
            sort_by = st.selectbox("Sort by", ["Created Date", "Name", "Performance"])
        
        # Display automations
        for automation in automations:
            if self._filter_automation(automation, status_filter, type_filter):
                self._render_automation_card(automation)
    
    def _render_automation_card(self, automation: Dict):
        """Render an automation card."""
        with st.expander(f"{automation['name']} ({automation['type']})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Status", automation.get("status", "Unknown"))
                st.metric("Type", automation.get("type", "Unknown"))
            
            with col2:
                st.metric("Active Contacts", automation.get("active_contacts", 0))
                st.metric("Emails Sent", automation.get("emails_sent", 0))
            
            with col3:
                st.metric("Avg Open Rate", f"{automation.get('avg_open_rate', 0):.1f}%")
                st.metric("Avg Click Rate", f"{automation.get('avg_click_rate', 0):.1f}%")
            
            # Automation actions
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("View Details", key=f"view_auto_{automation['id']}"):
                    self._show_automation_details(automation)
            
            with col2:
                if automation.get("status") == "active":
                    if st.button("Pause", key=f"pause_auto_{automation['id']}"):
                        self._pause_automation(automation['id'])
                else:
                    if st.button("Activate", key=f"activate_auto_{automation['id']}"):
                        self._activate_automation(automation['id'])
            
            with col3:
                if st.button("Edit", key=f"edit_auto_{automation['id']}"):
                    self._edit_automation(automation['id'])
            
            with col4:
                if st.button("Delete", key=f"delete_auto_{automation['id']}"):
                    self._delete_automation(automation['id'])
    
    # Helper methods for automation actions
    def _create_welcome_series(self, name, emails, target_lists, trigger, active, send_time, timezone, stop_on_reply, stop_on_unsubscribe):
        """Create welcome series automation."""
        try:
            automation_data = {
                "name": name,
                "type": "welcome_series",
                "emails": emails,
                "target_lists": target_lists,
                "trigger": trigger,
                "active": active,
                "send_time": send_time.strftime("%H:%M"),
                "timezone": timezone,
                "stop_on_reply": stop_on_reply,
                "stop_on_unsubscribe": stop_on_unsubscribe,
                "user_id": st.session_state.user_id
            }
            
            automation_id = self.email_service.create_automation(automation_data)
            st.success(f"Welcome series '{name}' created successfully!")
            st.session_state.welcome_emails = []  # Clear the session
            
        except Exception as e:
            st.error(f"Failed to create welcome series: {str(e)}")
            logger.error(f"Welcome series creation failed: {str(e)}")
    
    def _filter_automation(self, automation, status_filter, type_filter):
        """Filter automations based on criteria."""
        if status_filter != "All" and automation.get("status") != status_filter.lower():
            return False
        if type_filter != "All" and automation.get("type") != type_filter.lower().replace(" ", "_"):
            return False
        return True

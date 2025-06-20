import streamlit as st
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

from src.services.contact_service import ContactService
from src.utils.session_state import save_form_data, get_form_data

class ContactManager:
    """Contact management component"""
    
    def __init__(self):
        self.contact_service = ContactService()
    
    def render(self):
        """Render the contact management interface"""
        
        # Tabs for different contact operations
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 All Contacts", "➕ Add Contact", "📂 Contact Lists", "📊 Import/Export"
        ])
        
        with tab1:
            self._render_contacts_list()
        
        with tab2:
            self._render_add_contact_form()
        
        with tab3:
            self._render_contact_lists()
        
        with tab4:
            self._render_import_export()
    
    def _render_contacts_list(self):
        """Render contacts list with filtering and pagination"""
        
        st.subheader("📋 All Contacts")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_filter = st.selectbox(
                "Status",
                ["All", "Active", "Unsubscribed", "Bounced"],
                key="contact_status_filter"
            )
        
        with col2:
            search_term = st.text_input(
                "🔍 Search",
                placeholder="Search contacts...",
                key="contact_search"
            )
        
        with col3:
            per_page = st.selectbox(
                "Per Page",
                [25, 50, 100],
                key="contacts_per_page"
            )
        
        with col4:
            page = st.number_input(
                "Page",
                min_value=1,
                value=1,
                key="contacts_page"
            )
        
        # Apply filters button
        if st.button("🔍 Apply Filters", key="apply_contact_filters"):
            st.session_state.contact_filters = {
                'status': status_filter.lower() if status_filter != "All" else None,
                'search': search_term if search_term else None
            }
        
        # Get contacts
        filters = st.session_state.get('contact_filters', {})
        
        contacts_result = self.contact_service.get_contacts(
            user_id=st.session_state.user_id,
            page=page,
            per_page=per_page,
            filters=filters
        )
        
        if contacts_result['success']:
            contacts = contacts_result['contacts']
            pagination = contacts_result['pagination']
            
            if contacts:
                # Display contacts in a table-like format
                for idx, contact in enumerate(contacts):
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        
                        with col1:
                            st.markdown(f"""
                            **{contact['first_name']} {contact['last_name']}**  
                            📧 {contact['email']}  
                            🏢 {contact['company'] or 'N/A'}
                            """)
                        
                        with col2:
                            status_color = {
                                'active': '🟢',
                                'unsubscribed': '🔴',
                                'bounced': '🟡'
                            }.get(contact['status'], '⚪')
                            
                            st.markdown(f"""
                            {status_color} **{contact['status'].title()}**  
                            📅 Added: {contact['created_at']}
                            """)
                        
                        with col3:
                            # Contact tags
                            if contact['tags']:
                                tags_str = ', '.join(contact['tags'][:3])
                                if len(contact['tags']) > 3:
                                    tags_str += f" +{len(contact['tags']) - 3} more"
                                st.markdown(f"🏷️ {tags_str}")
                            else:
                                st.markdown("🏷️ No tags")
                        
                        with col4:
                            # Action buttons
                            if st.button("✏️", key=f"edit_contact_{contact['id']}", help="Edit"):
                                st.session_state.edit_contact_id = contact['id']
                                st.rerun()
                            
                            if st.button("🗑️", key=f"delete_contact_{contact['id']}", help="Delete"):
                                if st.session_state.get(f"confirm_delete_{contact['id']}", False):
                                    # Perform deletion
                                    result = self.contact_service.delete_contact(
                                        st.session_state.user_id, contact['id']
                                    )
                                    if result['success']:
                                        st.success("Contact deleted successfully!")
                                        st.rerun()
                                    else:
                                        st.error(f"Error: {result['error']}")
                                else:
                                    st.session_state[f"confirm_delete_{contact['id']}"] = True
                                    st.warning("Click again to confirm deletion")
                        
                        st.markdown("---")
                
                # Pagination info
                st.markdown(f"""
                **Showing {len(contacts)} of {pagination['total_count']} contacts**  
                Page {pagination['page']} of {pagination['total_pages']}
                """)
                
            else:
                st.info("No contacts found matching your criteria.")
        
        else:
            st.error(f"Error loading contacts: {contacts_result['error']}")
        
        # Handle edit contact modal
        if st.session_state.get('edit_contact_id'):
            self._render_edit_contact_modal()
    
    def _render_add_contact_form(self):
        """Render add contact form"""
        
        st.subheader("➕ Add New Contact")
        
        with st.form("add_contact_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name")
                email = st.text_input("Email Address *", placeholder="contact@example.com")
                company = st.text_input("Company")
            
            with col2:
                last_name = st.text_input("Last Name")
                phone = st.text_input("Phone Number")
                source = st.selectbox("Source", ["Manual", "Import", "Website", "API"])
            
            # Tags
            tags_input = st.text_input("Tags (comma separated)", placeholder="tag1, tag2, tag3")
            
            # Custom fields
            st.subheader("Custom Fields")
            custom_fields = {}
            
            col1, col2 = st.columns(2)
            with col1:
                custom_field_1_name = st.text_input("Custom Field 1 Name")
                custom_field_1_value = st.text_input("Custom Field 1 Value")
            
            with col2:
                custom_field_2_name = st.text_input("Custom Field 2 Name")
                custom_field_2_value = st.text_input("Custom Field 2 Value")
            
            # Build custom fields dict
            if custom_field_1_name and custom_field_1_value:
                custom_fields[custom_field_1_name] = custom_field_1_value
            
            if custom_field_2_name and custom_field_2_value:
                custom_fields[custom_field_2_name] = custom_field_2_value
            
            submitted = st.form_submit_button("Add Contact", use_container_width=True)
            
            if submitted:
                # Validate required fields
                if not email:
                    st.error("Email address is required")
                else:
                    # Process tags
                    tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()] if tags_input else []
                    
                    contact_data = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'phone': phone,
                        'company': company,
                        'source': source.lower(),
                        'tags': tags,
                        'custom_fields': custom_fields
                    }
                    
                    result = self.contact_service.add_contact(st.session_state.user_id, contact_data)
                    
                    if result['success']:
                        st.success("Contact added successfully!")
                        # Clear form by rerunning
                        st.rerun()
                    else:
                        st.error(f"Error: {result['error']}")
    
    def _render_contact_lists(self):
        """Render contact lists management"""
        
        st.subheader("📂 Contact Lists")
          # Get existing contact lists
        contact_lists = self.contact_service.get_contact_lists(st.session_state.user_id)
        
        if contact_lists:
            
            # Create new list form
            with st.expander("➕ Create New List"):
                with st.form("create_list_form"):
                    list_name = st.text_input("List Name *")
                    list_description = st.text_area("Description")
                    list_tags = st.text_input("Tags (comma separated)")
                    
                    if st.form_submit_button("Create List"):
                        if not list_name:
                            st.error("List name is required")
                        else:
                            tags = [tag.strip() for tag in list_tags.split(',') if tag.strip()] if list_tags else []
                            
                            list_data = {
                                'name': list_name,
                                'description': list_description,
                                'tags': tags
                            }
                            
                            result = self.contact_service.create_contact_list(
                                st.session_state.user_id, list_data
                            )
                            
                            if result['success']:
                                st.success("Contact list created successfully!")
                                st.rerun()
                            else:
                                st.error(f"Error: {result['error']}")
              # Display existing lists
            if contact_lists:
                for contact_list in contact_lists:
                    with st.container():
                        st.markdown(f"""
                        <div class="campaign-card">
                            <h4>📂 {contact_list['name']}</h4>
                            <p><strong>Description:</strong> {contact_list.get('description', 'No description')}</p>
                            <p><strong>Contacts:</strong> {contact_list.get('count', contact_list.get('contact_count', 0))}</p>
                            <p><strong>Created:</strong> {contact_list.get('created_at', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("👁️ View", key=f"view_list_{contact_list['id']}"):
                                st.session_state.view_list_id = contact_list['id']
                        
                        with col2:
                            if st.button("➕ Add Contacts", key=f"add_to_list_{contact_list['id']}"):
                                st.session_state.add_to_list_id = contact_list['id']
                        
                        with col3:
                            if st.button("✏️ Edit", key=f"edit_list_{contact_list['id']}"):
                                st.session_state.edit_list_id = contact_list['id']
                        
                        st.markdown("---")
            else:                st.info("No contact lists created yet.")
        
        else:
            st.error("Error loading contact lists")
    
    def _render_import_export(self):
        """Render import/export functionality"""
        
        st.subheader("📊 Import & Export Contacts")
        
        # Import section
        st.markdown("### 📥 Import Contacts")
        
        import_method = st.radio(
            "Import Method",
            ["CSV Upload", "Paste Text"],
            key="import_method"
        )
        
        if import_method == "CSV Upload":
            uploaded_file = st.file_uploader(
                "Choose CSV file",
                type=['csv'],
                help="CSV should contain at least an 'email' column"
            )
            
            if uploaded_file is not None:
                # Preview CSV
                try:
                    df = pd.read_csv(uploaded_file)
                    st.markdown("**Preview:**")
                    st.dataframe(df.head())
                    
                    # Show column mapping
                    st.markdown("**Column Mapping:**")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Required columns found:**")
                        required_cols = ['email']
                        for col in required_cols:
                            if col in df.columns:
                                st.success(f"✅ {col}")
                            else:
                                st.error(f"❌ {col}")
                    
                    with col2:
                        st.markdown("**Optional columns found:**")
                        optional_cols = ['first_name', 'last_name', 'company', 'phone']
                        for col in optional_cols:
                            if col in df.columns:
                                st.info(f"📝 {col}")
                    
                    if st.button("Import Contacts"):
                        # Convert to CSV string
                        csv_content = uploaded_file.getvalue().decode('utf-8')
                        
                        result = self.contact_service.import_contacts_from_csv(
                            st.session_state.user_id, csv_content, 'csv_upload'
                        )
                        
                        if result['success']:
                            st.success(f"""
                            Import completed!
                            - Imported: {result['imported_count']} contacts
                            - Skipped: {result['skipped_count']} contacts
                            - Total processed: {result['total_processed']} contacts
                            """)
                            
                            if result['errors']:
                                with st.expander("View Errors"):
                                    for error in result['errors']:
                                        st.warning(error)
                        else:
                            st.error(f"Import failed: {result['error']}")
                
                except Exception as e:
                    st.error(f"Error reading CSV file: {str(e)}")
        
        else:  # Paste Text
            st.markdown("Paste contact data (one email per line or CSV format):")
            text_data = st.text_area(
                "Contact Data",
                height=200,
                placeholder="email@example.com\ncontact@company.com\n..."
            )
            
            if st.button("Import from Text") and text_data:
                # Convert text to CSV format
                lines = text_data.strip().split('\n')
                csv_content = "email\n" + '\n'.join(lines)
                
                result = self.contact_service.import_contacts_from_csv(
                    st.session_state.user_id, csv_content, 'text_import'
                )
                
                if result['success']:
                    st.success(f"Imported {result['imported_count']} contacts successfully!")
                else:
                    st.error(f"Import failed: {result['error']}")
        
        # Export section
        st.markdown("### 📤 Export Contacts")
        
        export_format = st.selectbox("Export Format", ["CSV", "Excel"])
        export_filters = st.multiselect(
            "Export Filters",
            ["Active only", "Include custom fields", "Include tags"]
        )
        
        if st.button("Export Contacts"):
            result = self.contact_service.export_contacts(
                st.session_state.user_id,
                format=export_format.lower()
            )
            
            if result['success']:
                st.success("Export ready!")
                st.download_button(
                    label="Download Export",
                    data=result['content'],
                    file_name=result['filename'],
                    mime='text/csv'
                )
            else:
                st.error(f"Export failed: {result['error']}")
    
    def _render_edit_contact_modal(self):
        """Render edit contact modal"""
        
        contact_id = st.session_state.edit_contact_id
        
        # This would typically use a modal, but Streamlit doesn't have native modals
        # Using an expander as a workaround
        with st.expander("✏️ Edit Contact", expanded=True):
            # Get contact details first
            # For now, using a placeholder form
            
            with st.form("edit_contact_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    first_name = st.text_input("First Name", value="")
                    email = st.text_input("Email Address", value="")
                    company = st.text_input("Company", value="")
                
                with col2:
                    last_name = st.text_input("Last Name", value="")
                    phone = st.text_input("Phone", value="")
                    status = st.selectbox("Status", ["active", "unsubscribed", "bounced"])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("Update Contact"):
                        # Update contact logic here
                        st.success("Contact updated successfully!")
                        del st.session_state.edit_contact_id
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        del st.session_state.edit_contact_id
                        st.rerun()

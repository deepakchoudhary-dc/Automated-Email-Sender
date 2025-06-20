import streamlit as st
from datetime import datetime
from typing import Dict, List, Any

from src.services.template_service import TemplateService
from src.ui.components.ai_helper import AIHelper
from src.utils.session_state import save_form_data, get_form_data

class TemplateEditor:
    """Template editor component"""
    
    def __init__(self):
        self.template_service = TemplateService()
        self.ai_helper = AIHelper()
    
    def render(self):
        """Render the template editor interface"""
        
        # Check if editing existing template
        if st.session_state.get('edit_template'):
            self._render_edit_template()
        else:
            self._render_create_template()
    
    def _render_create_template(self):
        """Render create new template form"""
        
        st.subheader("➕ Create New Template")
        
        # Template creation method
        creation_method = st.radio(
            "How would you like to create your template?",
            ["Start from scratch", "Use predefined template", "Import HTML"],
            key="template_creation_method"
        )
        
        if creation_method == "Start from scratch":
            self._render_template_form()
        
        elif creation_method == "Use predefined template":
            self._render_predefined_templates()
        
        else:  # Import HTML
            self._render_html_import()
    
    def _render_template_form(self, template_data: Dict = None):
        """Render template creation/edit form"""
        
        # Get saved form data
        form_data = get_form_data('template_editor') if not template_data else template_data
        
        with st.form("template_form"):
            # Basic information
            st.markdown("### 📝 Basic Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(
                    "Template Name *",
                    value=form_data.get('name', ''),
                    placeholder="e.g., Welcome Email"
                )
                
                category = st.selectbox(
                    "Category",
                    ["General", "Welcome", "Newsletter", "Promotional", "Transactional", "Other"],
                    index=0 if not form_data.get('category') else 
                          ["general", "welcome", "newsletter", "promotional", "transactional", "other"].index(form_data.get('category', 'general'))
                )
            
            with col2:
                subject = st.text_input(
                    "Email Subject *",
                    value=form_data.get('subject', ''),
                    placeholder="e.g., Welcome to {{company}}!"
                )
                
                is_public = st.checkbox(
                    "Make template public",
                    value=form_data.get('is_public', False),
                    help="Public templates can be used by other users"
                )
              # Content creation
            st.markdown("### 🎨 Email Content")
            
            # Content editor tabs
            content_tab1, content_tab2, content_tab3, content_tab4 = st.tabs(["📝 Visual Editor", "💻 HTML Editor", "📋 Text Version", "🤖 AI Assistant"])
            
            with content_tab1:
                # Visual editor (simplified)
                st.markdown("**Visual Email Builder**")
                
                # Header section
                with st.expander("📍 Header Section"):
                    header_type = st.selectbox("Header Type", ["None", "Text Only", "Logo + Text", "Image Banner"])
                    
                    if header_type != "None":
                        header_text = st.text_input("Header Text", value="{{company}}")
                        if header_type in ["Logo + Text", "Image Banner"]:
                            header_image = st.text_input("Image URL", placeholder="https://example.com/logo.png")
                
                # Body sections
                with st.expander("📄 Body Content"):
                    body_sections = st.number_input("Number of sections", min_value=1, max_value=5, value=2)
                    
                    sections_content = []
                    for i in range(int(body_sections)):
                        st.markdown(f"**Section {i+1}**")
                        section_title = st.text_input(f"Section {i+1} Title", key=f"section_title_{i}")
                        section_content = st.text_area(f"Section {i+1} Content", key=f"section_content_{i}")
                        sections_content.append({
                            'title': section_title,
                            'content': section_content
                        })
                  # Footer section
                with st.expander("📍 Footer Section"):
                    footer_text = st.text_area(
                        "Footer Content",
                        value="© 2025 {{company}}. All rights reserved.\n\n[Unsubscribe]({{unsubscribe_url}})"
                    )
                
                # Note about HTML generation
                st.info("� Use the 'Generate HTML' button below the form to create HTML from this visual editor.")
            with content_tab2:
                # HTML editor
                html_content = st.text_area(
                    "HTML Content",
                    value=st.session_state.get('generated_html', form_data.get('html_content', self._get_default_html_template())),
                    height=400,
                    help="Use {{variable}} for personalization (e.g., {{first_name}}, {{company}})"
                )
                
                # Note about validation
                st.info("💡 Use the 'Validate HTML' button below the form to check your HTML.")
                
                with content_tab3:
                    # Text version
                    text_content = st.text_area(
                        "Plain Text Version",
                        value=form_data.get('text_content', ''),
                        height=200,
                        help="Plain text version for email clients that don't support HTML"
                    )
            
            with content_tab4:
                # AI Assistant tab
                self._render_ai_assistant_tab(subject, html_content)
            
            # Preview section
            st.markdown("### 👁️ Preview")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("🔍 Preview Template"):
                    # Generate preview
                    sample_data = {
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'email': 'john.doe@example.com',
                        'company': 'Example Corp'
                    }
                    
                    # Show preview in an expander
                    with st.expander("📧 Email Preview", expanded=True):
                        # Render preview
                        preview_html = self._render_template_preview(html_content, sample_data)
                        st.markdown(f"**Subject:** {self._render_template_preview(subject, sample_data)}")
                        st.markdown("**HTML Content:**")
                        st.components.v1.html(preview_html, height=400, scrolling=True)
            
            with col2:
                # AI generation button
                ai_generate = st.form_submit_button("🤖 Generate AI Content", use_container_width=True)
                st.markdown("---")
                  # Save template
                submitted = st.form_submit_button("💾 Save Template", use_container_width=True)
                
                # Handle AI generation
                if ai_generate:
                    if 'ai_inputs' in st.session_state and st.session_state.ai_inputs.get('description', '').strip():
                        with st.spinner("Generating AI content..."):
                            inputs = st.session_state.ai_inputs
                            content = self.ai_helper._generate_email_content(
                                inputs['email_type'], 
                                inputs['tone'], 
                                inputs['target_audience'], 
                                inputs['company_name'], 
                                inputs['description']
                            )
                            if content:
                                st.session_state.ai_generated_subject = content.get('subject', '')
                                st.session_state.ai_generated_content = content.get('content', '')
                                st.success("AI content generated! Use the buttons below to apply it to your template.")
                                st.rerun()
                    else:
                        st.error("Please fill in the AI assistant details first.")
                
                if submitted:
                    # Validate required fields
                    if not name:
                        st.error("Template name is required")
                    elif not subject:
                        st.error("Email subject is required")
                    elif not html_content:
                        st.error("HTML content is required")
                    else:
                        # Save template
                        template_data = {
                            'name': name,
                            'subject': subject,
                            'html_content': html_content,
                            'text_content': text_content,
                            'category': category.lower(),
                            'is_public': is_public
                        }
                        
                        result = self.template_service.create_template(
                            st.session_state.user_id, template_data
                        )
                        
                        if result['success']:
                            st.success("Template saved successfully!")
                            # Clear form data
                            save_form_data('template_editor', {})
                            st.rerun()
                        else:
                            st.error(f"Error: {result['error']}")
    
    def _render_predefined_templates(self):
        """Render predefined templates selection"""
        
        st.markdown("### 🎨 Choose from Predefined Templates")
        
        predefined_templates = self.template_service.get_predefined_templates()
        
        # Group templates by category
        categories = {}
        for template in predefined_templates:
            category = template['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(template)
        
        for category, templates in categories.items():
            st.markdown(f"#### 📁 {category.title()}")
            
            cols = st.columns(3)
            
            for idx, template in enumerate(templates):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="template-preview">
                        <h5>{template['name']}</h5>
                        <p>{template['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("👁️ Preview", key=f"preview_predefined_{template['id']}"):
                            # Show preview
                            with st.expander(f"Preview: {template['name']}", expanded=True):
                                st.components.v1.html(template['html_content'], height=300, scrolling=True)
                    
                    with col2:
                        if st.button("📝 Use Template", key=f"use_predefined_{template['id']}"):
                            # Create template from predefined
                            template_name = st.text_input(
                                f"Template Name for {template['name']}",
                                value=f"My {template['name']}",
                                key=f"name_for_{template['id']}"
                            )
                            
                            if template_name:
                                result = self.template_service.create_from_predefined(
                                    st.session_state.user_id,
                                    template['id'],
                                    template_name
                                )
                                
                                if result['success']:
                                    st.success(f"Template '{template_name}' created successfully!")
                                else:
                                    st.error(f"Error: {result['error']}")
    
    def _render_html_import(self):
        """Render HTML import functionality"""
        
        st.markdown("### 📥 Import HTML Template")
        
        import_method = st.radio(
            "Import Method",
            ["Upload HTML file", "Paste HTML code"],
            key="html_import_method"
        )
        
        if import_method == "Upload HTML file":
            uploaded_file = st.file_uploader(
                "Choose HTML file",
                type=['html', 'htm'],
                help="Upload an HTML file to use as template"
            )
            
            if uploaded_file is not None:
                try:
                    html_content = uploaded_file.getvalue().decode('utf-8')
                    
                    # Preview uploaded HTML
                    with st.expander("📄 Imported HTML Preview"):
                        st.components.v1.html(html_content, height=300, scrolling=True)
                    
                    # Template details form
                    with st.form("import_html_form"):
                        name = st.text_input("Template Name *", placeholder="e.g., Imported Template")
                        subject = st.text_input("Email Subject *", placeholder="e.g., {{first_name}}, check this out!")
                        category = st.selectbox("Category", ["General", "Welcome", "Newsletter", "Promotional", "Transactional"])
                        
                        if st.form_submit_button("Import Template"):
                            if name and subject:
                                template_data = {
                                    'name': name,
                                    'subject': subject,
                                    'html_content': html_content,
                                    'category': category.lower()
                                }
                                
                                result = self.template_service.create_template(
                                    st.session_state.user_id, template_data
                                )
                                
                                if result['success']:
                                    st.success("Template imported successfully!")
                                else:
                                    st.error(f"Error: {result['error']}")
                            else:
                                st.error("Please fill in template name and subject")
                
                except Exception as e:
                    st.error(f"Error reading HTML file: {str(e)}")
        
        else:  # Paste HTML code
            html_content = st.text_area(
                "Paste HTML Code",
                height=300,
                placeholder="<html>...</html>"
            )
            
            if html_content:
                # Preview pasted HTML
                with st.expander("📄 HTML Preview"):
                    st.components.v1.html(html_content, height=300, scrolling=True)
                
                # Template details form
                with st.form("paste_html_form"):
                    name = st.text_input("Template Name *")
                    subject = st.text_input("Email Subject *")
                    category = st.selectbox("Category", ["General", "Welcome", "Newsletter", "Promotional", "Transactional"])
                    
                    if st.form_submit_button("Create Template"):
                        if name and subject:
                            template_data = {
                                'name': name,
                                'subject': subject,
                                'html_content': html_content,
                                'category': category.lower()
                            }
                            
                            result = self.template_service.create_template(
                                st.session_state.user_id, template_data
                            )
                            
                            if result['success']:
                                st.success("Template created successfully!")
                            else:
                                st.error(f"Error: {result['error']}")
                        else:
                            st.error("Please fill in template name and subject")
    
    def _render_edit_template(self):
        """Render edit existing template"""
        
        template_id = st.session_state.edit_template
        
        # Get template data
        template_result = self.template_service.get_template(st.session_state.user_id, template_id)
        
        if template_result['success']:
            template_data = template_result['template']
            st.subheader(f"✏️ Edit Template: {template_data['name']}")
            
            # Render form with existing data
            self._render_template_form(template_data)
            
            # Cancel button
            if st.button("❌ Cancel Edit"):
                del st.session_state.edit_template
                st.rerun()
        
        else:
            st.error(f"Error loading template: {template_result['error']}")
            if st.button("← Back to Templates"):
                del st.session_state.edit_template
                st.rerun()
    
    def _generate_html_from_visual_editor(self, header_type, header_text, header_image, sections, footer_text):
        """Generate HTML from visual editor components"""
        
        html_parts = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<meta charset="utf-8">',
            '<title>Email Template</title>',
            '<style>',
            'body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }',
            '.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }',
            '.section { padding: 20px; margin: 20px 0; }',
            '.footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px; }',
            '</style>',
            '</head>',
            '<body>'
        ]
        
        # Header
        if header_type != "None":
            html_parts.append('<div class="header">')
            if header_image:
                html_parts.append(f'<img src="{header_image}" alt="Logo" style="max-height: 50px; margin-bottom: 10px;">')
            html_parts.append(f'<h1>{header_text}</h1>')
            html_parts.append('</div>')
        
        # Sections
        for section in sections:
            if section['title'] or section['content']:
                html_parts.append('<div class="section">')
                if section['title']:
                    html_parts.append(f'<h2>{section["title"]}</h2>')
                if section['content']:
                    html_parts.append(f'<p>{section["content"]}</p>')
                html_parts.append('</div>')
        
        # Footer
        if footer_text:
            html_parts.append('<div class="footer">')
            html_parts.append(footer_text.replace('\n', '<br>'))
            html_parts.append('</div>')
        
        html_parts.extend(['</body>', '</html>'])
        
        return '\n'.join(html_parts)
    
    def _get_default_html_template(self):
        """Get default HTML template"""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{subject}}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #667eea;">Hello, {{first_name}}!</h1>
    </div>
    
    <div style="margin: 20px 0;">
        <p>Welcome to our email! This is a sample template that you can customize.</p>
        <p>You can use variables like {{first_name}}, {{last_name}}, {{company}}, and {{email}} to personalize your emails.</p>
    </div>
    
    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3 style="margin-top: 0; color: #667eea;">What's Next?</h3>
        <ul>
            <li>Customize this template to match your brand</li>
            <li>Add your own content and styling</li>
            <li>Test with different variables</li>
        </ul>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="#" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; font-weight: bold;">
            Call to Action
        </a>
    </div>
    
    <div style="border-top: 1px solid #e9ecef; padding-top: 20px; margin-top: 30px; text-align: center; color: #666; font-size: 14px;">
        <p>© 2025 {{company}}. All rights reserved.</p>
        <p><a href="{{unsubscribe_url}}" style="color: #667eea;">Unsubscribe</a></p>
    </div>
</body>
</html>"""
    
    def _render_template_preview(self, content: str, sample_data: Dict) -> str:
        """Render template with sample data"""
        
        if not content:
            return content
        
        rendered = content
        for key, value in sample_data.items():
            placeholder = f'{{{{{key}}}}}'
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered
    
    def _render_ai_assistant_tab(self, current_subject: str, current_content: str):
        """Render AI assistant tab with various AI tools."""
        st.markdown("### 🤖 AI-Powered Template Assistant")        # AI tool selection
        ai_tool = st.selectbox(
            "Choose AI Tool",
            ["Content Generator", "Subject Optimizer", "Content Analyzer", "A/B Test Generator", "Quick Templates"]
        )
        
        if ai_tool == "Content Generator":
            generated_content = self.ai_helper.render_content_generator_inline()
            
            # Display generated content if available
            if 'ai_generated_subject' in st.session_state or 'ai_generated_content' in st.session_state:
                st.success("AI content generated!")
                col1, col2 = st.columns(2)
                with col1:
                    if 'ai_generated_subject' in st.session_state:
                        st.markdown("**Generated Subject:**")
                        st.code(st.session_state.ai_generated_subject)
                with col2:
                    if 'ai_generated_content' in st.session_state:
                        st.markdown("**Generated Content:**")
                        st.code(st.session_state.ai_generated_content[:200] + "..." if len(st.session_state.ai_generated_content) > 200 else st.session_state.ai_generated_content)
            
            if generated_content:
                col1, col2 = st.columns(2)
                with col1:
                    st.info("🎯 **AI Subject Generated**\nSubject will be applied when you save the template")
                
                with col2:
                    st.info("📝 **AI Content Generated**\nContent will be applied when you save the template")
        
        elif ai_tool == "Subject Optimizer":
            if current_subject:
                optimized_subjects = self.ai_helper.render_subject_optimizer(current_subject, current_content)
                if st.session_state.get('optimized_subject'):
                    st.success(f"Optimized subject: {st.session_state.optimized_subject}")
            else:
                st.info("Enter a subject line in the Basic Information section first")
        
        elif ai_tool == "Content Analyzer":
            if current_content and current_content.strip():
                analysis = self.ai_helper.render_content_analyzer(current_content)
                
                # Show improvement suggestions
                if analysis.get('sentiment', {}).get('suggestions'):
                    st.subheader("💡 AI Suggestions")
                    for suggestion in analysis['sentiment']['suggestions']:
                        st.write(f"• {suggestion}")
            else:
                st.info("Enter content in the HTML Editor tab first")
        
        elif ai_tool == "A/B Test Generator":
            if current_subject and current_content:
                base_content = {"subject": current_subject, "content": current_content}
                variations = self.ai_helper.render_ab_test_generator(base_content)
                
                if variations:
                    st.info("A/B test variations generated! Use these for campaign testing.")
            else:
                st.info("Complete the subject and content first")
        
        elif ai_tool == "Quick Templates":
            selected_template = self.ai_helper.render_quick_templates()
            if selected_template:
                col1, col2 = st.columns(2)
                with col1:
                    st.info("🎯 **Template Subject Ready**\nSubject will be applied when you save")
                
                with col2:
                    st.info("📝 **Template Content Ready**\nContent will be applied when you save")
        
        # Additional AI features
        st.markdown("---")
        st.subheader("🎯 Additional AI Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("🔍 **Mobile Analysis**\nUse the main form submit button to analyze mobile optimization")
        
        with col2:
            st.info("📊 **Engagement Prediction**\nUse the main form submit button to get AI engagement predictions")
        
        # Personalization helper
        with st.expander("👤 Personalization Helper"):
            sample_contact = {
                "first_name": "John",
                "last_name": "Doe", 
                "company": "Example Corp",
                "city": "New York"
            }
            self.ai_helper.render_personalization_helper(sample_contact)

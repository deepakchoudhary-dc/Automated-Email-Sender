from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

from src.database.models import EmailTemplate, User, db_session
from src.utils.logger import EmailSenderLogger
from src.utils.security import SecurityManager

logger = EmailSenderLogger('template_service')

class TemplateService:
    """Handles email template operations"""
    
    def __init__(self):
        self.security_manager = SecurityManager()
    
    def create_template(self, user_id: int, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new email template"""
        
        try:
            # Validate required fields
            if not template_data.get('name'):
                return {'success': False, 'error': 'Template name is required'}
            
            if not template_data.get('subject'):
                return {'success': False, 'error': 'Template subject is required'}
            
            # Validate HTML content for security
            html_content = template_data.get('html_content', '')
            if html_content and not self.security_manager.validate_email_content(html_content):
                return {'success': False, 'error': 'HTML content contains potentially dangerous elements'}
            
            with db_session() as session:
                # Check if template name already exists for user
                existing_template = session.query(EmailTemplate).filter(
                    EmailTemplate.user_id == user_id,
                    EmailTemplate.name == template_data['name']
                ).first()
                
                if existing_template:
                    return {'success': False, 'error': 'Template with this name already exists'}
                
                # Extract variables from template content
                variables = self._extract_template_variables(html_content)
                
                # Create new template
                template = EmailTemplate(
                    user_id=user_id,
                    name=template_data['name'].strip(),
                    subject=template_data['subject'].strip(),
                    html_content=html_content,
                    text_content=template_data.get('text_content', '').strip(),
                    template_type=template_data.get('template_type', 'custom'),
                    category=template_data.get('category', 'general'),
                    variables=variables,
                    is_public=template_data.get('is_public', False),
                    created_at=datetime.utcnow()
                )
                
                session.add(template)
                session.commit()
                
                logger.log_template_created(user_id, template.id, template.name)
                
                return {
                    'success': True,
                    'template_id': template.id,
                    'message': 'Template created successfully'
                }
                
        except Exception as e:
            logger.log_error('create_template_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def update_template(self, user_id: int, template_id: int, 
                       template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing template"""
        
        try:
            with db_session() as session:
                template = session.query(EmailTemplate).filter(
                    EmailTemplate.id == template_id,
                    EmailTemplate.user_id == user_id
                ).first()
                
                if not template:
                    return {'success': False, 'error': 'Template not found'}
                
                # Validate HTML content for security
                html_content = template_data.get('html_content')
                if html_content and not self.security_manager.validate_email_content(html_content):
                    return {'success': False, 'error': 'HTML content contains potentially dangerous elements'}
                
                # Update fields
                if 'name' in template_data:
                    # Check if new name conflicts with existing templates
                    if template_data['name'] != template.name:
                        existing_template = session.query(EmailTemplate).filter(
                            EmailTemplate.user_id == user_id,
                            EmailTemplate.name == template_data['name'],
                            EmailTemplate.id != template_id
                        ).first()
                        
                        if existing_template:
                            return {'success': False, 'error': 'Template with this name already exists'}
                    
                    template.name = template_data['name'].strip()
                
                if 'subject' in template_data:
                    template.subject = template_data['subject'].strip()
                
                if 'html_content' in template_data:
                    template.html_content = template_data['html_content']
                    # Update variables when content changes
                    template.variables = self._extract_template_variables(template_data['html_content'])
                
                if 'text_content' in template_data:
                    template.text_content = template_data['text_content'].strip()
                
                if 'category' in template_data:
                    template.category = template_data['category']
                
                if 'is_public' in template_data:
                    template.is_public = template_data['is_public']
                
                template.updated_at = datetime.utcnow()
                session.commit()
                
                logger.log_user_action(user_id, 'template_updated', {'template_id': template_id})
                
                return {'success': True, 'message': 'Template updated successfully'}
                
        except Exception as e:
            logger.log_error('update_template_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def delete_template(self, user_id: int, template_id: int) -> Dict[str, Any]:
        """Delete a template"""
        
        try:
            with db_session() as session:
                template = session.query(EmailTemplate).filter(
                    EmailTemplate.id == template_id,
                    EmailTemplate.user_id == user_id
                ).first()
                
                if not template:
                    return {'success': False, 'error': 'Template not found'}
                
                # Check if template is being used in any campaigns
                from src.database.models import Campaign
                campaigns_using_template = session.query(Campaign).filter(
                    Campaign.template_id == template_id
                ).count()
                
                if campaigns_using_template > 0:
                    return {
                        'success': False, 
                        'error': f'Template is being used in {campaigns_using_template} campaigns and cannot be deleted'
                    }
                
                session.delete(template)
                session.commit()
                
                logger.log_user_action(user_id, 'template_deleted', {'template_id': template_id})
                
                return {'success': True, 'message': 'Template deleted successfully'}
                
        except Exception as e:
            logger.log_error('delete_template_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def get_template(self, user_id: int, template_id: int) -> Dict[str, Any]:
        """Get a specific template"""
        
        try:
            with db_session() as session:
                template = session.query(EmailTemplate).filter(
                    EmailTemplate.id == template_id,
                    EmailTemplate.user_id == user_id
                ).first()
                
                if not template:
                    return {'success': False, 'error': 'Template not found'}
                
                return {
                    'success': True,
                    'template': {
                        'id': template.id,
                        'name': template.name,
                        'subject': template.subject,
                        'html_content': template.html_content,
                        'text_content': template.text_content,
                        'template_type': template.template_type,
                        'category': template.category,
                        'variables': template.variables or [],
                        'is_public': template.is_public,
                        'created_at': template.created_at.strftime('%Y-%m-%d %H:%M'),
                        'updated_at': template.updated_at.strftime('%Y-%m-%d %H:%M') if template.updated_at else None
                    }
                }
                
        except Exception as e:
            logger.log_error('get_template_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def get_templates_list(self, user_id: int, category: str = None, 
                          template_type: str = None, search_term: str = None) -> List[Dict[str, Any]]:
        """Get list of templates with filtering"""
        
        try:
            with db_session() as session:
                query = session.query(EmailTemplate).filter(EmailTemplate.user_id == user_id)
                
                # Apply filters
                if category:
                    query = query.filter(EmailTemplate.category == category)
                
                if template_type:
                    query = query.filter(EmailTemplate.template_type == template_type)
                
                if search_term:
                    search_pattern = f'%{search_term}%'
                    query = query.filter(
                        (EmailTemplate.name.ilike(search_pattern)) |
                        (EmailTemplate.subject.ilike(search_pattern))
                    )
                
                templates = query.order_by(EmailTemplate.created_at.desc()).all()
                
                templates_data = []
                for template in templates:
                    templates_data.append({
                        'id': template.id,
                        'name': template.name,
                        'subject': template.subject,
                        'category': template.category,
                        'template_type': template.template_type,
                        'is_public': template.is_public,
                        'created_at': template.created_at.strftime('%Y-%m-%d'),
                        'variables_count': len(template.variables) if template.variables else 0
                    })
                
                return templates_data
                
        except Exception as e:
            logger.log_error('get_templates_list_failed', str(e), user_id)
            return []
    
    def duplicate_template(self, user_id: int, template_id: int, 
                          new_name: str = None) -> Dict[str, Any]:
        """Duplicate an existing template"""
        
        try:
            with db_session() as session:
                original_template = session.query(EmailTemplate).filter(
                    EmailTemplate.id == template_id,
                    EmailTemplate.user_id == user_id
                ).first()
                
                if not original_template:
                    return {'success': False, 'error': 'Template not found'}
                
                # Generate new name if not provided
                if not new_name:
                    new_name = f"{original_template.name} (Copy)"
                
                # Ensure name is unique
                counter = 1
                base_name = new_name
                while session.query(EmailTemplate).filter(
                    EmailTemplate.user_id == user_id,
                    EmailTemplate.name == new_name
                ).first():
                    new_name = f"{base_name} ({counter})"
                    counter += 1
                
                # Create duplicate template
                duplicate_template = EmailTemplate(
                    user_id=user_id,
                    name=new_name,
                    subject=original_template.subject,
                    html_content=original_template.html_content,
                    text_content=original_template.text_content,
                    template_type=original_template.template_type,
                    category=original_template.category,
                    variables=original_template.variables,
                    is_public=False,  # Duplicates are private by default
                    created_at=datetime.utcnow()
                )
                
                session.add(duplicate_template)
                session.commit()
                
                logger.log_user_action(
                    user_id, 'template_duplicated',
                    {'original_id': template_id, 'new_id': duplicate_template.id}
                )
                
                return {
                    'success': True,
                    'template_id': duplicate_template.id,
                    'message': 'Template duplicated successfully'
                }
                
        except Exception as e:
            logger.log_error('duplicate_template_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def preview_template(self, user_id: int, template_id: int, 
                        sample_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a preview of the template with sample data"""
        
        try:
            template_result = self.get_template(user_id, template_id)
            
            if not template_result['success']:
                return template_result
            
            template = template_result['template']
            
            # Use sample data or default values
            if not sample_data:
                sample_data = {
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john.doe@example.com',
                    'company': 'Example Corp'
                }
            
            # Generate preview
            preview_html = self._render_template(template['html_content'], sample_data)
            preview_subject = self._render_template(template['subject'], sample_data)
            preview_text = self._render_template(template['text_content'] or '', sample_data)
            
            return {
                'success': True,
                'preview': {
                    'subject': preview_subject,
                    'html_content': preview_html,
                    'text_content': preview_text,
                    'sample_data': sample_data
                }
            }
            
        except Exception as e:
            logger.log_error('preview_template_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def get_template_categories(self, user_id: int) -> List[str]:
        """Get list of template categories used by the user"""
        
        try:
            with db_session() as session:
                categories = session.query(EmailTemplate.category).filter(
                    EmailTemplate.user_id == user_id,
                    EmailTemplate.category.isnot(None)
                ).distinct().all()
                
                return [cat[0] for cat in categories if cat[0]]
                
        except Exception as e:
            logger.log_error('get_template_categories_failed', str(e), user_id)
            return []
    
    def get_template_variables(self, user_id: int, template_id: int) -> List[str]:
        """Get list of variables used in a template"""
        
        try:
            template_result = self.get_template(user_id, template_id)
            
            if not template_result['success']:
                return []
            
            return template_result['template']['variables']
            
        except Exception as e:
            logger.log_error('get_template_variables_failed', str(e), user_id)
            return []
    
    def validate_template_syntax(self, html_content: str, text_content: str = None) -> Dict[str, Any]:
        """Validate template syntax and structure"""
        
        try:
            errors = []
            warnings = []
            
            # Check for security issues
            if not self.security_manager.validate_email_content(html_content):
                errors.append('Template contains potentially dangerous content')
            
            # Check for unclosed variables
            unclosed_vars = re.findall(r'\{\{[^}]+$', html_content)
            if unclosed_vars:
                errors.append(f'Unclosed template variables found: {unclosed_vars}')
            
            # Check for common HTML issues
            if '<html>' not in html_content.lower() and len(html_content) > 100:
                warnings.append('Template might benefit from proper HTML structure')
            
            # Check for missing alt text in images
            img_tags = re.findall(r'<img[^>]*>', html_content, re.IGNORECASE)
            for img in img_tags:
                if 'alt=' not in img.lower():
                    warnings.append('Image tags should include alt text for accessibility')
            
            # Extract and validate variables
            variables = self._extract_template_variables(html_content)
            
            return {
                'success': True,
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'variables': variables
            }
            
        except Exception as e:
            logger.log_error('validate_template_syntax_failed', str(e))
            return {'success': False, 'error': str(e)}
    
    def get_predefined_templates(self) -> List[Dict[str, Any]]:
        """Get list of predefined templates"""
        
        # This would typically come from a database or configuration file
        # For now, returning a static list
        return [
            {
                'id': 'welcome_simple',
                'name': 'Simple Welcome',
                'description': 'Clean and simple welcome email template',
                'category': 'welcome',
                'preview_image': '/static/templates/welcome_simple.png',
                'html_content': self._get_welcome_simple_template()
            },
            {
                'id': 'newsletter_modern',
                'name': 'Modern Newsletter', 
                'description': 'Contemporary newsletter design with sections',
                'category': 'newsletter',
                'preview_image': '/static/templates/newsletter_modern.png',
                'html_content': self._get_newsletter_modern_template()
            },
            {
                'id': 'promotion_sale',
                'name': 'Sale Promotion',
                'description': 'Eye-catching sale promotion template',
                'category': 'promotional',
                'preview_image': '/static/templates/promotion_sale.png',
                'html_content': self._get_promotion_sale_template()
            }
        ]
    
    def create_from_predefined(self, user_id: int, predefined_id: str, 
                              template_name: str) -> Dict[str, Any]:
        """Create a new template from a predefined template"""
        
        try:
            predefined_templates = {t['id']: t for t in self.get_predefined_templates()}
            
            if predefined_id not in predefined_templates:
                return {'success': False, 'error': 'Predefined template not found'}
            
            predefined = predefined_templates[predefined_id]
            
            template_data = {
                'name': template_name,
                'subject': f"{{{{first_name}}}}, check this out!",
                'html_content': predefined['html_content'],
                'text_content': '',
                'category': predefined['category'],
                'template_type': 'predefined'
            }
            
            return self.create_template(user_id, template_data)
            
        except Exception as e:
            logger.log_error('create_from_predefined_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def get_user_templates(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all templates for a user"""
        try:
            with db_session() as session:
                templates = session.query(EmailTemplate).filter(
                    EmailTemplate.user_id == user_id
                ).order_by(EmailTemplate.created_at.desc()).all()
                
                return [
                    {
                        'id': template.id,
                        'name': template.name,
                        'subject': template.subject,
                        'category': template.category,
                        'template_type': template.template_type,
                        'created_at': template.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'html_content': template.html_content,
                        'text_content': template.text_content
                    }
                    for template in templates
                ]
        except Exception as e:
            logger.error(f"Error getting user templates: {str(e)}")
            return []
    
    def _extract_template_variables(self, content: str) -> List[str]:
        """Extract template variables from content"""
        
        if not content:
            return []
        
        # Find all variables in {{variable}} format
        variables = re.findall(r'\{\{([^}]+)\}\}', content)
        
        # Clean and deduplicate
        cleaned_variables = []
        for var in variables:
            cleaned_var = var.strip()
            if cleaned_var and cleaned_var not in cleaned_variables:
                cleaned_variables.append(cleaned_var)
        
        return cleaned_variables
    
    def _render_template(self, content: str, data: Dict[str, Any]) -> str:
        """Render template with data"""
        
        if not content:
            return content
        
        rendered = content
        
        # Replace variables
        for key, value in data.items():
            placeholder = f'{{{{{key}}}}}'
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered
    
    def _get_welcome_simple_template(self) -> str:
        """Get simple welcome template HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome!</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #667eea;">Welcome, {{first_name}}!</h1>
                <p>Thank you for joining {{company}}. We're excited to have you on board!</p>
                <p>Here's what you can expect:</p>
                <ul>
                    <li>Regular updates and newsletters</li>
                    <li>Exclusive offers and promotions</li>
                    <li>Tips and insights from our team</li>
                </ul>
                <p>If you have any questions, feel free to reply to this email.</p>
                <p>Best regards,<br>The {{company}} Team</p>
            </div>
        </body>
        </html>
        """
    
    def _get_newsletter_modern_template(self) -> str:
        """Get modern newsletter template HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Newsletter</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">{{company}} Newsletter</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Your weekly dose of insights</p>
                </div>
                <div style="padding: 30px 20px;">
                    <h2 style="color: #333; margin-top: 0;">Hello {{first_name}}!</h2>
                    <p>Here are the latest updates from our team:</p>
                    
                    <div style="border-left: 4px solid #667eea; padding-left: 20px; margin: 20px 0;">
                        <h3 style="color: #667eea; margin: 0 0 10px 0;">Featured Article</h3>
                        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
                    </div>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 6px; margin: 20px 0;">
                        <h3 style="color: #333; margin: 0 0 10px 0;">Quick Tips</h3>
                        <ul style="margin: 0; padding-left: 20px;">
                            <li>Tip 1: Use personalization in your emails</li>
                            <li>Tip 2: Test different subject lines</li>
                            <li>Tip 3: Optimize for mobile devices</li>
                        </ul>
                    </div>
                </div>
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
                    <p style="margin: 0; color: #666; font-size: 14px;">
                        © 2025 {{company}}. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_promotion_sale_template(self) -> str:
        """Get promotion sale template HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Special Sale!</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%); color: white; padding: 40px 20px; text-align: center;">
                    <h1 style="margin: 0; font-size: 36px; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">🎉 SPECIAL SALE!</h1>
                    <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">Limited time offer just for you</p>
                </div>
                <div style="padding: 40px 20px; text-align: center;">
                    <h2 style="color: #333; margin-top: 0;">Hi {{first_name}}!</h2>
                    <p style="font-size: 18px; color: #666;">We have an exclusive offer just for you!</p>
                    
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin: 30px 0;">
                        <h3 style="margin: 0 0 15px 0; font-size: 28px;">50% OFF</h3>
                        <p style="margin: 0; font-size: 16px; opacity: 0.9;">Everything in our store</p>
                    </div>
                    
                    <p style="color: #e74c3c; font-weight: bold; font-size: 16px;">⏰ Offer expires in 24 hours!</p>
                    
                    <div style="margin: 30px 0;">
                        <a href="#" style="background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 18px; display: inline-block; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                            SHOP NOW
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px;">Use code: <strong>SAVE50</strong> at checkout</p>
                </div>
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
                    <p style="margin: 0; color: #666; font-size: 14px;">
                        © 2025 {{company}}. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

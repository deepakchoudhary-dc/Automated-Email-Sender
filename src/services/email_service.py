import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional

try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, Disposition, FileContent, FileName, FileType
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

import base64
import json
from datetime import datetime

from src.database.models import Campaign, Contact, EmailLog, User, db_session
from src.utils.logger import EmailSenderLogger
from src.utils.security import SecurityManager

logger = EmailSenderLogger('email_service')

class EmailService:
    """Handles email sending operations"""
    
    def __init__(self):
        self.security_manager = SecurityManager()
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
          # Initialize email clients
        self._init_email_clients()
    
    def _init_email_clients(self):
        """Initialize email service clients"""
        
        # SendGrid client
        if self.sendgrid_api_key and SENDGRID_AVAILABLE:
            self.sendgrid_client = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
        else:
            self.sendgrid_client = None
        
        # AWS SES client
        if self.aws_access_key and self.aws_secret_key and BOTO3_AVAILABLE:            self.ses_client = boto3.client(
                'ses',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
        else:
            self.ses_client = None
    
    def create_campaign(self, campaign_data: Dict[str, Any]) -> str:
        """Create a new email campaign."""
        try:
            with db_session() as session:
                campaign = Campaign(
                    name=campaign_data['name'],
                    subject=campaign_data['subject'],
                    html_content=campaign_data.get('html_content', campaign_data.get('content', '')),
                    text_content=campaign_data.get('text_content', ''),
                    from_email=campaign_data.get('from_email', os.getenv('DEFAULT_FROM_EMAIL', 'noreply@example.com')),
                    from_name=campaign_data.get('from_name', os.getenv('DEFAULT_FROM_NAME', 'Email Sender')),
                    reply_to=campaign_data.get('reply_to', ''),
                    scheduled_at=campaign_data.get('scheduled_time'),
                    campaign_type=campaign_data.get('type', 'one_time'),
                    user_id=campaign_data['user_id'],
                    status='draft',
                    contact_lists=campaign_data.get('contact_lists', []),
                    track_opens=campaign_data.get('track_opens', True),
                    track_clicks=campaign_data.get('track_clicks', True)
                )
                session.add(campaign)
                session.commit()
                
                logger.info(f"Campaign created: {campaign.id}")
                return str(campaign.id)
                
        except Exception as e:
            logger.error(f"Failed to create campaign: {str(e)}")
            raise
    
    def create_drip_campaign(self, campaign_data: Dict[str, Any]) -> str:
        """Create a drip email campaign."""
        try:
            with db_session() as session:
                campaign = Campaign(
                    name=campaign_data['name'],
                    campaign_type='drip',
                    user_id=campaign_data['user_id'],
                    status=campaign_data.get('status', 'active'),
                    settings=json.dumps({
                        'description': campaign_data.get('description', ''),
                        'trigger_type': campaign_data.get('trigger_type'),
                        'email_sequence': campaign_data.get('email_sequence', []),
                        'target_lists': campaign_data.get('target_lists', [])
                    })
                )
                session.add(campaign)
                session.commit()
                
                logger.info(f"Drip campaign created: {campaign.id}")
                return str(campaign.id)
                
        except Exception as e:
            logger.error(f"Failed to create drip campaign: {str(e)}")
            raise
    
    def create_ab_test_campaign(self, campaign_data: Dict[str, Any]) -> str:
        """Create an A/B test campaign."""
        try:
            with db_session() as session:
                campaign = Campaign(
                    name=campaign_data['name'],
                    campaign_type='ab_test',
                    user_id=campaign_data['user_id'],
                    status=campaign_data.get('status', 'active'),
                    settings=json.dumps({
                        'description': campaign_data.get('description', ''),
                        'test_variable': campaign_data.get('test_variable'),
                        'test_split': campaign_data.get('test_split', 20),
                        'test_duration': campaign_data.get('test_duration', 24),
                        'winner_metric': campaign_data.get('winner_metric', 'open_rate'),
                        'target_lists': campaign_data.get('target_lists', [])
                    })
                )
                session.add(campaign)
                session.commit()
                
                logger.info(f"A/B test campaign created: {campaign.id}")
                return str(campaign.id)
                
        except Exception as e:
            logger.error(f"Failed to create A/B test campaign: {str(e)}")
            raise
    
    def get_user_campaigns(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all campaigns for a user."""
        try:
            with db_session() as session:
                campaigns = session.query(Campaign).filter(Campaign.user_id == user_id).all()
                
                campaign_list = []
                for campaign in campaigns:
                    campaign_dict = {
                        'id': str(campaign.id),
                        'name': campaign.name,
                        'type': campaign.campaign_type,
                        'status': campaign.status,
                        'created_at': campaign.created_at.isoformat() if campaign.created_at else None,
                        'subject': campaign.subject,
                        'recipient_count': 0,  # TODO: Calculate from campaign logs
                        'sent_count': 0,
                        'open_count': 0,
                        'click_count': 0,
                        'open_rate': 0.0,
                        'click_rate': 0.0
                    }
                    
                    # Get campaign stats
                    stats = self._get_campaign_stats(session, campaign.id)
                    campaign_dict.update(stats)
                    
                    campaign_list.append(campaign_dict)
                
                return campaign_list
                
        except Exception as e:
            logger.error(f"Failed to get user campaigns: {str(e)}")
            return []
    
    def pause_campaign(self, campaign_id: str):
        """Pause a campaign."""
        try:
            with db_session() as session:
                campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
                if campaign:
                    campaign.status = 'paused'
                    session.commit()
                    logger.info(f"Campaign paused: {campaign_id}")
                
        except Exception as e:
            logger.error(f"Failed to pause campaign: {str(e)}")
            raise
    
    def resume_campaign(self, campaign_id: str):
        """Resume a paused campaign."""
        try:
            with db_session() as session:
                campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
                if campaign:
                    campaign.status = 'active'
                    session.commit()
                    logger.info(f"Campaign resumed: {campaign_id}")
                
        except Exception as e:
            logger.error(f"Failed to resume campaign: {str(e)}")
            raise
    
    def duplicate_campaign(self, campaign_id: str) -> str:
        """Duplicate an existing campaign."""
        try:
            with db_session() as session:
                original = session.query(Campaign).filter(Campaign.id == campaign_id).first()
                if not original:
                    raise ValueError("Campaign not found")
                
                duplicate = Campaign(
                    name=f"{original.name} (Copy)",
                    subject=original.subject,
                    html_content=original.html_content,
                    text_content=original.text_content,
                    from_email=original.from_email,
                    from_name=original.from_name,
                    reply_to=original.reply_to,
                    campaign_type=original.campaign_type,
                    user_id=original.user_id,
                    status='draft',
                    contact_lists=original.contact_lists,
                    filters=original.filters,
                    track_opens=original.track_opens,
                    track_clicks=original.track_clicks
                )
                session.add(duplicate)
                session.commit()
                
                logger.info(f"Campaign duplicated: {campaign_id} -> {duplicate.id}")
                return str(duplicate.id)
                
        except Exception as e:
            logger.error(f"Failed to duplicate campaign: {str(e)}")
            raise
    
    def delete_campaign(self, campaign_id: str):
        """Delete a campaign."""
        try:
            with db_session() as session:
                campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
                if campaign:
                    session.delete(campaign)
                    session.commit()
                    logger.info(f"Campaign deleted: {campaign_id}")
                
        except Exception as e:
            logger.error(f"Failed to delete campaign: {str(e)}")
            raise
    
    def send_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Send a campaign to its recipients."""
        try:
            with db_session() as session:
                campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
                if not campaign:
                    return {"success": False, "error": "Campaign not found"}
                
                # Get recipients from contact lists
                recipients = []
                if campaign.contact_lists:
                    from src.database.models import ContactListMember
                    for list_id in campaign.contact_lists:
                        list_members = session.query(ContactListMember).filter(
                            ContactListMember.contact_list_id == list_id
                        ).all()
                        for member in list_members:
                            if member.contact:
                                recipients.append({
                                    'id': member.contact.id,
                                    'email': member.contact.email,
                                    'first_name': member.contact.first_name or '',
                                    'last_name': member.contact.last_name or '',
                                    'company': member.contact.company or '',
                                    'custom_fields': member.contact.custom_fields or {}
                                })
                
                if not recipients:
                    return {"success": False, "error": "No recipients found"}
                
                # Update campaign status
                campaign.status = 'sending'
                campaign.recipient_count = len(recipients)
                session.commit()
                
                sent_count = 0
                failed_count = 0
                
                for recipient in recipients:
                    try:
                        # Send individual email
                        result = self.send_single_email(
                            to_email=recipient['email'],
                            subject=self._personalize_content(campaign.subject, recipient),
                            html_content=self._personalize_content(campaign.html_content or '', recipient),
                            text_content=self._personalize_content(campaign.text_content or '', recipient),
                            from_email=campaign.from_email,
                            from_name=campaign.from_name,
                            user_id=campaign.user_id
                        )
                        
                        if result['success']:
                            sent_count += 1
                        else:
                            failed_count += 1
                            
                    except Exception as e:
                        logger.error(f"Failed to send to {recipient['email']}: {str(e)}")
                        failed_count += 1
                
                # Update campaign status
                campaign.status = 'sent'
                campaign.sent_at = datetime.utcnow()
                campaign.delivered_count = sent_count
                session.commit()
                
                return {
                    "success": True,
                    "sent_count": sent_count,
                    "failed_count": failed_count,
                    "total_recipients": len(recipients)
                }
                
        except Exception as e:
            logger.error(f"Failed to send campaign: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_automation(self, automation_data: Dict[str, Any]) -> str:
        """Create a new email automation."""
        try:
            with db_session() as session:
                # Store automation in Campaign table with type 'automation'
                automation = Campaign(
                    name=automation_data['name'],
                    campaign_type='automation',
                    user_id=automation_data['user_id'],
                    status='active' if automation_data.get('active', False) else 'draft',
                    subject=automation_data.get('subject', 'Automation'),
                    html_content=automation_data.get('html_content', ''),
                    text_content=automation_data.get('text_content', ''),
                    from_email=automation_data.get('from_email', os.getenv('DEFAULT_FROM_EMAIL', 'noreply@example.com')),
                    from_name=automation_data.get('from_name', os.getenv('DEFAULT_FROM_NAME', 'Automation'))
                )
                session.add(automation)
                session.commit()
                
                logger.info(f"Automation created: {automation.id}")
                return str(automation.id)
                
        except Exception as e:
            logger.error(f"Failed to create automation: {str(e)}")
            raise
    
    def get_user_automations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all automations for a user."""
        try:
            with db_session() as session:
                automations = session.query(Campaign).filter(
                    Campaign.user_id == user_id,
                    Campaign.campaign_type == 'automation'
                ).all()
                
                automation_list = []
                for automation in automations:
                    settings = json.loads(automation.settings) if automation.settings else {}
                    
                    automation_dict = {
                        'id': str(automation.id),
                        'name': automation.name,
                        'type': settings.get('type', 'custom'),
                        'status': automation.status,
                        'created_at': automation.created_at.isoformat() if automation.created_at else None,
                        'active_contacts': 0,  # TODO: Calculate active contacts in automation
                        'emails_sent': 0,
                        'avg_open_rate': 0.0,
                        'avg_click_rate': 0.0
                    }
                    
                    automation_list.append(automation_dict)
                
                return automation_list
                
        except Exception as e:
            logger.error(f"Failed to get user automations: {str(e)}")
            return []
    
    def _get_campaign_stats(self, session, campaign_id: str) -> Dict[str, Any]:
        """Get campaign statistics."""
        try:
            # Query email logs for campaign stats
            logs = session.query(EmailLog).filter(EmailLog.campaign_id == campaign_id).all()
            
            total_sent = len(logs)
            opened = len([log for log in logs if log.opened_at])
            clicked = len([log for log in logs if log.clicked_at])
            
            open_rate = (opened / total_sent * 100) if total_sent > 0 else 0
            click_rate = (clicked / total_sent * 100) if total_sent > 0 else 0
            
            return {
                'sent_count': total_sent,
                'open_count': opened,
                'click_count': clicked,
                'open_rate': round(open_rate, 1),
                'click_rate': round(click_rate, 1)
            }
            
        except Exception as e:
            logger.error(f"Failed to get campaign stats: {str(e)}")
            return {
                'sent_count': 0,
                'open_count': 0,
                'click_count': 0,
                'open_rate': 0.0,
                'click_rate': 0.0
            }
    
    def send_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Send an email campaign"""
        
        try:
            with db_session() as session:
                campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
                
                if not campaign:
                    return {'success': False, 'error': 'Campaign not found'}
                
                if campaign.status != 'draft':
                    return {'success': False, 'error': 'Campaign is not in draft status'}
                
                # Get recipient contacts
                recipients = self._get_campaign_recipients(campaign_id, session)
                
                if not recipients:
                    return {'success': False, 'error': 'No recipients found'}
                
                # Update campaign status
                campaign.status = 'sending'
                campaign.recipient_count = len(recipients)
                session.commit()
                
                # Send emails
                sent_count = 0
                failed_count = 0
                
                for recipient in recipients:
                    try:
                        result = self._send_single_email(
                            campaign=campaign,
                            recipient=recipient,
                            session=session
                        )
                        
                        if result['success']:
                            sent_count += 1
                        else:
                            failed_count += 1
                            
                    except Exception as e:
                        logger.log_error('email_send_failed', str(e), campaign.user_id)
                        failed_count += 1
                
                # Update campaign status
                campaign.status = 'sent'
                campaign.sent_at = datetime.utcnow()
                campaign.delivered_count = sent_count
                session.commit()
                
                logger.log_campaign_created(campaign.user_id, campaign_id, campaign.name)
                
                return {
                    'success': True,
                    'sent_count': sent_count,
                    'failed_count': failed_count,
                    'total_recipients': len(recipients)
                }
                
        except Exception as e:
            logger.log_error('campaign_send_failed', str(e))
            return {'success': False, 'error': str(e)}
    
    def send_single_email(self, to_email: str, subject: str, html_content: str = None,
                         text_content: str = None, from_email: str = None,
                         from_name: str = None, attachments: List[Dict] = None,
                         user_id: int = None) -> Dict[str, Any]:
        """Send a single email"""
        
        try:
            # Default values
            if not from_email:
                from_email = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@example.com')
            
            if not from_name:
                from_name = os.getenv('DEFAULT_FROM_NAME', 'Email Sender')
            
            # Choose email provider
            provider = self._choose_email_provider()
            
            if provider == 'sendgrid':
                result = self._send_via_sendgrid(
                    to_email, subject, html_content, text_content,
                    from_email, from_name, attachments
                )
            elif provider == 'aws_ses':
                result = self._send_via_aws_ses(
                    to_email, subject, html_content, text_content,
                    from_email, from_name, attachments
                )
            else:
                result = self._send_via_smtp(
                    to_email, subject, html_content, text_content,
                    from_email, from_name, attachments
                )
            
            # Log the email
            if user_id:
                self._log_email(
                    user_id=user_id,
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    status='sent' if result['success'] else 'failed',
                    provider=provider,
                    provider_message_id=result.get('message_id'),
                    error_message=result.get('error')
                )
            
            return result
            
        except Exception as e:
            logger.log_error('single_email_send_failed', str(e), user_id)
            return {'success': False, 'error': str(e)}
    
    def _send_single_email(self, campaign: Campaign, recipient: Dict,
                          session) -> Dict[str, Any]:
        """Send a single email from campaign"""
        
        try:
            # Personalize content
            personalized_content = self._personalize_content(
                campaign.html_content,
                recipient
            )
            
            personalized_subject = self._personalize_content(
                campaign.subject,
                recipient
            )
            
            # Send email
            result = self.send_single_email(
                to_email=recipient['email'],
                subject=personalized_subject,
                html_content=personalized_content,
                text_content=campaign.text_content,
                from_email=campaign.from_email,
                from_name=campaign.from_name,
                user_id=campaign.user_id
            )
            
            # Create email log
            email_log = EmailLog(
                campaign_id=campaign.id,
                contact_id=recipient.get('id'),
                user_id=campaign.user_id,
                to_email=recipient['email'],
                subject=personalized_subject,
                html_content=personalized_content,
                text_content=campaign.text_content,
                status='sent' if result['success'] else 'failed',
                provider=result.get('provider'),
                provider_message_id=result.get('message_id'),
                error_message=result.get('error'),
                sent_at=datetime.utcnow() if result['success'] else None
            )
            
            session.add(email_log)
            session.commit()
            
            return result
            
        except Exception as e:
            logger.log_error('campaign_email_send_failed', str(e), campaign.user_id)
            return {'success': False, 'error': str(e)}
    
    def _send_via_sendgrid(self, to_email: str, subject: str, html_content: str = None,
                          text_content: str = None, from_email: str = None,
                          from_name: str = None, attachments: List[Dict] = None) -> Dict[str, Any]:
        """Send email via SendGrid"""
        
        if not self.sendgrid_client:
            return {'success': False, 'error': 'SendGrid not configured'}
        
        try:
            # Create email
            from_email_obj = Email(from_email, from_name)
            to_email_obj = To(to_email)
            
            # Create mail object
            if html_content:
                content = Content("text/html", html_content)
            else:
                content = Content("text/plain", text_content or "")
            
            mail = Mail(from_email_obj, to_email_obj, subject, content)
            
            # Add text content if HTML is provided
            if html_content and text_content:
                mail.add_content(Content("text/plain", text_content))
            
            # Add attachments
            if attachments:
                for attachment_data in attachments:
                    attachment = Attachment()
                    attachment.file_content = FileContent(attachment_data['content'])
                    attachment.file_type = FileType(attachment_data['type'])
                    attachment.file_name = FileName(attachment_data['filename'])
                    attachment.disposition = Disposition('attachment')
                    mail.add_attachment(attachment)
            
            # Send email
            response = self.sendgrid_client.send(mail)
            
            logger.log_email_provider_interaction(
                'sendgrid', 'send_email', True,
                {'status_code': response.status_code}
            )
            
            return {
                'success': True,
                'provider': 'sendgrid',
                'message_id': response.headers.get('X-Message-Id'),
                'status_code': response.status_code
            }
            
        except Exception as e:
            logger.log_email_provider_interaction(
                'sendgrid', 'send_email', False, {'error': str(e)}
            )
            return {'success': False, 'error': str(e), 'provider': 'sendgrid'}
    
    def _send_via_aws_ses(self, to_email: str, subject: str, html_content: str = None,
                         text_content: str = None, from_email: str = None,
                         from_name: str = None, attachments: List[Dict] = None) -> Dict[str, Any]:
        """Send email via AWS SES"""
        
        if not self.ses_client:
            return {'success': False, 'error': 'AWS SES not configured'}
        
        try:
            # Prepare destination
            destination = {'ToAddresses': [to_email]}
            
            # Prepare message
            message = {
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {}
            }
            
            if html_content:
                message['Body']['Html'] = {'Data': html_content, 'Charset': 'UTF-8'}
            
            if text_content:
                message['Body']['Text'] = {'Data': text_content, 'Charset': 'UTF-8'}
            
            # Send email
            response = self.ses_client.send_email(
                Source=f"{from_name} <{from_email}>" if from_name else from_email,
                Destination=destination,
                Message=message
            )
            
            logger.log_email_provider_interaction(
                'aws_ses', 'send_email', True,
                {'message_id': response['MessageId']}
            )
            
            return {
                'success': True,
                'provider': 'aws_ses',
                'message_id': response['MessageId']
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.log_email_provider_interaction(
                'aws_ses', 'send_email', False,
                {'error_code': error_code, 'error_message': error_message}
            )
            
            return {
                'success': False,
                'error': f"{error_code}: {error_message}",
                'provider': 'aws_ses'
            }
        except Exception as e:
            logger.log_email_provider_interaction(
                'aws_ses', 'send_email', False, {'error': str(e)}
            )
            return {'success': False, 'error': str(e), 'provider': 'aws_ses'}
    
    def _send_via_smtp(self, to_email: str, subject: str, html_content: str = None,
                      text_content: str = None, from_email: str = None,
                      from_name: str = None, attachments: List[Dict] = None) -> Dict[str, Any]:
        """Send email via SMTP (fallback)"""
        
        try:
            # SMTP configuration
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_username = os.getenv('SMTP_USERNAME', from_email)
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            if not smtp_password:
                return {'success': False, 'error': 'SMTP password not configured'}
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{from_name} <{from_email}>" if from_name else from_email
            message['To'] = to_email
            
            # Add content
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                message.attach(text_part)
            
            if html_content:
                html_part = MIMEText(html_content, 'html')
                message.attach(html_part)
            
            # Add attachments
            if attachments:
                for attachment_data in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment_data['content'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment_data["filename"]}'
                    )
                    message.attach(part)
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(smtp_username, smtp_password)
                server.sendmail(from_email, to_email, message.as_string())
            
            logger.log_email_provider_interaction(
                'smtp', 'send_email', True, {'server': smtp_server}
            )
            
            return {
                'success': True,
                'provider': 'smtp',
                'message_id': None
            }
            
        except Exception as e:
            logger.log_email_provider_interaction(
                'smtp', 'send_email', False, {'error': str(e)}
            )
            return {'success': False, 'error': str(e), 'provider': 'smtp'}
    
    def _choose_email_provider(self) -> str:
        """Choose the best available email provider"""
        
        if self.sendgrid_client:
            return 'sendgrid'
        elif self.ses_client:
            return 'aws_ses'
        else:
            return 'smtp'
    
    def _get_campaign_recipients(self, campaign_id: int, session) -> List[Dict]:
        """Get recipients for a campaign"""
        
        campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
        
        if not campaign:
            return []
        
        recipients = []
        
        # If campaign has specific contact lists, get contacts from those lists
        if campaign.contact_lists:
            from src.database.models import ContactListMember
            for list_id in campaign.contact_lists:
                list_members = session.query(ContactListMember).filter(
                    ContactListMember.contact_list_id == list_id
                ).all()
                
                for member in list_members:
                    if member.contact and member.contact.status == 'active':
                        recipients.append({
                            'id': member.contact.id,
                            'email': member.contact.email,
                            'first_name': member.contact.first_name or '',
                            'last_name': member.contact.last_name or '',
                            'company': member.contact.company or '',
                            'custom_fields': member.contact.custom_fields or {}
                        })
        else:
            # If no specific lists, get all active contacts for the user
            contacts = session.query(Contact).filter(
                Contact.user_id == campaign.user_id,
                Contact.status == 'active'
            ).all()
            
            for contact in contacts:
                recipients.append({
                    'id': contact.id,
                    'email': contact.email,
                    'first_name': contact.first_name or '',
                    'last_name': contact.last_name or '',
                    'company': contact.company or '',
                    'custom_fields': contact.custom_fields or {}
                })
        
        # Remove duplicates based on email
        unique_recipients = {}
        for recipient in recipients:
            if recipient['email'] not in unique_recipients:
                unique_recipients[recipient['email']] = recipient
        
        return list(unique_recipients.values())
    
    def _personalize_content(self, content: str, recipient: Dict) -> str:
        """Personalize email content with recipient data"""
        
        if not content:
            return content
        
        # Basic personalization
        personalized = content
        
        # Replace common variables
        replacements = {
            '{{first_name}}': recipient.get('first_name', ''),
            '{{last_name}}': recipient.get('last_name', ''),
            '{{full_name}}': f"{recipient.get('first_name', '')} {recipient.get('last_name', '')}".strip(),
            '{{email}}': recipient.get('email', ''),
            '{{company}}': recipient.get('company', ''),
        }
        
        # Add custom fields
        custom_fields = recipient.get('custom_fields', {})
        for field_name, field_value in custom_fields.items():
            replacements[f'{{{{custom.{field_name}}}}}'] = str(field_value)
        
        # Apply replacements
        for placeholder, value in replacements.items():
            personalized = personalized.replace(placeholder, value)
        
        return personalized
    
    def _log_email(self, user_id: int, to_email: str, subject: str,
                   html_content: str = None, text_content: str = None,
                   status: str = 'sent', provider: str = None,
                   provider_message_id: str = None, error_message: str = None):
        """Log email sending event"""
        
        try:
            with db_session() as session:
                email_log = EmailLog(
                    user_id=user_id,
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    status=status,
                    provider=provider,
                    provider_message_id=provider_message_id,
                    error_message=error_message,
                    sent_at=datetime.utcnow() if status == 'sent' else None,
                    created_at=datetime.utcnow()
                )
                
                session.add(email_log)
                session.commit()
                
                logger.log_email_sent(None, to_email, status)
                
        except Exception as e:
            logger.log_error('email_logging_failed', str(e), user_id)
    
    def get_email_status(self, message_id: str, provider: str) -> Dict[str, Any]:
        """Get email delivery status"""
        
        # This would integrate with provider webhooks/APIs
        # For now, returning placeholder
        return {
            'status': 'delivered',
            'delivered_at': datetime.utcnow(),
            'opened': False,
            'clicked': False
        }
    
    def handle_webhook(self, provider: str, webhook_data: Dict) -> bool:
        """Handle email provider webhooks"""
        
        try:
            if provider == 'sendgrid':
                return self._handle_sendgrid_webhook(webhook_data)
            elif provider == 'aws_ses':
                return self._handle_aws_ses_webhook(webhook_data)
            else:
                return False
                
        except Exception as e:
            logger.log_error('webhook_handling_failed', str(e))
            return False
    
    def _handle_sendgrid_webhook(self, webhook_data: Dict) -> bool:
        """Handle SendGrid webhook events"""
        
        # Process SendGrid webhook events
        # Update email logs with delivery status, opens, clicks, etc.
        return True
    
    def _handle_aws_ses_webhook(self, webhook_data: Dict) -> bool:
        """Handle AWS SES webhook events"""
        
        # Process AWS SES webhook events
        # Update email logs with delivery status, bounces, complaints, etc.
        return True

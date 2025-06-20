"""
Webhook service for handling email provider callbacks (opens, clicks, bounces, etc.)
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
import hmac
import hashlib
from src.database.models import EmailLog, Campaign, Contact, db_session
from src.utils.logger import get_logger

# Optional Flask import for webhook functionality
try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
    request = None
    jsonify = None

logger = get_logger(__name__)

class WebhookService:
    """Handles webhooks from email service providers"""
    
    def __init__(self):
        if not FLASK_AVAILABLE:
            logger.warning("Flask not available. Webhook functionality disabled. Install with: pip install flask>=3.0.2")
            self.app = None
            return
            
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup webhook routes for different providers"""
        
        @self.app.route('/webhook/sendgrid', methods=['POST'])
        def handle_sendgrid_webhook():
            return self.handle_sendgrid_events()
        
        @self.app.route('/webhook/ses', methods=['POST'])
        def handle_ses_webhook():
            return self.handle_ses_events()
        
        @self.app.route('/webhook/mailgun', methods=['POST'])
        def handle_mailgun_webhook():
            return self.handle_mailgun_events()
        
        @self.app.route('/webhook/health', methods=['GET'])
        def health_check():
            return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})
    
    def handle_sendgrid_events(self) -> Dict[str, Any]:
        """Handle SendGrid webhook events"""
        try:
            events = request.get_json()
            if not events:
                return jsonify({"error": "No events received"}), 400
            
            processed_count = 0
            for event in events:
                if self._process_sendgrid_event(event):
                    processed_count += 1
            
            logger.info(f"Processed {processed_count} SendGrid events")
            return jsonify({"processed": processed_count})
            
        except Exception as e:
            logger.error(f"SendGrid webhook error: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def handle_ses_events(self) -> Dict[str, Any]:
        """Handle AWS SES webhook events"""
        try:
            # Handle SNS notification format
            data = request.get_json()
            
            # Verify SNS signature if needed
            if request.headers.get('x-amz-sns-message-type') == 'Notification':
                message = json.loads(data.get('Message', '{}'))
                if self._process_ses_event(message):
                    return jsonify({"status": "processed"})
            
            return jsonify({"error": "Invalid event format"}), 400
            
        except Exception as e:
            logger.error(f"SES webhook error: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def handle_mailgun_events(self) -> Dict[str, Any]:
        """Handle Mailgun webhook events"""
        try:
            # Verify Mailgun signature
            if not self._verify_mailgun_signature(request):
                return jsonify({"error": "Invalid signature"}), 401
            
            event_data = request.form.to_dict()
            if self._process_mailgun_event(event_data):
                return jsonify({"status": "processed"})
            
            return jsonify({"error": "Failed to process event"}), 400
            
        except Exception as e:
            logger.error(f"Mailgun webhook error: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def _process_sendgrid_event(self, event: Dict[str, Any]) -> bool:
        """Process a single SendGrid event"""
        try:
            event_type = event.get('event')
            email = event.get('email')
            message_id = event.get('sg_message_id')
            timestamp = event.get('timestamp')
            
            if not all([event_type, email, message_id]):
                logger.warning(f"Incomplete SendGrid event: {event}")
                return False
            
            # Find the corresponding email log
            with db_session() as session:
                email_log = session.query(EmailLog).filter(
                    EmailLog.message_id == message_id
                ).first()
                
                if not email_log:
                    logger.warning(f"Email log not found for message_id: {message_id}")
                    return False
                
                # Update email log based on event type
                event_time = datetime.fromtimestamp(timestamp) if timestamp else datetime.now()
                
                if event_type == 'delivered':
                    email_log.status = 'delivered'
                    email_log.delivered_at = event_time
                elif event_type == 'open':
                    email_log.opened_at = event_time
                    email_log.open_count = (email_log.open_count or 0) + 1
                elif event_type == 'click':
                    email_log.clicked_at = event_time
                    email_log.click_count = (email_log.click_count or 0) + 1
                    # Store clicked URL if available
                    if 'url' in event:
                        email_log.clicked_urls = json.dumps(
                            json.loads(email_log.clicked_urls or '[]') + [event['url']]
                        )
                elif event_type == 'bounce':
                    email_log.status = 'bounced'
                    email_log.bounced_at = event_time
                    email_log.bounce_reason = event.get('reason', '')
                elif event_type == 'dropped':
                    email_log.status = 'dropped'
                    email_log.error_message = event.get('reason', '')
                elif event_type == 'spam':
                    email_log.status = 'spam'
                elif event_type == 'unsubscribe':
                    email_log.unsubscribed_at = event_time
                    # Update contact status
                    contact = session.query(Contact).filter(
                        Contact.email == email
                    ).first()
                    if contact:
                        contact.status = 'unsubscribed'
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error processing SendGrid event: {str(e)}")
            return False
    
    def _process_ses_event(self, event: Dict[str, Any]) -> bool:
        """Process AWS SES event"""
        try:
            event_type = event.get('eventType')
            mail = event.get('mail', {})
            message_id = mail.get('messageId')
            
            if not all([event_type, message_id]):
                return False
            
            with db_session() as session:
                email_log = session.query(EmailLog).filter(
                    EmailLog.message_id == message_id
                ).first()
                
                if not email_log:
                    return False
                
                event_time = datetime.now()
                
                if event_type == 'delivery':
                    email_log.status = 'delivered'
                    email_log.delivered_at = event_time
                elif event_type == 'bounce':
                    email_log.status = 'bounced'
                    email_log.bounced_at = event_time
                    bounce_info = event.get('bounce', {})
                    email_log.bounce_reason = bounce_info.get('bouncedRecipients', [{}])[0].get('diagnosticCode', '')
                elif event_type == 'complaint':
                    email_log.status = 'spam'
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error processing SES event: {str(e)}")
            return False
    
    def _process_mailgun_event(self, event: Dict[str, Any]) -> bool:
        """Process Mailgun event"""
        try:
            event_type = event.get('event')
            message_id = event.get('Message-Id')
            
            if not all([event_type, message_id]):
                return False
            
            with db_session() as session:
                email_log = session.query(EmailLog).filter(
                    EmailLog.message_id == message_id
                ).first()
                
                if not email_log:
                    return False
                
                event_time = datetime.now()
                
                if event_type == 'delivered':
                    email_log.status = 'delivered'
                    email_log.delivered_at = event_time
                elif event_type == 'opened':
                    email_log.opened_at = event_time
                    email_log.open_count = (email_log.open_count or 0) + 1
                elif event_type == 'clicked':
                    email_log.clicked_at = event_time
                    email_log.click_count = (email_log.click_count or 0) + 1
                elif event_type == 'bounced':
                    email_log.status = 'bounced'
                    email_log.bounced_at = event_time
                    email_log.bounce_reason = event.get('reason', '')
                elif event_type == 'unsubscribed':
                    email_log.unsubscribed_at = event_time
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error processing Mailgun event: {str(e)}")
            return False
    
    def _verify_mailgun_signature(self, request) -> bool:
        """Verify Mailgun webhook signature"""
        try:
            # This would use your Mailgun webhook signing key
            # For now, return True (implement proper verification in production)
            return True
        except Exception as e:
            logger.error(f"Mailgun signature verification failed: {str(e)}")
            return False
    
    def start_webhook_server(self, host: str = '0.0.0.0', port: int = 5001, debug: bool = False):
        """Start the webhook server"""
        logger.info(f"Starting webhook server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

# Global webhook service instance
webhook_service = WebhookService()

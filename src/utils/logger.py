import logging
import os
from datetime import datetime
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from dotenv import load_dotenv

load_dotenv()

def setup_logging():
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Setup file handler
    log_filename = os.path.join(logs_dir, f"email_sender_{datetime.now().strftime('%Y_%m_%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()  # Console output
        ]
    )
    
    # Setup Sentry for error monitoring (if configured)
    sentry_dsn = os.getenv('SENTRY_DSN')
    if sentry_dsn:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[sentry_logging],
            traces_sample_rate=0.1,
            environment=os.getenv('ENVIRONMENT', 'development')
        )
    
    # Get logger
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)

class EmailSenderLogger:
    """Custom logger for Email Sender application"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_user_action(self, user_id: int, action: str, details: dict = None):
        """Log user actions"""
        log_message = f"User {user_id} performed action: {action}"
        if details:
            log_message += f" | Details: {details}"
        
        self.logger.info(log_message)
    
    def log_email_sent(self, campaign_id: int, recipient_email: str, status: str):
        """Log email sending events"""
        self.logger.info(
            f"Email sent - Campaign: {campaign_id}, "
            f"Recipient: {recipient_email}, Status: {status}"
        )
    
    def log_campaign_created(self, user_id: int, campaign_id: int, campaign_name: str):
        """Log campaign creation"""
        self.logger.info(
            f"Campaign created - User: {user_id}, "
            f"Campaign ID: {campaign_id}, Name: {campaign_name}"
        )
    
    def log_template_created(self, user_id: int, template_id: int, template_name: str):
        """Log template creation"""
        self.logger.info(
            f"Template created - User: {user_id}, "
            f"Template ID: {template_id}, Name: {template_name}"
        )
    
    def log_contact_imported(self, user_id: int, count: int, source: str):
        """Log contact import"""
        self.logger.info(
            f"Contacts imported - User: {user_id}, "
            f"Count: {count}, Source: {source}"
        )
    
    def log_authentication(self, email: str, success: bool, ip_address: str = None):
        """Log authentication attempts"""
        status = "successful" if success else "failed"
        log_message = f"Authentication {status} - Email: {email}"
        
        if ip_address:
            log_message += f", IP: {ip_address}"
        
        if success:
            self.logger.info(log_message)
        else:
            self.logger.warning(log_message)
    
    def log_error(self, error_type: str, error_message: str, user_id: int = None, 
                  additional_context: dict = None):
        """Log application errors"""
        log_message = f"Error - Type: {error_type}, Message: {error_message}"
        
        if user_id:
            log_message += f", User: {user_id}"
        
        if additional_context:
            log_message += f", Context: {additional_context}"
        
        self.logger.error(log_message)
    
    def log_api_call(self, endpoint: str, method: str, status_code: int, 
                     response_time: float, user_id: int = None):
        """Log API calls"""
        log_message = (
            f"API Call - Endpoint: {endpoint}, Method: {method}, "
            f"Status: {status_code}, Response Time: {response_time:.3f}s"
        )
        
        if user_id:
            log_message += f", User: {user_id}"
        
        if status_code >= 400:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def log_database_operation(self, operation: str, table: str, affected_rows: int = None,
                              execution_time: float = None):
        """Log database operations"""
        log_message = f"DB Operation - {operation} on {table}"
        
        if affected_rows is not None:
            log_message += f", Affected rows: {affected_rows}"
        
        if execution_time is not None:
            log_message += f", Execution time: {execution_time:.3f}s"
        
        self.logger.info(log_message)
    
    def log_email_provider_interaction(self, provider: str, action: str, 
                                     success: bool, response_data: dict = None):
        """Log email provider interactions"""
        status = "successful" if success else "failed"
        log_message = f"Email Provider - {provider}: {action} {status}"
        
        if response_data:
            log_message += f", Response: {response_data}"
        
        if success:
            self.logger.info(log_message)
        else:
            self.logger.error(log_message)
    
    def log_security_event(self, event_type: str, details: dict, user_id: int = None,
                          ip_address: str = None):
        """Log security-related events"""
        log_message = f"Security Event - {event_type}: {details}"
        
        if user_id:
            log_message += f", User: {user_id}"
        
        if ip_address:
            log_message += f", IP: {ip_address}"
        
        self.logger.warning(log_message)
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "ms"):
        """Log performance metrics"""
        self.logger.info(f"Performance - {metric_name}: {value}{unit}")
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

# Create application-wide logger instances
app_logger = EmailSenderLogger('email_sender')
auth_logger = EmailSenderLogger('email_sender.auth')
email_logger = EmailSenderLogger('email_sender.email')
db_logger = EmailSenderLogger('email_sender.database')
api_logger = EmailSenderLogger('email_sender.api')

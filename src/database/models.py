from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.dialects.postgresql import UUID
from contextlib import contextmanager
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///email_sender.db')

if DATABASE_URL.startswith('sqlite'):
    engine = create_engine(DATABASE_URL, echo=False)
else:
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextmanager
def db_session() -> Session:
    """Database session context manager"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    company = Column(String(100))
    role = Column(String(20), default='user')
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    timezone = Column(String(50), default='UTC')
    preferences = Column(JSON, default=dict)
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="user")
    templates = relationship("EmailTemplate", back_populates="user")
    contacts = relationship("Contact", back_populates="user")
    contact_lists = relationship("ContactList", back_populates="user")

class Contact(Base):
    """Contact model"""
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    company = Column(String(100))
    phone = Column(String(20))
    tags = Column(JSON, default=list)
    custom_fields = Column(JSON, default=dict)
    status = Column(String(20), default='active')  # active, unsubscribed, bounced
    source = Column(String(50))  # manual, import, api
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contacted = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="contacts")
    email_logs = relationship("EmailLog", back_populates="contact")

class ContactList(Base):
    """Contact list model"""
    __tablename__ = 'contact_lists'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="contact_lists")
    contacts = relationship("ContactListMember", back_populates="contact_list")

class ContactListMember(Base):
    """Many-to-many relationship between contacts and lists"""
    __tablename__ = 'contact_list_members'
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    contact_list_id = Column(Integer, ForeignKey('contact_lists.id'), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contact = relationship("Contact")
    contact_list = relationship("ContactList", back_populates="contacts")

class EmailTemplate(Base):
    """Email template model"""
    __tablename__ = 'email_templates'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    subject = Column(String(255), nullable=False)
    html_content = Column(Text)
    text_content = Column(Text)
    template_type = Column(String(20), default='custom')  # custom, predefined
    category = Column(String(50))
    variables = Column(JSON, default=list)  # Available template variables
    preview_image = Column(String(255))
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="templates")
    campaigns = relationship("Campaign", back_populates="template")

class Campaign(Base):
    """Email campaign model"""
    __tablename__ = 'campaigns'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    template_id = Column(Integer, ForeignKey('email_templates.id'))
    name = Column(String(100), nullable=False)
    subject = Column(String(255), nullable=False)
    html_content = Column(Text)
    text_content = Column(Text)
    from_email = Column(String(255), nullable=False)
    from_name = Column(String(100))
    reply_to = Column(String(255))
    
    # Campaign settings
    campaign_type = Column(String(20), default='one_time')  # one_time, drip, triggered
    status = Column(String(20), default='draft')  # draft, scheduled, sending, sent, paused
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    
    # Targeting
    recipient_count = Column(Integer, default=0)
    contact_lists = Column(JSON, default=list)  # List of contact list IDs
    filters = Column(JSON, default=dict)  # Segmentation filters
    
    # A/B Testing
    is_ab_test = Column(Boolean, default=False)
    ab_test_config = Column(JSON, default=dict)
    
    # Tracking
    track_opens = Column(Boolean, default=True)
    track_clicks = Column(Boolean, default=True)
    
    # Statistics
    delivered_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    bounced_count = Column(Integer, default=0)
    unsubscribed_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="campaigns")
    template = relationship("EmailTemplate", back_populates="campaigns")
    email_logs = relationship("EmailLog", back_populates="campaign")

class EmailLog(Base):
    """Email sending log model"""
    __tablename__ = 'email_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Email details
    to_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    html_content = Column(Text)
    text_content = Column(Text)
    
    # Sending details
    status = Column(String(20), default='pending')  # pending, sent, failed, bounced
    provider = Column(String(50))  # sendgrid, aws_ses, gmail
    provider_message_id = Column(String(255))
    error_message = Column(Text)
    
    # Tracking
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    bounced_at = Column(DateTime)
    unsubscribed_at = Column(DateTime)
    
    # Metadata
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="email_logs")
    contact = relationship("Contact", back_populates="email_logs")

class DripCampaign(Base):
    """Drip campaign model"""
    __tablename__ = 'drip_campaigns'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), default='draft')  # draft, active, paused, completed
    
    # Trigger settings
    trigger_type = Column(String(20), default='manual')  # manual, signup, purchase, etc.
    trigger_conditions = Column(JSON, default=dict)
    
    # Settings
    contact_lists = Column(JSON, default=list)
    filters = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    emails = relationship("DripEmail", back_populates="drip_campaign")

class DripEmail(Base):
    """Individual email in a drip campaign"""
    __tablename__ = 'drip_emails'
    
    id = Column(Integer, primary_key=True, index=True)
    drip_campaign_id = Column(Integer, ForeignKey('drip_campaigns.id'), nullable=False)
    template_id = Column(Integer, ForeignKey('email_templates.id'))
    
    name = Column(String(100), nullable=False)
    subject = Column(String(255), nullable=False)
    html_content = Column(Text)
    text_content = Column(Text)
    
    # Timing
    send_delay_days = Column(Integer, default=0)
    send_delay_hours = Column(Integer, default=0)
    send_time = Column(String(5))  # HH:MM format
    
    # Conditions
    send_conditions = Column(JSON, default=dict)
    
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    drip_campaign = relationship("DripCampaign", back_populates="emails")

class Automation(Base):
    """Email automation model"""
    __tablename__ = 'automations'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Trigger
    trigger_type = Column(String(50), nullable=False)  # contact_added, date_based, behavior
    trigger_config = Column(JSON, default=dict)
    
    # Actions
    actions = Column(JSON, default=list)  # List of actions to perform
    
    # Settings
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    
    # Statistics
    triggered_count = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ApiKey(Base):
    """API key model for integrations"""
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    key_hash = Column(String(255), nullable=False)
    permissions = Column(JSON, default=list)
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Webhook(Base):
    """Webhook model for external integrations"""
    __tablename__ = 'webhooks'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    events = Column(JSON, default=list)  # Events to listen for
    secret = Column(String(255))
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)

# Initialize database
if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")

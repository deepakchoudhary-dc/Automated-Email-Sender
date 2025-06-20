#!/usr/bin/env python3
"""
Database initialization script for Automated Email Sender
"""

import os
import sys
from datetime import datetime
import argparse

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.models import (
    create_tables, drop_tables, db_session,
    User, EmailTemplate, Contact, ContactList
)
from src.utils.logger import setup_logging, get_logger
from src.auth.authentication import Authentication

logger = get_logger(__name__)

def init_database():
    """Initialize database with tables"""
    try:
        logger.info("Creating database tables...")
        create_tables()
        logger.info("Database tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    try:
        logger.info("Creating sample data...")
        
        with db_session() as session:
            # Create sample user
            auth = Authentication()
            sample_user = User(
                first_name="Demo",
                last_name="User",
                email="demo@example.com",
                password_hash=auth._hash_password("demo123"),
                company="Demo Company",
                role="admin",
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow()
            )
            session.add(sample_user)
            session.flush()  # To get the user ID
            
            # Create sample contacts
            sample_contacts = [
                Contact(
                    user_id=sample_user.id,
                    email="john.doe@example.com",
                    first_name="John",
                    last_name="Doe",
                    company="Tech Corp",
                    phone="+1234567890",
                    status="active",
                    source="manual",
                    created_at=datetime.utcnow()
                ),
                Contact(
                    user_id=sample_user.id,
                    email="jane.smith@example.com",
                    first_name="Jane",
                    last_name="Smith",
                    company="Design Studio",
                    phone="+1234567891",
                    status="active",
                    source="manual",
                    created_at=datetime.utcnow()
                ),
                Contact(
                    user_id=sample_user.id,
                    email="bob.johnson@example.com",
                    first_name="Bob",
                    last_name="Johnson",
                    company="Marketing Inc",
                    status="active",
                    source="manual",
                    created_at=datetime.utcnow()
                )
            ]
            
            for contact in sample_contacts:
                session.add(contact)
            
            # Create sample templates
            welcome_template = EmailTemplate(
                user_id=sample_user.id,
                name="Welcome Email",
                subject="Welcome to {{company}}, {{first_name}}!",
                html_content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Welcome!</title>
                </head>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #667eea;">Welcome, {{first_name}}!</h1>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <p>Thank you for joining {{company}}. We're excited to have you on board!</p>
                        <p>Here's what you can expect from us:</p>
                        <ul>
                            <li>Regular updates and newsletters</li>
                            <li>Exclusive offers and promotions</li>
                            <li>Tips and insights from our team</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="#" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; font-weight: bold;">
                            Get Started
                        </a>
                    </div>
                    
                    <div style="border-top: 1px solid #e9ecef; padding-top: 20px; margin-top: 30px; text-align: center; color: #666; font-size: 14px;">
                        <p>If you have any questions, feel free to reply to this email.</p>
                        <p>Best regards,<br>The {{company}} Team</p>
                        <p>© 2025 {{company}}. All rights reserved.</p>
                    </div>
                </body>
                </html>
                """,
                text_content="""
                Welcome, {{first_name}}!
                
                Thank you for joining {{company}}. We're excited to have you on board!
                
                Here's what you can expect from us:
                - Regular updates and newsletters
                - Exclusive offers and promotions
                - Tips and insights from our team
                
                If you have any questions, feel free to reply to this email.
                
                Best regards,
                The {{company}} Team
                """,
                template_type="predefined",
                category="welcome",
                variables=["first_name", "company"],
                is_public=True,
                created_at=datetime.utcnow()
            )
            session.add(welcome_template)
            
            newsletter_template = EmailTemplate(
                user_id=sample_user.id,
                name="Monthly Newsletter",
                subject="{{company}} Newsletter - {{month}} Edition",
                html_content="""
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
                            <p style="margin: 10px 0 0 0; opacity: 0.9;">Your monthly dose of insights</p>
                        </div>
                        <div style="padding: 30px 20px;">
                            <h2 style="color: #333; margin-top: 0;">Hello {{first_name}}!</h2>
                            <p>Here are the latest updates from our team:</p>
                            
                            <div style="border-left: 4px solid #667eea; padding-left: 20px; margin: 20px 0;">
                                <h3 style="color: #667eea; margin: 0 0 10px 0;">Featured Article</h3>
                                <p>This month we're featuring insights on email marketing best practices and how to improve your engagement rates.</p>
                            </div>
                            
                            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 6px; margin: 20px 0;">
                                <h3 style="color: #333; margin: 0 0 10px 0;">Quick Tips</h3>
                                <ul style="margin: 0; padding-left: 20px;">
                                    <li>Personalize your email subject lines</li>
                                    <li>Test different send times</li>
                                    <li>Segment your audience for better results</li>
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
                """,
                template_type="predefined",
                category="newsletter",
                variables=["first_name", "company", "month"],
                is_public=True,
                created_at=datetime.utcnow()
            )
            session.add(newsletter_template)
            
            # Create sample contact list
            sample_list = ContactList(
                user_id=sample_user.id,
                name="Demo Contacts",
                description="Sample contact list for demonstration",
                tags=["demo", "sample"],
                created_at=datetime.utcnow()
            )
            session.add(sample_list)
            
            session.commit()
            
        logger.info("Sample data created successfully!")
        logger.info("Demo user credentials: demo@example.com / demo123")
        return True
        
    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")
        return False

def reset_database():
    """Reset database by dropping and recreating tables"""
    try:
        logger.info("Resetting database...")
        drop_tables()
        logger.info("Database tables dropped")
        
        if init_database():
            logger.info("Database reset successfully!")
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Database initialization script")
    parser.add_argument(
        'action',
        choices=['init', 'reset', 'sample'],
        help='Action to perform: init (create tables), reset (drop and recreate), sample (add sample data)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger.info("Starting database initialization script...")
    
    success = False
    
    if args.action == 'init':
        success = init_database()
    elif args.action == 'reset':
        success = reset_database()
    elif args.action == 'sample':
        success = create_sample_data()
    
    if success:
        logger.info(f"Database {args.action} completed successfully!")
        print(f"✅ Database {args.action} completed successfully!")
        
        if args.action in ['init', 'reset']:
            print("\n📝 Next steps:")
            print("1. Run 'python init_db.py sample' to add sample data")
            print("2. Start the application with 'streamlit run app.py'")
            print("3. Login with demo@example.com / demo123")
        
    else:
        logger.error(f"Database {args.action} failed!")
        print(f"❌ Database {args.action} failed! Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()

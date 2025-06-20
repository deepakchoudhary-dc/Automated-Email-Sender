"""
AI Content Generation Service for email content creation and optimization.
"""

import openai
import json
from typing import Dict, List, Any, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AIContentService:
    """AI-powered content generation and optimization"""
    
    def __init__(self):
        # Initialize OpenAI client (would use API key from environment)
        # openai.api_key = os.getenv("OPENAI_API_KEY")
        pass
    
    def generate_email_content(self, prompt: str, email_type: str = "promotional", 
                             tone: str = "professional", target_audience: str = "general") -> Dict[str, str]:
        """Generate email content based on prompt and parameters."""
        try:
            # For demo purposes, return predefined content
            # In production, this would call OpenAI API
            
            templates = {
                "promotional": {
                    "subject": f"🎉 Special Offer: {prompt[:30]}...",
                    "content": f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; text-align: center; color: white;">
                            <h1 style="margin: 0; font-size: 28px;">Special Offer Just for You!</h1>
                        </div>
                        
                        <div style="padding: 30px; background: #f9f9f9;">
                            <h2 style="color: #333; font-size: 24px;">About {prompt}</h2>
                            <p style="color: #666; font-size: 16px; line-height: 1.6;">
                                We're excited to share this amazing opportunity with you. Our latest offering
                                combines quality, value, and innovation to deliver exactly what you've been looking for.
                            </p>
                            
                            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                                <h3 style="color: #333; margin-top: 0;">Key Benefits:</h3>
                                <ul style="color: #666; line-height: 1.6;">
                                    <li>Premium quality guaranteed</li>
                                    <li>Exclusive pricing for subscribers</li>
                                    <li>Limited time availability</li>
                                    <li>Money-back guarantee</li>
                                </ul>
                            </div>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="#" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                                    Get Started Now
                                </a>
                            </div>
                            
                            <p style="color: #999; font-size: 14px; text-align: center;">
                                This offer expires soon. Don't miss out!
                            </p>
                        </div>
                        
                        <div style="background: #333; padding: 20px; text-align: center; color: #ccc; font-size: 12px;">
                            <p>© 2025 Your Company. All rights reserved.</p>
                            <p><a href="#" style="color: #667eea;">Unsubscribe</a> | <a href="#" style="color: #667eea;">Update Preferences</a></p>
                        </div>
                    </body>
                    </html>
                    """
                },
                "welcome": {
                    "subject": f"Welcome to our community! 👋",
                    "content": f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 40px; text-align: center; color: white;">
                            <h1 style="margin: 0; font-size: 28px;">Welcome to Our Community!</h1>
                            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">We're thrilled to have you on board</p>
                        </div>
                        
                        <div style="padding: 30px; background: #f9f9f9;">
                            <h2 style="color: #333; font-size: 22px;">Hi there! 🎉</h2>
                            <p style="color: #666; font-size: 16px; line-height: 1.6;">
                                Thank you for joining us! You're now part of an amazing community focused on {prompt}.
                                We can't wait to share valuable insights, tips, and exclusive content with you.
                            </p>
                            
                            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                                <h3 style="color: #333; margin-top: 0;">What to expect:</h3>
                                <ul style="color: #666; line-height: 1.6;">
                                    <li>Weekly newsletters with valuable content</li>
                                    <li>Exclusive tips and strategies</li>
                                    <li>Early access to new features</li>
                                    <li>Special member-only discounts</li>
                                </ul>
                            </div>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="#" style="background: #4facfe; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                                    Get Started
                                </a>
                            </div>
                            
                            <p style="color: #666; font-size: 14px;">
                                Have questions? Just reply to this email - we're here to help!
                            </p>
                        </div>
                        
                        <div style="background: #333; padding: 20px; text-align: center; color: #ccc; font-size: 12px;">
                            <p>© 2025 Your Company. All rights reserved.</p>
                            <p><a href="#" style="color: #4facfe;">Manage Preferences</a></p>
                        </div>
                    </body>
                    </html>
                    """
                },
                "newsletter": {
                    "subject": f"📰 This Week: {prompt[:40]}...",
                    "content": f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background: #2c3e50; padding: 30px; text-align: center; color: white;">
                            <h1 style="margin: 0; font-size: 26px;">Weekly Newsletter</h1>
                            <p style="margin: 10px 0 0 0; opacity: 0.8;">Stay informed with the latest updates</p>
                        </div>
                        
                        <div style="padding: 30px; background: white;">
                            <h2 style="color: #2c3e50; font-size: 22px; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                                This Week's Highlights
                            </h2>
                            
                            <div style="margin: 20px 0;">
                                <h3 style="color: #333; font-size: 18px;">📈 {prompt}</h3>
                                <p style="color: #666; line-height: 1.6;">
                                    Discover the latest trends and insights that matter to you. Our team has curated
                                    the most important updates and actionable tips for this week.
                                </p>
                            </div>
                            
                            <div style="background: #ecf0f1; padding: 20px; border-radius: 8px; margin: 20px 0;">
                                <h4 style="color: #2c3e50; margin-top: 0;">📚 Featured Articles</h4>
                                <ul style="color: #555; line-height: 1.8;">
                                    <li><a href="#" style="color: #3498db; text-decoration: none;">Understanding the Latest Trends</a></li>
                                    <li><a href="#" style="color: #3498db; text-decoration: none;">Best Practices You Should Know</a></li>
                                    <li><a href="#" style="color: #3498db; text-decoration: none;">Expert Tips for Success</a></li>
                                </ul>
                            </div>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="#" style="background: #3498db; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                                    Read Full Newsletter
                                </a>
                            </div>
                        </div>
                        
                        <div style="background: #34495e; padding: 20px; text-align: center; color: #bdc3c7; font-size: 12px;">
                            <p>© 2025 Your Company Newsletter. All rights reserved.</p>
                            <p><a href="#" style="color: #3498db;">Unsubscribe</a> | <a href="#" style="color: #3498db;">Forward to a Friend</a></p>
                        </div>
                    </body>
                    </html>
                    """
                }
            }
            
            template = templates.get(email_type, templates["promotional"])
            return template
            
        except Exception as e:
            logger.error(f"AI content generation failed: {str(e)}")
            return {
                "subject": "AI Generated Subject",
                "content": "<p>AI generated content would appear here.</p>"
            }
    
    def optimize_subject_line(self, original_subject: str, email_content: str, target_audience: str) -> List[str]:
        """Generate optimized subject line variations."""
        try:
            # For demo purposes, return variations
            # In production, would use AI to analyze and optimize
            
            variations = [
                f"✨ {original_subject}",
                f"🎯 {original_subject} - Limited Time",
                f"Don't miss: {original_subject}",
                f"Exclusive: {original_subject}",
                f"Last chance: {original_subject}",
                f"Breaking: {original_subject}",
                f"🔥 Hot: {original_subject}",
                f"Urgent: {original_subject}"
            ]
            
            return variations[:5]  # Return top 5 variations
            
        except Exception as e:
            logger.error(f"Subject line optimization failed: {str(e)}")
            return [original_subject]
    
    def analyze_content_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze the sentiment and tone of email content."""
        try:
            # Simplified sentiment analysis for demo
            # In production, would use proper NLP libraries or AI APIs
            
            positive_words = ['great', 'amazing', 'excellent', 'fantastic', 'wonderful', 'awesome', 'love', 'best']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disappointing']
            
            content_lower = content.lower()
            positive_count = sum(1 for word in positive_words if word in content_lower)
            negative_count = sum(1 for word in negative_words if word in content_lower)
            
            if positive_count > negative_count:
                sentiment = "positive"
                score = min(0.8, 0.5 + (positive_count - negative_count) * 0.1)
            elif negative_count > positive_count:
                sentiment = "negative"
                score = max(0.2, 0.5 - (negative_count - positive_count) * 0.1)
            else:
                sentiment = "neutral"
                score = 0.5
            
            return {
                "sentiment": sentiment,
                "score": round(score, 2),
                "tone": "professional" if "formal" in content_lower else "casual",
                "readability": "good",  # Would calculate actual readability score
                "suggestions": [
                    "Consider adding more emotional appeal",
                    "Include a clear call-to-action",
                    "Personalize the greeting"
                ]
            }
            
        except Exception as e:
            logger.error(f"Content sentiment analysis failed: {str(e)}")
            return {"sentiment": "neutral", "score": 0.5}
    
    def generate_personalization_tags(self, contact_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate personalization suggestions based on contact data."""
        try:
            tags = {}
            
            # Basic personalization
            if contact_data.get('first_name'):
                tags['first_name'] = contact_data['first_name']
            if contact_data.get('last_name'):
                tags['last_name'] = contact_data['last_name']
            if contact_data.get('company'):
                tags['company'] = contact_data['company']
            
            # Location-based
            if contact_data.get('city'):
                tags['city'] = contact_data['city']
            if contact_data.get('country'):
                tags['country'] = contact_data['country']
            
            # Behavioral
            if contact_data.get('last_purchase_date'):
                tags['last_purchase'] = contact_data['last_purchase_date']
            if contact_data.get('favorite_category'):
                tags['interest'] = contact_data['favorite_category']
            
            # Time-based
            tags['current_time'] = "morning"  # Would calculate based on contact's timezone
            tags['day_of_week'] = "Wednesday"  # Would get actual day
            
            return tags
            
        except Exception as e:
            logger.error(f"Personalization tag generation failed: {str(e)}")
            return {}
    
    def suggest_send_time(self, contact_data: Dict[str, Any], historical_data: List[Dict]) -> Dict[str, Any]:
        """Suggest optimal send time based on contact behavior and historical data."""
        try:
            # Analyze historical open/click patterns
            # For demo, return suggested times
            
            suggestions = {
                "optimal_day": "Tuesday",
                "optimal_time": "10:00 AM",
                "timezone": contact_data.get('timezone', 'UTC'),
                "confidence": 0.75,
                "reasoning": "Based on historical engagement patterns, Tuesday mornings show 23% higher open rates for similar contacts.",
                "alternatives": [
                    {"day": "Wednesday", "time": "2:00 PM", "confidence": 0.68},
                    {"day": "Thursday", "time": "9:00 AM", "confidence": 0.65}
                ]
            }
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Send time suggestion failed: {str(e)}")
            return {"optimal_day": "Tuesday", "optimal_time": "10:00 AM"}
    
    def generate_ab_test_variations(self, base_content: Dict[str, str], test_type: str) -> List[Dict[str, str]]:
        """Generate A/B test variations for content."""
        try:
            variations = []
            base_subject = base_content.get('subject', '')
            base_html = base_content.get('content', '')
            
            if test_type == "subject_line":
                # Generate subject line variations
                subject_variations = self.optimize_subject_line(base_subject, base_html, "general")
                for i, subject in enumerate(subject_variations[:3]):
                    variations.append({
                        "version": f"Variation {i+1}",
                        "subject": subject,
                        "content": base_html,
                        "changes": f"Modified subject line: {subject}"
                    })
            
            elif test_type == "content":
                # Generate content variations
                variations = [
                    {
                        "version": "Variation 1",
                        "subject": base_subject,
                        "content": base_html.replace("Get Started Now", "Start Your Journey"),
                        "changes": "Changed CTA button text"
                    },
                    {
                        "version": "Variation 2", 
                        "subject": base_subject,
                        "content": base_html.replace("Special Offer", "Exclusive Deal"),
                        "changes": "Changed headline wording"
                    }
                ]
            
            elif test_type == "send_time":
                # Generate time-based variations
                variations = [
                    {
                        "version": "Morning Send",
                        "subject": base_subject,
                        "content": base_html,
                        "send_time": "09:00",
                        "changes": "Send at 9:00 AM"
                    },
                    {
                        "version": "Afternoon Send",
                        "subject": base_subject,
                        "content": base_html,
                        "send_time": "14:00",
                        "changes": "Send at 2:00 PM"
                    }
                ]
            
            return variations
            
        except Exception as e:
            logger.error(f"A/B test variation generation failed: {str(e)}")
            return []
    
    def analyze_spam_score(self, subject: str, content: str) -> Dict[str, Any]:
        """Analyze content for potential spam indicators."""
        try:
            spam_words = [
                'free', 'urgent', 'limited time', 'act now', 'click here', 
                'guaranteed', 'no risk', 'winner', 'congratulations',
                'cash', 'money', 'income', 'offer expires', 'order now'
            ]
            
            content_text = content.lower().replace('<', ' ').replace('>', ' ')
            full_text = f"{subject.lower()} {content_text}"
            
            spam_indicators = []
            score = 0
            
            # Check for spam words
            for word in spam_words:
                if word in full_text:
                    spam_indicators.append(f"Contains '{word}'")
                    score += 1
            
            # Check for excessive caps
            if len([c for c in subject if c.isupper()]) > len(subject) * 0.5:
                spam_indicators.append("Too many capital letters in subject")
                score += 2
            
            # Check for excessive exclamation marks
            if subject.count('!') > 2:
                spam_indicators.append("Too many exclamation marks")
                score += 1
            
            # Calculate final score (0-100)
            spam_percentage = min(100, (score / 15) * 100)
            
            risk_level = "low"
            if spam_percentage > 60:
                risk_level = "high"
            elif spam_percentage > 30:
                risk_level = "medium"
            
            return {
                "spam_score": round(spam_percentage, 1),
                "risk_level": risk_level,
                "indicators": spam_indicators,
                "suggestions": [
                    "Reduce use of promotional language",
                    "Avoid excessive punctuation",
                    "Include personalization",
                    "Add unsubscribe link"
                ]
            }
            
        except Exception as e:
            logger.error(f"Spam score analysis failed: {str(e)}")
            return {"spam_score": 0, "risk_level": "low"}

# Global AI service instance  
ai_content_service = AIContentService()

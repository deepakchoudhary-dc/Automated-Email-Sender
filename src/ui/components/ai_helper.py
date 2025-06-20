"""
AI Helper Component for integrated AI assistance in the UI.
"""

import streamlit as st
from typing import Dict, List, Any, Optional
from src.services.ai_content_service import AIContentService
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AIHelper:
    def __init__(self):
        self.ai_service = AIContentService()
    
    def render_content_generator(self) -> Optional[Dict[str, str]]:
        """Render AI content generator interface."""
        st.subheader("🤖 AI Content Generator")
        
        with st.form("ai_content_generator"):
            col1, col2 = st.columns(2)
            
            with col1:
                email_type = st.selectbox(
                    "Email Type",
                    ["promotional", "welcome", "newsletter", "announcement", "follow-up"]
                )
                tone = st.selectbox(
                    "Tone",
                    ["professional", "casual", "friendly", "urgent", "inspirational"]
                )
                
            with col2:
                target_audience = st.text_input("Target Audience", "customers")
                company_name = st.text_input("Company Name", "Your Company")
            
            description = st.text_area(
                "Brief Description",
                "Describe what this email should accomplish...",
                height=100
            )
            
            if st.form_submit_button("Generate Content", use_container_width=True):
                if description.strip():
                    with st.spinner("Generating AI content..."):
                        content = self._generate_email_content(
                            email_type, tone, target_audience, company_name, description
                        )
                        return content
                else:
                    st.error("Please provide a description")
        
        return None

    def render_content_generator_inline(self) -> Optional[Dict[str, str]]:
        """Render AI content generator interface without forms (for use inside other forms)."""
        st.subheader("🤖 AI Content Generator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email_type = st.selectbox(
                "Email Type",
                ["promotional", "welcome", "newsletter", "announcement", "follow-up"],
                key="ai_email_type_inline"
            )
            tone = st.selectbox(
                "Tone",
                ["professional", "casual", "friendly", "urgent", "inspirational"],
                key="ai_tone_inline"
            )
            
        with col2:
            target_audience = st.text_input("Target Audience", "customers", key="ai_audience_inline")
            company_name = st.text_input("Company Name", "Your Company", key="ai_company_inline")
        
        description = st.text_area(
            "Brief Description",
            "Describe what this email should accomplish...",
            height=100,
            key="ai_description_inline"
        )
        
        # Store the inputs in session state for later use
        st.session_state.ai_inputs = {
            'email_type': email_type,
            'tone': tone,
            'target_audience': target_audience,
            'company_name': company_name,
            'description': description
        }
        
        st.info("💡 Fill in the details above and use the form's submit button to generate AI content.")
        
        return None
    
    def render_subject_optimizer(self, current_subject: str, email_content: str = "") -> List[str]:
        """Render subject line optimizer."""
        st.subheader("📝 Subject Line Optimizer")
        
        if not current_subject:
            st.info("Enter a subject line to get optimization suggestions")
            return []
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                target_audience = st.selectbox(
                    "Target Audience", 
                    ["general", "new_subscribers", "loyal_customers", "prospects"],
                    key="subject_optimizer_audience"
                )
            
            with col2:
                if st.button("Optimize", type="primary", key="optimize_subject"):
                    with st.spinner("Optimizing subject line..."):
                        variations = self.ai_service.optimize_subject_line(
                            current_subject, email_content, target_audience
                        )
                        
                        if variations:
                            st.subheader("✨ Optimized Variations")
                            for i, variation in enumerate(variations):
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    st.text(variation)
                                with col2:
                                    if st.button("Use", key=f"use_subject_{i}"):
                                        st.session_state.optimized_subject = variation
                                        st.success("Subject line updated!")
                        
                        return variations
        
        return []
    
    def render_content_analyzer(self, content: str) -> Dict[str, Any]:
        """Render content analysis tools."""
        st.subheader("🔍 Content Analyzer")
        
        if not content:
            st.info("Enter email content to analyze")
            return {}
        
        # Tabs for different analysis types
        tab1, tab2, tab3 = st.tabs(["📊 Sentiment", "⚠️ Spam Check", "📱 Preview"])
        
        with tab1:
            sentiment_analysis = self.ai_service.analyze_content_sentiment(content)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sentiment", sentiment_analysis.get('sentiment', 'Unknown'))
            with col2:
                st.metric("Score", f"{sentiment_analysis.get('score', 0):.2f}")
            with col3:
                st.metric("Tone", sentiment_analysis.get('tone', 'Unknown'))
            
            if sentiment_analysis.get('suggestions'):
                st.subheader("💡 Suggestions")
                for suggestion in sentiment_analysis['suggestions']:
                    st.write(f"• {suggestion}")
        
        with tab2:
            spam_analysis = self.ai_service.analyze_spam_score(
                st.session_state.get('email_subject', ''), content
            )
            
            col1, col2 = st.columns(2)
            with col1:
                score = spam_analysis.get('spam_score', 0)
                risk_level = spam_analysis.get('risk_level', 'low')
                
                color = "green" if risk_level == "low" else "orange" if risk_level == "medium" else "red"
                st.metric("Spam Score", f"{score}%", help=f"Risk level: {risk_level}")
                
                if score > 30:
                    st.warning(f"High spam risk detected ({risk_level} risk)")
                else:
                    st.success("Low spam risk")
            
            with col2:
                if spam_analysis.get('indicators'):
                    st.subheader("⚠️ Issues Found")
                    for indicator in spam_analysis['indicators']:
                        st.write(f"• {indicator}")
                
                if spam_analysis.get('suggestions'):
                    st.subheader("💡 Improvements")
                    for suggestion in spam_analysis['suggestions']:
                        st.write(f"• {suggestion}")
        
        with tab3:
            st.subheader("📱 Mobile Preview")
            # Simplified mobile preview
            with st.container():
                st.markdown(
                    f"""
                    <div style="
                        max-width: 320px; 
                        border: 2px solid #ccc; 
                        border-radius: 10px; 
                        padding: 10px; 
                        background: white;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    ">
                        <div style="font-size: 12px; color: #666; margin-bottom: 10px;">
                            Mobile Preview
                        </div>
                        <div style="font-size: 14px; line-height: 1.4;">
                            {content[:200]}...
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        
        return {"sentiment": sentiment_analysis, "spam": spam_analysis}
    
    def render_ab_test_generator(self, base_content: Dict[str, str]) -> List[Dict[str, str]]:
        """Render A/B test variation generator."""
        st.subheader("🧪 A/B Test Generator")
        
        if not base_content:
            st.info("Create base content first to generate A/B test variations")
            return []
        
        test_type = st.selectbox(
            "What to test",
            ["subject_line", "content", "send_time", "sender_name"]
        )
        
        if st.button("Generate Variations", type="primary", key="generate_ab_variations"):
            with st.spinner("Generating A/B test variations..."):
                variations = self.ai_service.generate_ab_test_variations(base_content, test_type)
                
                if variations:
                    st.subheader("🔬 Test Variations")
                    for i, variation in enumerate(variations):
                        with st.expander(f"Variation {i+1}: {variation.get('version', 'Unknown')}"):
                            st.write(f"**Changes:** {variation.get('changes', 'None specified')}")
                            if test_type == "subject_line":
                                st.write(f"**Subject:** {variation.get('subject', '')}")
                            elif test_type == "content":
                                st.write("**Content Preview:**")
                                st.text(variation.get('content', '')[:200] + "...")
                            elif test_type == "send_time":
                                st.write(f"**Send Time:** {variation.get('send_time', '')}")
                
                return variations
        
        return []
    
    def render_personalization_helper(self, contact_data: Dict[str, Any] = None) -> Dict[str, str]:
        """Render personalization helper."""
        st.subheader("👤 Personalization Helper")
        
        if not contact_data:
            st.info("Contact data will be used to suggest personalization tags")
            return {}
        
        tags = self.ai_service.generate_personalization_tags(contact_data)
        
        if tags:
            st.subheader("🏷️ Available Tags")
            
            col1, col2 = st.columns(2)
            for i, (tag, value) in enumerate(tags.items()):
                with col1 if i % 2 == 0 else col2:
                    st.code(f"{{{{ {tag} }}}}", language="html")
                    st.caption(f"Example: {value}")
        
        # Show usage examples
        st.subheader("💡 Usage Examples")
        examples = [
            "Hi {{ first_name }}, welcome to our newsletter!",
            "Special offer for {{ city }} residents",
            "Thank you for your {{ last_purchase }} purchase",
            "Good {{ current_time }}, {{ first_name }}!"
        ]
        
        for example in examples:
            st.code(example, language="html")
        
        return tags
    
    def render_send_time_optimizer(self, contact_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Render send time optimization helper."""
        st.subheader("⏰ Send Time Optimizer")
        
        # Sample historical data for demo
        historical_data = []
        
        optimization = self.ai_service.suggest_send_time(contact_data or {}, historical_data)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Optimal Day", optimization.get('optimal_day', 'Tuesday'))
        
        with col2:
            st.metric("Optimal Time", optimization.get('optimal_time', '10:00 AM'))
        
        with col3:
            confidence = optimization.get('confidence', 0.75)
            st.metric("Confidence", f"{confidence*100:.0f}%")
        
        if optimization.get('reasoning'):
            st.info(optimization['reasoning'])
        
        # Show alternatives
        if optimization.get('alternatives'):
            st.subheader("🔄 Alternative Times")
            for alt in optimization['alternatives']:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(alt.get('day', 'Unknown'))
                with col2:
                    st.write(alt.get('time', 'Unknown'))
                with col3:
                    st.write(f"{alt.get('confidence', 0)*100:.0f}%")
        
        return optimization
    
    def render_quick_templates(self) -> Optional[Dict[str, str]]:
        """Render quick template suggestions."""
        st.subheader("⚡ Quick Templates")
        
        template_types = {
            "Welcome Email": {
                "subject": "Welcome to our community! 👋",
                "description": "Perfect for new subscribers"
            },
            "Product Launch": {
                "subject": "🚀 Exciting News: Our Latest Product is Here!",
                "description": "Announce new products or features"
            },
            "Newsletter": {
                "subject": "📰 Weekly Roundup: What You Missed",
                "description": "Regular newsletter template"
            },
            "Promotional": {
                "subject": "🎉 Limited Time: Special Offer Inside",
                "description": "Sales and promotional emails"
            },
            "Re-engagement": {
                "subject": "We miss you! Come back for exclusive offers",
                "description": "Win back inactive subscribers"
            }
        }
        
        for template_name, template_info in template_types.items():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"**{template_name}**")
                    st.caption(template_info['description'])
                
                with col2:
                    st.code(template_info['subject'])
                
                with col3:
                    if st.button("Use", key=f"template_{template_name}"):
                        # Generate content for this template type
                        content = self.ai_service.generate_email_content(
                            template_name.lower(), template_name.lower().replace(' ', '_')
                        )
                        st.session_state.selected_template = {
                            "name": template_name,
                            "content": content
                        }
                        st.success(f"Loaded {template_name} template!")
                        return content
                
                st.divider()
        
        return None

    def _generate_email_content(self, email_type: str, tone: str, target_audience: str, company_name: str, description: str) -> Dict[str, str]:
        """Generate email content using AI (simulated)."""
        try:
            # This is a simulated AI content generation
            # In a real implementation, you would call an AI API like OpenAI, Anthropic, etc.
            
            # Generate subject based on email type and tone
            subject_templates = {
                'promotional': {
                    'professional': f"Exclusive Offer from {company_name}",
                    'casual': f"Hey! Check out this deal from {company_name}",
                    'friendly': f"We've got something special for you!",
                    'urgent': f"Limited Time: {company_name} Special Offer",
                    'inspirational': f"Transform Your Experience with {company_name}"
                },
                'welcome': {
                    'professional': f"Welcome to {company_name}",
                    'casual': f"Welcome aboard! 🎉",
                    'friendly': f"So happy to have you with us!",
                    'urgent': f"Action Required: Complete Your {company_name} Setup",
                    'inspirational': f"Your Journey with {company_name} Begins Now"
                },
                'newsletter': {
                    'professional': f"{company_name} Newsletter - Latest Updates",
                    'casual': f"What's new at {company_name}?",
                    'friendly': f"Your monthly update from friends at {company_name}",
                    'urgent': f"Breaking: Important Updates from {company_name}",
                    'inspirational': f"Discover What's Possible This Month"
                },
                'announcement': {
                    'professional': f"Important Announcement from {company_name}",
                    'casual': f"Big news from {company_name}!",
                    'friendly': f"We have some exciting news to share!",
                    'urgent': f"Urgent: {company_name} Announcement",
                    'inspirational': f"Exciting Changes Are Coming"
                },
                'follow-up': {
                    'professional': f"Following up on your {company_name} inquiry",
                    'casual': f"Just checking in!",
                    'friendly': f"How are things going?",
                    'urgent': f"Time-sensitive follow-up",
                    'inspirational': f"Let's continue your success story"
                }
            }
            
            subject = subject_templates.get(email_type, {}).get(tone, f"{email_type.title()} from {company_name}")
            
            # Generate content based on description and parameters
            content_intro = {
                'professional': f"Dear {{{{first_name}}}},",
                'casual': f"Hi {{{{first_name}}}}!",
                'friendly': f"Hello {{{{first_name}}}},",
                'urgent': f"{{{{first_name}}}}, this is important:",
                'inspirational': f"{{{{first_name}}}}, are you ready to transform your experience?"
            }
            
            intro = content_intro.get(tone, f"Hello {{{{first_name}}}},")
            
            # Create HTML content
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .content {{ line-height: 1.6; color: #333; }}
                    .cta {{ text-align: center; margin: 30px 0; }}
                    .cta a {{ background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; }}
                    .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{company_name}</h1>
                    </div>
                    <div class="content">
                        <p>{intro}</p>
                        <p>{description}</p>
                        <p>We value our {target_audience} and are committed to providing you with the best experience possible.</p>
                    </div>
                    <div class="cta">
                        <a href="{{{{action_url}}}}">Take Action</a>
                    </div>
                    <div class="footer">
                        <p>Best regards,<br>The {company_name} Team</p>
                        <p><a href="{{{{unsubscribe_url}}}}">Unsubscribe</a> | <a href="{{{{company_url}}}}">{company_name}</a></p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return {
                'subject': subject,
                'content': html_content.strip()
            }
            
        except Exception as e:
            # Fallback content if generation fails
            return {
                'subject': f"{email_type.title()} from {company_name}",
                'content': f"""
                <html>
                <body>
                    <h2>{company_name}</h2>
                    <p>Hello {{{{first_name}}}},</p>
                    <p>{description}</p>
                    <p>Best regards,<br>The {company_name} Team</p>
                </body>
                </html>
                """.strip()
            }

# Global AI helper instance
ai_helper = AIHelper()

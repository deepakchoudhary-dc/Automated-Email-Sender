# Automated Email Sender - Advanced Streamlit Application

## 🚀 Features

- **Bulk Email Sending**: Send emails to large lists efficiently
- **Personalization**: Dynamic templates with custom fields
- **Drip Campaigns**: Automated email sequences and scheduling
- **Advanced Analytics**: Delivery tracking, open rates, click tracking
- **Multi-Provider Support**: SendGrid, AWS SES, Gmail API
- **Template Management**: Visual email editor with HTML support
- **Contact Management**: Advanced segmentation and filtering
- **File Attachments**: Support for multiple file types
- **Security**: OAuth2 authentication, encrypted credentials
- **GDPR Compliance**: Unsubscribe links, data protection
- **AI Integration**: Content generation and optimization
- **Real-time Monitoring**: Live campaign status and logs

## 🛠️ Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (see `.env.example`)
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## 📋 Configuration

Create a `.env` file with your API keys and configuration:

```env
# Email Service Provider
SENDGRID_API_KEY=your_sendgrid_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/email_sender

# Redis (for background tasks)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here

# Monitoring
SENTRY_DSN=your_sentry_dsn
```

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. **Fork or Clone** this repository
2. **Connect to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select this repository
   - Set the main file as `app.py`

3. **Configure Secrets**:
   - In Streamlit Cloud, go to "Settings" → "Secrets"
   - Copy the contents from `.streamlit/secrets.toml.example`
   - Add your actual API keys and configuration values

4. **Environment Variables Required**:
   ```toml
   FERNET_KEY = "your-base64-encoded-fernet-key"
   GOOGLE_CLIENT_ID = "your-google-oauth-client-id"
   GOOGLE_CLIENT_SECRET = "your-google-oauth-client-secret"
   SENDGRID_API_KEY = "your-sendgrid-api-key"
   OPENAI_API_KEY = "your-openai-api-key"  # Optional
   ```

5. **Deploy**: Click "Deploy" and your app will be live!

### Local Development

```bash
# Clone the repository
git clone https://github.com/deepakchoudhary-dc/Automated-Email-Sender.git
cd Automated-Email-Sender

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your actual values

# Initialize database
python init_db.py

# Run the application
streamlit run app.py
```

## 📊 Usage

1. **Authentication**: Log in with Google OAuth or create an account
2. **Contacts**: Import contacts from CSV/Excel or add manually
3. **Templates**: Create beautiful email templates with the visual editor
4. **Campaigns**: Set up bulk emails with personalization
5. **Scheduling**: Create drip campaigns and automated sequences
6. **Analytics**: Monitor performance with real-time dashboards

## 🔒 Security Features

- OAuth2 authentication
- Encrypted credential storage
- Rate limiting
- Input validation and sanitization
- CSRF protection
- Secure file upload handling

## 📈 Analytics

Track comprehensive email metrics:
- Delivery rates
- Open rates
- Click-through rates
- Bounce rates
- Unsubscribe rates
- Geographic analytics
- Device/client analytics

## 🤖 AI Features

- Content generation with GPT integration
- Subject line optimization
- Send time optimization
- Audience segmentation
- Spam score checking

## 📧 Supported Email Providers

- SendGrid
- AWS SES
- Gmail API
- Microsoft Graph API
- Custom SMTP servers

## 🎨 Template Features

- Drag-and-drop email builder
- Pre-built templates
- Custom HTML/CSS support
- Dynamic content blocks
- Image optimization
- Mobile responsive design

## 📱 Contact Management

- Advanced segmentation
- Custom fields
- Import/export functionality
- Duplicate detection
- Suppression lists
- GDPR compliance tools

## ⚡ Performance

- Async email sending
- Background task processing
- Rate limiting
- Connection pooling
- Caching strategies

## 🛡️ Compliance

- CAN-SPAM Act compliance
- GDPR compliance
- Automatic unsubscribe handling
- Data retention policies
- Audit logging

## 📞 Support

For issues and feature requests, please create an issue in the GitHub repository.

## 📄 License

MIT License - see LICENSE file for details.

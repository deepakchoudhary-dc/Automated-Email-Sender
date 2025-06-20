# Project Structure

## Automated Email Sender - Clean Structure

```
e:\Autoamted email sender\
├── .env                          # Environment variables (not in git)
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── app.py                        # Main Streamlit application
├── email_sender.db               # SQLite database
├── init_db.py                    # Database initialization script
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
├── logs/                         # Application logs
│   ├── email_sender_2025_06_12.log
│   ├── email_sender_2025_06_13.log
│   └── email_sender_2025_06_20.log
└── src/                          # Source code
    ├── __init__.py
    ├── auth/                     # Authentication
    │   ├── __init__.py
    │   └── authentication.py
    ├── database/                 # Database models
    │   ├── __init__.py
    │   └── models.py
    ├── services/                 # Business logic
    │   ├── __init__.py
    │   ├── ai_content_service.py
    │   ├── analytics_service.py
    │   ├── contact_service.py
    │   ├── email_service.py
    │   ├── template_service.py
    │   └── webhook_service.py
    ├── ui/                       # User interface
    │   ├── __init__.py
    │   ├── dashboard.py          # Main dashboard
    │   ├── sidebar_working.py    # Working sidebar
    │   └── components/           # UI components
    │       ├── __init__.py
    │       ├── ai_helper.py
    │       ├── analytics_dashboard.py
    │       ├── automation_builder.py
    │       ├── campaign_builder.py
    │       ├── contact_manager.py
    │       └── template_editor.py
    └── utils/                    # Utilities
        ├── __init__.py
        ├── google_oauth.py
        ├── logger.py
        ├── security.py
        └── session_state.py
```

## Removed Files (Unwanted/Duplicate)

### Removed for being duplicates:
- `src/ui/dashboard_simple.py` (duplicate of dashboard.py)
- `src/ui/sidebar.py` (replaced by sidebar_working.py)
- `src/ui/sidebar_simple.py` (duplicate)
- `src/ui/components/template_editor_fixed.py` (duplicate of template_editor.py)

### Removed for being temporary:
- `temp_fix.py` (temporary development file)
- `generate_keys.py` (utility file not needed for main app)

### Removed for being cache:
- All `__pycache__/` directories (Python bytecode cache)

## Clean Project Benefits

1. **No duplicate files** - Single source of truth for each component
2. **No cache files** - Cleaner repository
3. **Proper gitignore** - Prevents future cache/temp files from being committed
4. **Clear structure** - Easy to navigate and understand
5. **Production ready** - Only essential files remain

## Key Files

- **app.py**: Main application entry point
- **src/ui/dashboard.py**: Main UI dashboard
- **src/ui/sidebar_working.py**: Working sidebar implementation
- **src/services/email_service.py**: Core email sending functionality
- **src/services/contact_service.py**: Contact management
- **src/services/template_service.py**: Email template management
- **src/auth/authentication.py**: User authentication
- **.env**: Configuration (create from .env.example)

# StaffingPro - Contractor Management Platform

## Overview

StaffingPro is a Flask-based web application designed for staffing agencies to manage contractor information, track spread reports, and monitor contractor status. The system provides CSV upload functionality for batch updates, contractor management capabilities, and a review queue system for handling data discrepancies.

## System Architecture

### Backend Architecture
- **Framework**: Flask 3.1.1 with Python 3.11
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-Login for session management
- **Forms**: WTForms with Flask-WTF for form handling and validation
- **File Processing**: Pandas for CSV data processing
- **Deployment**: Gunicorn WSGI server on Replit

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Feather Icons
- **JavaScript**: Vanilla JavaScript with Bootstrap components

### Application Structure
```
├── app.py              # Application factory and configuration
├── main.py             # Application entry point
├── models.py           # Database models (User, Contractor)
├── routes.py           # URL routes and view functions
├── forms.py            # WTForms form definitions
├── utils.py            # Utility functions for data processing
├── templates/          # Jinja2 HTML templates
├── static/             # CSS, JS, and static assets
└── .replit            # Replit configuration
```

## Key Components

### Database Models
1. **User Model**: Handles user authentication with username, email, password hashing, and profile information
2. **Contractor Model**: Core entity storing contractor details including talent name, job title, status, dates, contact information, and financial data
3. **ReviewQueue Model**: Tracks contractors that need manual review when not found in uploads
4. **UploadHistory Model**: Maintains audit trail of CSV file uploads

### Authentication System
- Flask-Login integration for session management
- Password hashing using Werkzeug security functions
- User registration and login forms with validation
- Protected routes requiring authentication

### CSV Processing Pipeline
- File upload validation (CSV format, 16MB size limit)
- Pandas-based data parsing with multiple date format support
- Automatic contractor creation and updates
- Review queue population for missing contractors
- Error handling and user feedback

### Web Interface
- Responsive Bootstrap-based UI
- Dashboard with key metrics and statistics
- Contractor CRUD operations with search and filtering
- CSV upload interface with progress feedback
- Review queue for data validation

## Data Flow

1. **User Authentication**: Users log in through Flask-Login system
2. **Dashboard Access**: Authenticated users see contractor statistics and recent activity
3. **CSV Upload Process**:
   - File validation and parsing
   - Contractor data extraction and normalization
   - Database updates (create/update contractors)
   - Review queue population for missing records
4. **Contractor Management**: CRUD operations through web forms
5. **Review Queue**: Manual review of data discrepancies

## External Dependencies

### Python Packages
- **Flask Stack**: flask, flask-sqlalchemy, flask-login, flask-wtf
- **Database**: psycopg2-binary for PostgreSQL connectivity
- **Data Processing**: pandas for CSV handling
- **Security**: werkzeug for password hashing
- **Validation**: wtforms, email-validator
- **Server**: gunicorn for production deployment

### Frontend Dependencies
- **Bootstrap 5.3.0**: CSS framework via CDN
- **Feather Icons**: Icon library via CDN
- **Custom CSS/JS**: Local styling and functionality

### Infrastructure
- **PostgreSQL**: Primary database (configured via DATABASE_URL)
- **Replit**: Hosting platform with Nix package management
- **Environment Variables**: SESSION_SECRET, DATABASE_URL

## Deployment Strategy

### Replit Configuration
- **Runtime**: Python 3.11 with Nix package manager
- **Packages**: glibcLocales, openssl, postgresql
- **Deployment**: Autoscale target with Gunicorn
- **Process**: `gunicorn --bind 0.0.0.0:5000 main:app`

### Environment Setup
- Database connection via DATABASE_URL environment variable
- Session security via SESSION_SECRET
- File upload directory configuration
- SQLAlchemy connection pooling for reliability

### Production Considerations
- ProxyFix middleware for deployment behind reverse proxy
- Connection pool recycling every 300 seconds
- Pre-ping for connection health checking
- Debug mode disabled in production

## Changelog
- June 23, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.
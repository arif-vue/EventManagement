# Event Management System

A Django-based event management system that allows users to create, manage, and RSVP to events.

## Features

- User authentication and profile management
- Event creation and management
- Event categories
- RSVP functionality
- Admin dashboard
- Email notifications

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd event-management
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
1. Copy `.env.example` to `.env`
2. Fill in your actual values in the `.env` file:
   - `SECRET_KEY`: Generate a new Django secret key
   - `EMAIL_HOST_USER`: Your Gmail address
   - `EMAIL_HOST_PASSWORD`: Your Gmail app password (not your regular password)

### 5. Database Setup
```bash
python manage.py migrate
python manage.py setup_roles
python manage.py createsuperuser
```

### 6. Run the development server
```bash
python manage.py runserver
```

## Environment Variables

The following environment variables need to be set in your `.env` file:

- `SECRET_KEY`: Django secret key for security
- `DEBUG`: Set to True for development, False for production
- `EMAIL_HOST_USER`: Email address for sending notifications
- `EMAIL_HOST_PASSWORD`: App password for the email account

## Gmail App Password Setup

To get an app password for Gmail:
1. Enable 2-factor authentication on your Google account
2. Go to Google Account settings > Security > App passwords
3. Generate a new app password for "Mail"
4. Use this 16-character password in your `.env` file

## Security Notes

- Never commit your `.env` file to version control
- Use strong, unique passwords
- In production, set `DEBUG=False`
- Use environment-specific settings for production deployment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'your-secret-key-here'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'techhub.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False


# Email configuration
MAIL_SERVER = 'smtp.example.com'  # e.g., 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your-email@example.com'
MAIL_PASSWORD = 'your-email-password'
MAIL_DEFAULT_SENDER = 'your-email@example.com'
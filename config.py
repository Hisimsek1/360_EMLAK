"""
Configuration module for 360 Emlak Platform
Supports Development and Production environments
"""
import os
from datetime import timedelta


class Config:
    """Base configuration with common settings"""
    
    # Application
    APP_NAME = "360 Emlak"
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2024'
    
    # Session Configuration
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # CSRF tokens don't expire
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # JSON Database
    DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'data.json')
    
    # Logging
    LOG_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    LOG_FILE = os.path.join(LOG_FOLDER, 'app.log')
    
    # Pagination
    PROPERTIES_PER_PAGE = 12
    
    # Brand Colors (Updated to Navy Theme 2026)
    PRIMARY_COLOR = '#1E3A8A'  # Navy Blue
    SECONDARY_COLOR = '#FFFFFF'


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    ENV = 'development'
    
    # Less strict in development
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Strict security in production
    SESSION_COOKIE_SECURE = True
    
    # Must set these environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    def __init__(self):
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production!")


class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    ENV = 'testing'
    WTF_CSRF_ENABLED = False
    
    # Use separate test data file
    DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'test_data.json')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env_name=None):
    """
    Get configuration object based on environment name
    
    Args:
        env_name (str): Environment name ('development', 'production', 'testing')
                       If None, uses FLASK_ENV environment variable or 'development'
    
    Returns:
        Config: Configuration object
    """
    if env_name is None:
        env_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(env_name, config['default'])

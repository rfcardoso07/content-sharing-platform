"""
Configuration settings for the Flask application.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/content_sharing_platform'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('FLASK_ENV') == 'development'
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    )
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # API
    API_TITLE = 'Content Sharing Platform API'
    API_VERSION = 'v1'
    
    # Pagination
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/content_sharing_platform_test'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

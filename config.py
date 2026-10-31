import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if it exists
load_dotenv(BASE_DIR / '.env')


class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-insecure-secret-key-change-in-prod-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 9
    WTF_CSRF_ENABLED = True

    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Handle Heroku/Render/Vercel postgres:// vs postgresql:// format
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Default SQLite database
        # On Vercel / AWS Lambda, root filesystem is read-only except /tmp
        if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
            SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/blog.db'
        else:
            instance_path = BASE_DIR / 'instance'
            try:
                instance_path.mkdir(exist_ok=True)
                SQLALCHEMY_DATABASE_URI = f"sqlite:///{instance_path / 'blog.db'}"
            except OSError:
                SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/blog.db'


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}


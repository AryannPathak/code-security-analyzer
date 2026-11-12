import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration with production-grade defaults."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'smartflow-enterprise-secret-key-2026')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'smartflow-jwt-security-key-aiml')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database Configuration
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'smartflow_db')
    
    # Priority: explicit DATABASE_URL > constructed MySQL URI > SQLite local database
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Default MySQL connection using PyMySQL driver
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    
    USE_SQLITE_FALLBACK = os.getenv('USE_SQLITE_FALLBACK', 'True').lower() in ('true', '1', 'yes')
    SQLITE_DATABASE_PATH = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), '..', 'smartflow.db'
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Connection Pool settings for handling high concurrent transactions
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 1800,
        'pool_pre_ping': True
    }
    
    # CORS Configuration
    CORS_ORIGINS = [
        os.getenv('FRONTEND_URL', 'http://localhost:5173'),
        'http://localhost:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:3000'
    ]
    
    # AIML Configuration
    MODEL_CACHE_DIR = os.getenv('MODEL_CACHE_DIR', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'aiml', 'models')))
    ANOMALY_CONTAMINATION = float(os.getenv('ANOMALY_CONTAMINATION', 0.03))


class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}


class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'
    # In production, pool size can be raised for high-throughput
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'max_overflow': 40,
        'pool_recycle': 1800,
        'pool_pre_ping': True
    }


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env and .env.local if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / ".env.local")


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-secret-key-change-in-production-123456")
    
    # Database URL handling
    # Neon / Supabase / Heroku sometimes provide 'postgres://', SQLAlchemy requires 'postgresql://'
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        instance_dir = BASE_DIR / "instance"
        instance_dir.mkdir(exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{instance_dir / 'interview_system.db'}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI configuration
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    
    # Upload settings
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max upload limit
    UPLOAD_EXTENSIONS = [".pdf"]
    
    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

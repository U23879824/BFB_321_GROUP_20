import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Config:
    """Shared settings for all environments."""

    SECRET_KEY = os.getenv("SECRET_KEY")

    MYSQL_HOST = os.getenv("DB_HOST", "localhost")
    MYSQL_USER = os.getenv("DB_USER", "root")
    MYSQL_PASSWORD = os.getenv("DB_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("DB_NAME", "stocksync_db")
    MYSQL_PORT = int(os.getenv("DB_PORT", "3306"))


class DevelopmentConfig(Config):
    """Local development settings."""

    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing settings."""

    DEBUG = False
    TESTING = True
    MYSQL_DATABASE = os.getenv("TEST_DB_NAME", "stocksync_test_db")


class ProductionConfig(Config):
    """Production deployment settings."""

    DEBUG = False
    TESTING = False


configurations = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}


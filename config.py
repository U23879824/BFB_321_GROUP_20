
import os
from dotenv import load_dotenv

# Load settings from the local .env file
load_dotenv()


class Config:
    """Settings shared by all environments."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME", "stocksync_db")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    """Settings for local development."""

    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Settings for automated testing."""

    DEBUG = False
    TESTING = True


class ProductionConfig(Config):
    """Settings for deployment."""

    DEBUG = False
    TESTING = False


# Choose the configuration using APP_ENV
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}

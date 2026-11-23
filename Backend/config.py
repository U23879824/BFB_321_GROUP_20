import os
from pathlib import Path
from dotenv import load_dotenv

# Locate the main project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")


class BaseConfig:

    SECRET_KEY = os.getenv("SECRET_KEY", "stocksync-secret-key")

    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "stocksync_db")

    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):

    DEBUG = True


class TestingConfig(BaseConfig):

    TESTING = True
    DEBUG = False


class ProductionConfig(BaseConfig):

    DEBUG = False


configurations = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}
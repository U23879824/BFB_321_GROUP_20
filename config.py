<<<<<<< HEAD

import os
from dotenv import load_dotenv

# Load settings from the local .env file
=======
import os
from dotenv import load_dotenv

>>>>>>> d2a9c9b393350c6dc6f5c610817721b91cffbe09
load_dotenv()


class Config:
<<<<<<< HEAD
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
=======
    SECRET_KEY = os.getenv("SECRET_KEY", "stocksync-dev-key")

    MYSQL_HOST = os.getenv("DB_HOST", "localhost")
    MYSQL_USER = os.getenv("DB_USER", "root")
    MYSQL_PASSWORD = os.getenv("DB_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("DB_NAME", "stocksync_db")
    MYSQL_PORT = int(os.getenv("DB_PORT", "3306"))


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
>>>>>>> d2a9c9b393350c6dc6f5c610817721b91cffbe09
    TESTING = True


class ProductionConfig(Config):
<<<<<<< HEAD
    """Settings for deployment."""

    DEBUG = False
    TESTING = False


# Choose the configuration using APP_ENV
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}
=======
    DEBUG = False


configurations = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}
>>>>>>> d2a9c9b393350c6dc6f5c610817721b91cffbe09

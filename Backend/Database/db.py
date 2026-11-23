import mysql.connector
import os

from Backend.config import configurations


def get_db_connection():

    environment = os.getenv("FLASK_ENV", "development")

    config_class = configurations.get(
        environment,
        configurations["development"]
    )

    connection = mysql.connector.connect(

        host=config_class.MYSQL_HOST,

        port=config_class.MYSQL_PORT,

        user=config_class.MYSQL_USER,

        password=config_class.MYSQL_PASSWORD,

        database=config_class.MYSQL_DATABASE

    )

    return connection
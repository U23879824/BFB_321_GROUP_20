 
import pymysql
from flask import current_app, g


def connect():
    return pymysql.connect(
        host=current_app.config["DB_HOST"],
        port=current_app.config["DB_PORT"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        database=current_app.config["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )


def get_db():
    if "db" not in g:
        g.db = connect()

    return g.db


def close_db(error=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)

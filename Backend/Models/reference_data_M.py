
from Backend.Database.db import get_db


def get_all_categories():
    db = get_db()

    with db.cursor() as cursor:
        cursor.execute("""
            SELECT category_id, category_name, description
            FROM categories
            ORDER BY category_name
        """)

        return cursor.fetchall()


def get_all_stores():
    db = get_db()

    with db.cursor() as cursor:
        cursor.execute("""
            SELECT store_id, store_name, address, city,
                   latitude, longitude
            FROM stores
            ORDER BY store_name
        """)

        return cursor.fetchall()

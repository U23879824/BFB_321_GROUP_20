
from Backend.Database.db import get_db


def get_all_products(page, size, category_id=None, name=None):
    db = get_db()
    offset = (page - 1) * size

    conditions = []
    values = []

    if category_id is not None:
        conditions.append("p.category_id = %s")
        values.append(category_id)

    if name:
        conditions.append("p.product_name LIKE %s")
        values.append(f"%{name}%")

    where_clause = (
        "WHERE " + " AND ".join(conditions)
        if conditions else ""
    )

    with db.cursor() as cursor:
        cursor.execute(
            f"SELECT COUNT(*) AS total FROM products p {where_clause}",
            values
        )
        total = cursor.fetchone()["total"]

        cursor.execute(
            f"""
            SELECT p.product_id, p.product_name, p.sku,
                   p.category_id, c.category_name,
                   p.unit_price, p.description
            FROM products p
            LEFT JOIN categories c
                ON p.category_id = c.category_id
            {where_clause}
            ORDER BY p.product_id
            LIMIT %s OFFSET %s
            """,
            values + [size, offset]
        )

        records = cursor.fetchall()

    return records, total


def get_product(product_id):
    db = get_db()

    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT p.product_id, p.product_name, p.sku,
                   p.category_id, c.category_name,
                   p.unit_price, p.description
            FROM products p
            LEFT JOIN categories c
                ON p.category_id = c.category_id
            WHERE p.product_id = %s
            """,
            (product_id,)
        )

        return cursor.fetchone()


def create_product(data):
    db = get_db()

    try:
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO products
                (product_name, sku, category_id, unit_price, description)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    data["product_name"],
                    data["sku"],
                    data["category_id"],
                    data["unit_price"],
                    data.get("description")
                )
            )

            product_id = cursor.lastrowid

        db.commit()
        return product_id

    except Exception:
        db.rollback()
        raise


def update_product(product_id, data):
    db = get_db()

    allowed_fields = [
        "product_name",
        "sku",
        "category_id",
        "unit_price",
        "description"
    ]

    updates = []
    values = []

    for field in allowed_fields:
        if field in data:
            updates.append(f"{field} = %s")
            values.append(data[field])

    if not updates:
        return False

    values.append(product_id)

    try:
        with db.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE products
                SET {", ".join(updates)}
                WHERE product_id = %s
                """,
                values
            )

            updated = cursor.rowcount > 0

        db.commit()
        return updated

    except Exception:
        db.rollback()
        raise

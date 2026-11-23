
from Backend.Database.db import get_db

def get_all_inventory(page, size, store_id=None, product_id=None):
    db = get_db()
    offset = (page - 1) * size

    conditions = []
    values = []

    if store_id is not None:
        conditions.append("i.store_id = %s")
        values.append(store_id)

    if product_id is not None:
        conditions.append("i.product_id = %s")
        values.append(product_id)

    where_clause = (
        "WHERE " + " AND ".join(conditions)
        if conditions else ""
    )

    with db.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM inventory i
            {where_clause}
            """,
            values
        )
        total = cursor.fetchone()["total"]

        cursor.execute(
            f"""
            SELECT i.inventory_id, i.store_id, s.store_name,
                   i.product_id, p.product_name,
                   i.quantity_on_hand, i.reorder_level,
                   i.last_updated
            FROM inventory i
            JOIN stores s ON i.store_id = s.store_id
            JOIN products p ON i.product_id = p.product_id
            {where_clause}
            ORDER BY i.inventory_id
            LIMIT %s OFFSET %s
            """,
            values + [size, offset]
        )
        records = cursor.fetchall()

    return records, total


def get_inventory_item(inventory_id):
    db = get_db()

    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT i.inventory_id, i.store_id, s.store_name,
                   i.product_id, p.product_name,
                   i.quantity_on_hand, i.reorder_level,
                   i.last_updated
            FROM inventory i
            JOIN stores s ON i.store_id = s.store_id
            JOIN products p ON i.product_id = p.product_id
            WHERE i.inventory_id = %s
            """,
            (inventory_id,)
        )

        return cursor.fetchone()


def update_inventory(inventory_id, data):
    db = get_db()

    allowed_fields = [
        "quantity_on_hand",
        "reorder_level"
    ]

    updates = []
    values = []

    for field in allowed_fields:
        if field in data:
            updates.append(f"{field} = %s")
            values.append(data[field])

    if not updates:
        return False

    values.append(inventory_id)

    try:
        with db.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE inventory
                SET {", ".join(updates)},
                    last_updated = CURRENT_TIMESTAMP
                WHERE inventory_id = %s
                """,
                values
            )

            updated = cursor.rowcount > 0

        db.commit()
        return updated

    except Exception:
        db.rollback()
        raise


def create_stock_movement(data):
    db = get_db()

    try:
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT quantity_on_hand
                FROM inventory
                WHERE inventory_id = %s
                FOR UPDATE
                """,
                (data["inventory_id"],)
            )

            inventory = cursor.fetchone()

            if inventory is None:
                db.rollback()
                return None

            current = inventory["quantity_on_hand"]
            quantity = data["quantity"]
            movement_type = data["movement_type"]

            if movement_type == "IN":
                new_quantity = current + quantity

            elif movement_type == "OUT":
                if quantity > current:
                    raise ValueError(
                        "Insufficient stock available."
                    )

                new_quantity = current - quantity

            else:
                # ADJUSTMENT sets the new stock level.
                new_quantity = quantity

            cursor.execute(
                """
                UPDATE inventory
                SET quantity_on_hand = %s,
                    last_updated = CURRENT_TIMESTAMP
                WHERE inventory_id = %s
                """,
                (new_quantity, data["inventory_id"])
            )

            cursor.execute(
                """
                INSERT INTO stock_movements
                (inventory_id, movement_type, quantity, notes)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    data["inventory_id"],
                    movement_type,
                    quantity,
                    data.get("notes")
                )
            )

            movement_id = cursor.lastrowid

        db.commit()
        return movement_id

    except Exception:
        db.rollback()
        raise

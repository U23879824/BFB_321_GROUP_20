from flask import Blueprint, request, jsonify
from mysql.connector import Error
from db import get_db_connection
import logging

inventory_bp = Blueprint("inventory", __name__)

logger = logging.getLogger(__name__)


# GET ALL INVENTORY WITH PAGINATION AND FILTERING
@inventory_bp.route("/api/inventory", methods=["GET"])
def get_inventory():

    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=10, type=int)
    store_id = request.args.get("store_id", type=int)
    product_id = request.args.get("product_id", type=int)

    if page < 1 or size < 1 or size > 100:
        return jsonify({
            "success": False,
            "error": "Invalid pagination values."
        }), 400

    if request.args.get("store_id") and (store_id is None or store_id < 1):
        return jsonify({"success": False, "error": "Invalid store ID."}), 400

    if request.args.get("product_id") and (product_id is None or product_id < 1):
        return jsonify({"success": False, "error": "Invalid product ID."}), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT i.inventory_id, i.store_id, s.store_name,
                   i.product_id, p.product_name,
                   i.quantity_on_hand, i.reorder_level,
                   i.last_updated
            FROM inventory i
            JOIN stores s ON i.store_id = s.store_id
            JOIN products p ON i.product_id = p.product_id
            WHERE 1=1
        """

        values = []

        if store_id:
            query += " AND i.store_id = %s"
            values.append(store_id)

        if product_id:
            query += " AND i.product_id = %s"
            values.append(product_id)

        query += " ORDER BY i.inventory_id LIMIT %s OFFSET %s"

        values.extend([size, (page - 1) * size])

        cursor.execute(query, values)
        records = cursor.fetchall()

        return jsonify({
            "success": True,
            "page": page,
            "size": size,
            "data": records
        }), 200

    except Error:
        logger.exception("Error retrieving inventory")

        return jsonify({
            "success": False,
            "error": "Unable to retrieve inventory."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# GET ONE INVENTORY RECORD
@inventory_bp.route("/api/inventory/<int:inventory_id>", methods=["GET"])
def get_inventory_item(inventory_id):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM inventory
            WHERE inventory_id = %s
        """, (inventory_id,))

        record = cursor.fetchone()

        if not record:
            return jsonify({
                "success": False,
                "error": "Inventory record not found."
            }), 404

        return jsonify({
            "success": True,
            "data": record
        }), 200

    except Error:
        logger.exception("Error retrieving inventory record")

        return jsonify({
            "success": False,
            "error": "Unable to retrieve inventory record."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# UPDATE INVENTORY
@inventory_bp.route("/api/inventory/<int:inventory_id>", methods=["PATCH"])
def update_inventory(inventory_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({
            "success": False,
            "error": "A valid JSON object is required."
        }), 400

    allowed_fields = ["quantity_on_hand", "reorder_level"]

    if any(field not in allowed_fields for field in data):
        return jsonify({
            "success": False,
            "error": "Only quantity_on_hand and reorder_level can be updated."
        }), 400

    for field in data:
        value = data[field]

        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            return jsonify({
                "success": False,
                "error": f"{field} must be a non-negative integer."
            }), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT inventory_id FROM inventory WHERE inventory_id = %s",
            (inventory_id,)
        )

        if not cursor.fetchone():
            return jsonify({
                "success": False,
                "error": "Inventory record not found."
            }), 404

        fields = []
        values = []

        for field in allowed_fields:
            if field in data:
                fields.append(f"{field} = %s")
                values.append(data[field])

        values.append(inventory_id)

        query = (
            "UPDATE inventory SET "
            + ", ".join(fields)
            + " WHERE inventory_id = %s"
        )

        cursor.execute(query, values)
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Inventory updated successfully.",
            "inventory_id": inventory_id
        }), 200

    except Error:
        if connection:
            connection.rollback()

        logger.exception("Error updating inventory")

        return jsonify({
            "success": False,
            "error": "Unable to update inventory."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# RECORD STOCK MOVEMENT AND UPDATE INVENTORY
@inventory_bp.route("/api/stock-movements", methods=["POST"])
def create_stock_movement():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "A valid JSON object is required."
        }), 400

    inventory_id = data.get("inventory_id")
    movement_type = data.get("movement_type")
    quantity = data.get("quantity")
    notes = data.get("notes")

    if isinstance(inventory_id, bool) or not isinstance(inventory_id, int) or inventory_id < 1:
        return jsonify({"success": False, "error": "A valid inventory ID is required."}), 400

    if movement_type not in ["IN", "OUT", "ADJUSTMENT"]:
        return jsonify({"success": False, "error": "Movement type must be IN, OUT or ADJUSTMENT."}), 400

    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"success": False, "error": "Quantity must be a positive integer."}), 400

    if notes is not None and not isinstance(notes, str):
        return jsonify({"success": False, "error": "Notes must be text."}), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        connection.start_transaction()

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT quantity_on_hand
            FROM inventory
            WHERE inventory_id = %s
            FOR UPDATE
        """, (inventory_id,))

        inventory = cursor.fetchone()

        if not inventory:
            connection.rollback()

            return jsonify({
                "success": False,
                "error": "Inventory record not found."
            }), 404

        current_quantity = inventory["quantity_on_hand"]

        if movement_type == "IN":
            new_quantity = current_quantity + quantity

        elif movement_type == "OUT":
            new_quantity = current_quantity - quantity

        else:
            new_quantity = quantity

        if new_quantity < 0:
            connection.rollback()

            return jsonify({
                "success": False,
                "error": "Insufficient stock for this movement."
            }), 400

        cursor.execute("""
            UPDATE inventory
            SET quantity_on_hand = %s
            WHERE inventory_id = %s
        """, (new_quantity, inventory_id))

        cursor.execute("""
            INSERT INTO stock_movements
            (inventory_id, movement_type, quantity, notes)
            VALUES (%s, %s, %s, %s)
        """, (inventory_id, movement_type, quantity, notes))

        movement_id = cursor.lastrowid

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Stock movement recorded successfully.",
            "movement_id": movement_id,
            "previous_quantity": current_quantity,
            "new_quantity": new_quantity
        }), 201

    except Error:
        if connection:
            connection.rollback()

        logger.exception("Error recording stock movement")

        return jsonify({
            "success": False,
            "error": "Unable to record stock movement."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
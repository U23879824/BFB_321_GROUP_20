 from flask import Blueprint, jsonify, request
from mysql.connector import Error, IntegrityError
import logging

from Backend.Database.db import get_db_connection
from Backend.Routes.helpers import read_pagination, require_json_object


inventory_bp = Blueprint("inventory", __name__)

logger = logging.getLogger(__name__)


# 1. GET ALL INVENTORY
@inventory_bp.route("/api/inventory", methods=["GET"])
def get_inventory():

    page, size, error_response = read_pagination()

    if error_response:
        return error_response

    store_id = request.args.get("store_id")
    product_id = request.args.get("product_id")

    for field, value in [("store_id", store_id), ("product_id", product_id)]:

        if value is not None:

            try:

                if int(value) < 1:
                    raise ValueError

            except ValueError:

                return jsonify({
                    "success": False,
                    "error": f"{field} must be a positive whole number."
                }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        conditions = []
        parameters = []

        if store_id:

            conditions.append("i.store_id = %s")
            parameters.append(int(store_id))

        if product_id:

            conditions.append("i.product_id = %s")
            parameters.append(int(product_id))

        where = ""

        if conditions:

            where = " WHERE " + " AND ".join(conditions)

        cursor.execute(
            "SELECT COUNT(*) AS total FROM inventory i" + where,
            tuple(parameters)
        )

        total = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT
                i.inventory_id,
                i.store_id,
                s.store_name,
                i.product_id,
                p.product_name,
                p.sku,
                i.quantity_on_hand,
                i.reorder_level,
                i.last_updated
            FROM inventory i
            JOIN stores s ON i.store_id = s.store_id
            JOIN products p ON i.product_id = p.product_id
            """ + where + """
            ORDER BY i.inventory_id
            LIMIT %s OFFSET %s
            """,
            tuple(parameters + [size, (page - 1) * size])
        )

        records = cursor.fetchall()

        return jsonify({

            "success": True,

            "data": records,

            "pagination": {

                "page": page,

                "size": size,

                "total_records": total,

                "total_pages": (total + size - 1) // size

            }

        }), 200

    except Error:

        logger.exception("Inventory retrieval failed")

        return jsonify({
            "success": False,
            "error": "Unable to retrieve inventory."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# 2. GET ONE INVENTORY RECORD
@inventory_bp.route("/api/inventory/<int:inventory_id>", methods=["GET"])
def get_inventory_record(inventory_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM inventory
            WHERE inventory_id = %s
            """,
            (inventory_id,)
        )

        record = cursor.fetchone()

        if record is None:

            return jsonify({
                "success": False,
                "error": "Inventory record not found."
            }), 404

        return jsonify({
            "success": True,
            "data": record
        }), 200

    except Error:

        logger.exception("Inventory retrieval failed")

        return jsonify({
            "success": False,
            "error": "Unable to retrieve inventory record."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# 3. CREATE INVENTORY RECORD
@inventory_bp.route("/api/inventory", methods=["POST"])
def create_inventory():

    data, error_response = require_json_object()

    if error_response:
        return error_response

    required = [
        "store_id",
        "product_id",
        "quantity_on_hand",
        "reorder_level"
    ]

    if any(field not in data for field in required):

        return jsonify({
            "success": False,
            "error": "All inventory fields are required."
        }), 400

    for field in required:

        if type(data[field]) is not int:

            return jsonify({
                "success": False,
                "error": f"{field} must be a whole number."
            }), 400

    if data["store_id"] < 1 or data["product_id"] < 1:

        return jsonify({
            "success": False,
            "error": "Store ID and product ID must be positive."
        }), 400

    if data["quantity_on_hand"] < 0 or data["reorder_level"] < 0:

        return jsonify({
            "success": False,
            "error": "Inventory quantities cannot be negative."
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO inventory
            (
                store_id,
                product_id,
                quantity_on_hand,
                reorder_level
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                data["store_id"],
                data["product_id"],
                data["quantity_on_hand"],
                data["reorder_level"]
            )
        )

        inventory_id = cursor.lastrowid

        connection.commit()

        return jsonify({

            "success": True,

            "message": "Inventory created successfully.",

            "inventory_id": inventory_id

        }), 201

    except IntegrityError as error:

        if connection:
            connection.rollback()

        if error.errno == 1062:

            return jsonify({
                "success": False,
                "error": "Inventory already exists for this store and product."
            }), 400

        if error.errno == 1452:

            return jsonify({
                "success": False,
                "error": "The specified store or product does not exist."
            }), 400

        logger.exception("Inventory creation integrity error")

        return jsonify({
            "success": False,
            "error": "Unable to create inventory."
        }), 500

    except Error:

        if connection:
            connection.rollback()

        logger.exception("Inventory creation failed")

        return jsonify({
            "success": False,
            "error": "Unable to create inventory."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# 4. UPDATE INVENTORY
@inventory_bp.route("/api/inventory/<int:inventory_id>", methods=["PATCH"])
def update_inventory(inventory_id):

    data, error_response = require_json_object()

    if error_response:
        return error_response

    allowed = {"quantity_on_hand", "reorder_level"}

    if not data or set(data) - allowed:

        return jsonify({
            "success": False,
            "error": "Only quantity_on_hand and reorder_level can be updated."
        }), 400

    for field, value in data.items():

        if type(value) is not int or value < 0:

            return jsonify({
                "success": False,
                "error": f"{field} must be a non-negative whole number."
            }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        updates = []
        values = []

        for field in data:

            updates.append(f"{field} = %s")
            values.append(data[field])

        values.append(inventory_id)

        cursor.execute(
            "UPDATE inventory SET " + ", ".join(updates)
            + " WHERE inventory_id = %s",
            tuple(values)
        )

        if cursor.rowcount == 0:

            cursor.execute(
                "SELECT inventory_id FROM inventory WHERE inventory_id = %s",
                (inventory_id,)
            )

            if cursor.fetchone() is None:

                return jsonify({
                    "success": False,
                    "error": "Inventory record not found."
                }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Inventory updated successfully."
        }), 200

    except Error:

        if connection:
            connection.rollback()

        logger.exception("Inventory update failed")

        return jsonify({
            "success": False,
            "error": "Unable to update inventory."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# 5. RECORD STOCK MOVEMENT
@inventory_bp.route("/api/stock-movements", methods=["POST"])
def create_stock_movement():

    data, error_response = require_json_object()

    if error_response:
        return error_response

    inventory_id = data.get("inventory_id")
    movement_type = data.get("movement_type")
    quantity = data.get("quantity")
    notes = data.get("notes")

    if type(inventory_id) is not int or inventory_id < 1:

        return jsonify({
            "success": False,
            "error": "A valid inventory ID is required."
        }), 400

    if movement_type not in ["IN", "OUT", "ADJUSTMENT"]:

        return jsonify({
            "success": False,
            "error": "Movement type must be IN, OUT or ADJUSTMENT."
        }), 400

    if type(quantity) is not int or quantity <= 0:

        return jsonify({
            "success": False,
            "error": "Quantity must be a positive whole number."
        }), 400

    if notes is not None and (not isinstance(notes, str) or len(notes) > 255):

        return jsonify({
            "success": False,
            "error": "Notes must be text of at most 255 characters."
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        connection.start_transaction()

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT quantity_on_hand
            FROM inventory
            WHERE inventory_id = %s
            FOR UPDATE
            """,
            (inventory_id,)
        )

        record = cursor.fetchone()

        if record is None:

            connection.rollback()

            return jsonify({
                "success": False,
                "error": "Inventory record not found."
            }), 404

        old_quantity = record["quantity_on_hand"]

        if movement_type == "IN":

            new_quantity = old_quantity + quantity

        elif movement_type == "OUT":

            new_quantity = old_quantity - quantity

        else:

            new_quantity = quantity

        if new_quantity < 0:

            connection.rollback()

            return jsonify({
                "success": False,
                "error": "Insufficient stock."
            }), 400

        cursor.execute(
            """
            UPDATE inventory
            SET quantity_on_hand = %s
            WHERE inventory_id = %s
            """,
            (new_quantity, inventory_id)
        )

        cursor.execute(
            """
            INSERT INTO stock_movements
            (
                inventory_id,
                movement_type,
                quantity,
                notes
            )
            VALUES (%s, %s, %s, %s)
            """,
            (inventory_id, movement_type, quantity, notes)
        )

        movement_id = cursor.lastrowid

        connection.commit()

        return jsonify({

            "success": True,

            "message": "Stock movement recorded successfully.",

            "data": {

                "movement_id": movement_id,

                "previous_quantity": old_quantity,

                "new_quantity": new_quantity

            }

        }), 201

    except Error:

        if connection:
            connection.rollback()

        logger.exception("Stock movement failed")

        return jsonify({
            "success": False,
            "error": "Unable to record stock movement."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
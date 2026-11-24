 
from flask import Blueprint, request, jsonify
import logging
import pymysql

from Backend.Models import inventory_M as inventory_model

inventory_bp = Blueprint("inventory", __name__)
logger = logging.getLogger(__name__)


@inventory_bp.route("/api/inventory", methods=["GET"])
def list_inventory():
    try:
        try:
            page = int(request.args.get("page", "1"))
            size = int(request.args.get("size", "10"))
        except ValueError:
            return jsonify({
                "error": "page and size must be integers."
            }), 400

        if page < 1 or size < 1 or size > 100:
            return jsonify({
                "error": "page must be at least 1 and size must be between 1 and 100."
            }), 400

        store_id = request.args.get("store_id")
        product_id = request.args.get("product_id")

        try:
            if store_id is not None:
                store_id = int(store_id)
                if store_id <= 0:
                    raise ValueError

            if product_id is not None:
                product_id = int(product_id)
                if product_id <= 0:
                    raise ValueError

        except ValueError:
            return jsonify({
                "error": "store_id and product_id must be positive integers."
            }), 400

        records, total = inventory_model.get_all_inventory(
            page, size, store_id, product_id
        )

        return jsonify({
            "data": records,
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size
            }
        }), 200

    except Exception:
        logger.exception("Could not retrieve inventory")
        return jsonify({"error": "Could not retrieve inventory."}), 500


@inventory_bp.route("/api/inventory/<int:inventory_id>", methods=["GET"])
def get_inventory(inventory_id):
    try:
        record = inventory_model.get_inventory_item(inventory_id)

        if record is None:
            return jsonify({
                "error": "Inventory record not found."
            }), 404

        return jsonify({"data": record}), 200

    except Exception:
        logger.exception("Could not retrieve inventory record")
        return jsonify({"error": "Could not retrieve inventory record."}), 500


@inventory_bp.route("/api/inventory/<int:inventory_id>", methods=["PATCH"])
def edit_inventory(inventory_id):
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({
            "error": "A non-empty JSON object is required."
        }), 400

    for field, value in data.items():
        if field not in ["quantity_on_hand", "reorder_level"]:
            return jsonify({
                "error": f"Invalid field: {field}"
            }), 400

        if type(value) is not int or value < 0:
            return jsonify({
                "error": f"{field} must be a non-negative integer."
            }), 400

    try:
        existing = inventory_model.get_inventory_item(inventory_id)

        if existing is None:
            return jsonify({
                "error": "Inventory record not found."
            }), 404

        inventory_model.update_inventory(inventory_id, data)

        return jsonify({
            "message": "Inventory updated successfully."
        }), 200

    except Exception:
        logger.exception("Could not update inventory")
        return jsonify({"error": "Could not update inventory."}), 500


@inventory_bp.route("/api/stock-movements", methods=["POST"])
def add_stock_movement():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    required = ["inventory_id", "movement_type", "quantity"]

    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} is required."}), 400

    if type(data["inventory_id"]) is not int or data["inventory_id"] <= 0:
        return jsonify({
            "error": "inventory_id must be a positive integer."
        }), 400

    if data["movement_type"] not in ["IN", "OUT", "ADJUSTMENT"]:
        return jsonify({
            "error": "movement_type must be IN, OUT or ADJUSTMENT."
        }), 400

    if type(data["quantity"]) is not int or data["quantity"] <= 0:
        return jsonify({
            "error": "quantity must be a positive integer."
        }), 400

    if "notes" in data and data["notes"] is not None:
        if not isinstance(data["notes"], str):
            return jsonify({"error": "notes must be a string."}), 400

    try:
        movement_id = inventory_model.create_stock_movement(data)

        if movement_id is None:
            return jsonify({
                "error": "Inventory record not found."
            }), 404

        return jsonify({
            "message": "Stock movement recorded successfully.",
            "movement_id": movement_id
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except pymysql.MySQLError:
        logger.exception("Database error while recording stock movement")
        return jsonify({
            "error": "Could not record stock movement."
        }), 500

    except Exception:
        logger.exception("Could not record stock movement")
        return jsonify({
            "error": "Could not record stock movement."
        }), 500

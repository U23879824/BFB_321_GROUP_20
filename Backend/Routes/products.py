 
from flask import Blueprint, request, jsonify
from decimal import Decimal, InvalidOperation
import logging
import pymysql

from Backend.Models import products as product_model

products_bp = Blueprint("products", __name__)
logger = logging.getLogger(__name__)


def validate_product(data, partial=False):
    if not isinstance(data, dict):
        return "Request body must be a JSON object."

    required = ["product_name", "sku", "category_id", "unit_price"]
    allowed_fields = [
        "product_name",
        "sku",
        "category_id",
        "unit_price",
        "description"
    ]

    for field in data:
        if field not in allowed_fields:
            return f"Invalid field: {field}"

    if not partial:
        for field in required:
            if field not in data:
                return f"{field} is required."

    if "product_name" in data:
        if not isinstance(data["product_name"], str) or not data["product_name"].strip():
            return "product_name must be a non-empty string."

    if "sku" in data:
        if not isinstance(data["sku"], str) or not data["sku"].strip():
            return "sku must be a non-empty string."

    if "category_id" in data:
        if type(data["category_id"]) is not int or data["category_id"] <= 0:
            return "category_id must be a positive integer."

    if "unit_price" in data:
        try:
            price = Decimal(str(data["unit_price"]))

            if not price.is_finite() or price < 0:
                return "unit_price must be a non-negative number."

        except (InvalidOperation, ValueError):
            return "unit_price must be a valid number."

    if "description" in data:
        if data["description"] is not None and not isinstance(data["description"], str):
            return "description must be a string."

    return None


def handle_database_error(error):
    code = error.args[0] if error.args else None

    if code == 1062:
        return jsonify({
            "error": "A product with this SKU already exists."
        }), 409

    if code == 1452:
        return jsonify({
            "error": "The selected category does not exist."
        }), 400

    logger.exception("Product database error")
    return jsonify({"error": "A database error occurred."}), 500


@products_bp.route("/api/products", methods=["GET"])
def list_products():
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

        category_id = request.args.get("category_id")

        if category_id is not None:
            try:
                category_id = int(category_id)
                if category_id <= 0:
                    raise ValueError
            except ValueError:
                return jsonify({
                    "error": "category_id must be a positive integer."
                }), 400

        name = request.args.get("name")

        records, total = product_model.get_all_products(
            page, size, category_id, name
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
        logger.exception("Could not retrieve products")
        return jsonify({"error": "Could not retrieve products."}), 500


@products_bp.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    try:
        product = product_model.get_product(product_id)

        if product is None:
            return jsonify({"error": "Product not found."}), 404

        return jsonify({"data": product}), 200

    except Exception:
        logger.exception("Could not retrieve product")
        return jsonify({"error": "Could not retrieve product."}), 500


@products_bp.route("/api/products", methods=["POST"])
def add_product():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 400

    data = request.get_json(silent=True)
    error = validate_product(data)

    if error:
        return jsonify({"error": error}), 400

    try:
        product_id = product_model.create_product(data)

        return jsonify({
            "message": "Product created successfully.",
            "product_id": product_id
        }), 201

    except pymysql.MySQLError as error:
        return handle_database_error(error)

    except Exception:
        logger.exception("Could not create product")
        return jsonify({"error": "Could not create product."}), 500


@products_bp.route("/api/products/<int:product_id>", methods=["PUT"])
def replace_product(product_id):
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 400

    data = request.get_json(silent=True)
    error = validate_product(data)

    if error:
        return jsonify({"error": error}), 400

    try:
        existing = product_model.get_product(product_id)

        if existing is None:
            return jsonify({"error": "Product not found."}), 404

        product_model.update_product(product_id, data)

        return jsonify({
            "message": "Product updated successfully.",
            "product_id": product_id
        }), 200

    except pymysql.MySQLError as error:
        return handle_database_error(error)

    except Exception:
        logger.exception("Could not update product")
        return jsonify({"error": "Could not update product."}), 500


@products_bp.route("/api/products/<int:product_id>", methods=["PATCH"])
def patch_product(product_id):
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 400

    data = request.get_json(silent=True)
    error = validate_product(data, partial=True)

    if error:
        return jsonify({"error": error}), 400

    if not data:
        return jsonify({
            "error": "At least one field must be provided."
        }), 400

    try:
        existing = product_model.get_product(product_id)

        if existing is None:
            return jsonify({"error": "Product not found."}), 404

        product_model.update_product(product_id, data)

        return jsonify({
            "message": "Product updated successfully.",
            "product_id": product_id
        }), 200

    except pymysql.MySQLError as error:
        return handle_database_error(error)

    except Exception:
        logger.exception("Could not update product")
        return jsonify({"error": "Could not update product."}), 500

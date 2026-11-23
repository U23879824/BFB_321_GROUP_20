from flask import Blueprint, request, jsonify
from mysql.connector import IntegrityError, Error
from db import get_db_connection
import logging

products_bp = Blueprint("products", __name__)

logger = logging.getLogger(__name__)


# GET ALL PRODUCTS WITH PAGINATION AND FILTERING
@products_bp.route("/api/products", methods=["GET"])
def get_products():

    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=10, type=int)
    category = request.args.get("category")
    name = request.args.get("name")

    if page < 1 or size < 1 or size > 100:
        return jsonify({
            "success": False,
            "error": "Page must be at least 1 and size must be between 1 and 100."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT p.product_id, p.product_name, p.sku,
                   p.category_id, c.category_name,
                   p.unit_price, p.description
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            WHERE 1=1
        """

        values = []

        if category:
            query += " AND c.category_name = %s"
            values.append(category)

        if name:
            query += " AND p.product_name LIKE %s"
            values.append(f"%{name}%")

        query += " ORDER BY p.product_id LIMIT %s OFFSET %s"

        values.extend([size, (page - 1) * size])

        cursor.execute(query, values)
        products = cursor.fetchall()

        return jsonify({
            "success": True,
            "page": page,
            "size": size,
            "data": products
        }), 200

    except Error:
        logger.exception("Error retrieving products")
        return jsonify({
            "success": False,
            "error": "Unable to retrieve products."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# GET ONE PRODUCT
@products_bp.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM products
            WHERE product_id = %s
        """, (product_id,))

        product = cursor.fetchone()

        if not product:
            return jsonify({
                "success": False,
                "error": "Product not found."
            }), 404

        return jsonify({
            "success": True,
            "data": product
        }), 200

    except Error:
        logger.exception("Error retrieving product")
        return jsonify({
            "success": False,
            "error": "Unable to retrieve product."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# CREATE PRODUCT
@products_bp.route("/api/products", methods=["POST"])
def create_product():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "A valid JSON object is required."
        }), 400

    required_fields = [
        "product_name",
        "sku",
        "category_id",
        "unit_price"
    ]

    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            return jsonify({
                "success": False,
                "error": f"{field} is required."
            }), 400

    if not isinstance(data["product_name"], str) or not data["product_name"].strip():
        return jsonify({
            "success": False,
            "error": "Product name must be valid text."
        }), 400

    if not isinstance(data["sku"], str) or not data["sku"].strip():
        return jsonify({
            "success": False,
            "error": "SKU must be valid text."
        }), 400

    if isinstance(data["category_id"], bool) or not isinstance(data["category_id"], int) or data["category_id"] < 1:
        return jsonify({
            "success": False,
            "error": "Category ID must be a positive integer."
        }), 400

    try:
        price = float(data["unit_price"])

        if price < 0:
            raise ValueError

    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "error": "Unit price must be a valid non-negative number."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            INSERT INTO products
            (product_name, sku, category_id, unit_price, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data["product_name"].strip(),
            data["sku"].strip(),
            data["category_id"],
            price,
            data.get("description")
        ))

        product_id = cursor.lastrowid
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Product created successfully.",
            "product_id": product_id
        }), 201

    except IntegrityError as error:
        if connection:
            connection.rollback()

        if error.errno == 1062:
            return jsonify({
                "success": False,
                "error": "This SKU already exists."
            }), 400

        if error.errno == 1452:
            return jsonify({
                "success": False,
                "error": "The selected category does not exist."
            }), 400

        logger.exception("Product creation integrity error")
        return jsonify({
            "success": False,
            "error": "Unable to create product."
        }), 500

    except Error:
        if connection:
            connection.rollback()

        logger.exception("Error creating product")

        return jsonify({
            "success": False,
            "error": "Unable to create product."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# UPDATE PRODUCT
@products_bp.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "A valid JSON object is required."
        }), 400

    allowed_fields = [
        "product_name",
        "sku",
        "category_id",
        "unit_price",
        "description"
    ]

    if not data or any(field not in allowed_fields for field in data):
        return jsonify({
            "success": False,
            "error": "Provide at least one valid product field."
        }), 400

    if "product_name" in data:
        if not isinstance(data["product_name"], str) or not data["product_name"].strip():
            return jsonify({"success": False, "error": "Invalid product name."}), 400

    if "sku" in data:
        if not isinstance(data["sku"], str) or not data["sku"].strip():
            return jsonify({"success": False, "error": "Invalid SKU."}), 400

    if "category_id" in data:
        if isinstance(data["category_id"], bool) or not isinstance(data["category_id"], int) or data["category_id"] < 1:
            return jsonify({"success": False, "error": "Invalid category ID."}), 400

    if "unit_price" in data:
        try:
            price = float(data["unit_price"])
            if price < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid unit price."}), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT product_id FROM products WHERE product_id = %s",
            (product_id,)
        )

        if not cursor.fetchone():
            return jsonify({
                "success": False,
                "error": "Product not found."
            }), 404

        fields = []
        values = []

        for field in allowed_fields:
            if field in data:
                value = data[field]

                if field in ("product_name", "sku") and isinstance(value, str):
                    value = value.strip()

                fields.append(f"{field} = %s")
                values.append(value)

        values.append(product_id)

        query = (
            "UPDATE products SET "
            + ", ".join(fields)
            + " WHERE product_id = %s"
        )

        cursor.execute(query, values)
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Product updated successfully.",
            "product_id": product_id
        }), 200

    except IntegrityError as error:
        if connection:
            connection.rollback()

        if error.errno == 1062:
            return jsonify({
                "success": False,
                "error": "The SKU already belongs to another product."
            }), 400

        if error.errno == 1452:
            return jsonify({
                "success": False,
                "error": "The selected category does not exist."
            }), 400

        logger.exception("Product update integrity error")
        return jsonify({
            "success": False,
            "error": "Unable to update product."
        }), 500

    except Error:
        if connection:
            connection.rollback()

        logger.exception("Error updating product")

        return jsonify({
            "success": False,
            "error": "Unable to update product."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
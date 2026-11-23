from flask import Blueprint, jsonify, request
from mysql.connector import Error, IntegrityError
from decimal import Decimal, InvalidOperation
import logging

from Backend.Database.db import get_db_connection
from Backend.Routes.helpers import read_pagination, require_json_object


products_bp = Blueprint("products", __name__)

logger = logging.getLogger(__name__)


def validate_product(data, partial=False):

    allowed_fields = {
        "product_name",
        "sku",
        "category_id",
        "unit_price",
        "description"
    }

    required_fields = {
        "product_name",
        "sku",
        "category_id",
        "unit_price"
    }

    if not data:

        return "At least one product field is required."

    if set(data) - allowed_fields:

        return "Unknown product field supplied."

    if not partial:

        missing = required_fields - set(data)

        if missing:

            return "Missing required fields: " + ", ".join(missing)

    if "product_name" in data:

        if not isinstance(data["product_name"], str) or not data["product_name"].strip() or len(data["product_name"]) > 150:

            return "Invalid product name."

    if "sku" in data:

        if not isinstance(data["sku"], str) or not data["sku"].strip() or len(data["sku"]) > 50:

            return "Invalid SKU."

    if "category_id" in data:

        if type(data["category_id"]) is not int or data["category_id"] < 1:

            return "Category ID must be a positive whole number."

    if "unit_price" in data:

        try:

            price = Decimal(str(data["unit_price"]))

            if not price.is_finite() or price < 0:

                return "Unit price must be a non-negative number."

            if price.as_tuple().exponent < -2:

                return "Unit price cannot have more than two decimal places."

        except (InvalidOperation, ValueError, TypeError):

            return "Unit price must be a valid number."

    if "description" in data and data["description"] is not None:

        if not isinstance(data["description"], str) or len(data["description"]) > 255:

            return "Invalid description."

    return None


# 1. GET ALL PRODUCTS
@products_bp.route("/api/products", methods=["GET"])
def get_products():

    page, size, error_response = read_pagination()

    if error_response:
        return error_response

    category = request.args.get("category")
    name = request.args.get("name")

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        conditions = []
        parameters = []

        if category:

            conditions.append("c.category_name = %s")
            parameters.append(category.strip())

        if name:

            conditions.append("p.product_name LIKE %s")
            parameters.append("%" + name.strip() + "%")

        where = ""

        if conditions:

            where = " WHERE " + " AND ".join(conditions)

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM products p
            JOIN categories c
            ON p.category_id = c.category_id
            """ + where,
            tuple(parameters)
        )

        total = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT
                p.product_id,
                p.product_name,
                p.sku,
                p.category_id,
                c.category_name,
                p.unit_price,
                p.description
            FROM products p
            JOIN categories c
            ON p.category_id = c.category_id
            """ + where + """
            ORDER BY p.product_id
            LIMIT %s OFFSET %s
            """,
            tuple(parameters + [size, (page - 1) * size])
        )

        products = cursor.fetchall()

        return jsonify({

            "success": True,

            "data": products,

            "pagination": {

                "page": page,

                "size": size,

                "total_records": total,

                "total_pages": (total + size - 1) // size

            }

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


# 2. GET ONE PRODUCT
@products_bp.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM products
            WHERE product_id = %s
            """,
            (product_id,)
        )

        product = cursor.fetchone()

        if product is None:

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


# 3. CREATE PRODUCT
@products_bp.route("/api/products", methods=["POST"])
def create_product():

    data, error_response = require_json_object()

    if error_response:
        return error_response

    validation_error = validate_product(data)

    if validation_error:

        return jsonify({
            "success": False,
            "error": validation_error
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO products
            (
                product_name,
                sku,
                category_id,
                unit_price,
                description
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                data["product_name"].strip(),
                data["sku"].strip(),
                data["category_id"],
                str(Decimal(str(data["unit_price"]))),
                data.get("description")
            )
        )

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

        logger.exception("Product creation failed")

        return jsonify({
            "success": False,
            "error": "Unable to create product."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# 4. UPDATE COMPLETE PRODUCT USING PUT
@products_bp.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):

    data, error_response = require_json_object()

    if error_response:
        return error_response

    validation_error = validate_product(data)

    if validation_error:

        return jsonify({
            "success": False,
            "error": validation_error
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE products
            SET
                product_name = %s,
                sku = %s,
                category_id = %s,
                unit_price = %s,
                description = %s
            WHERE product_id = %s
            """,
            (
                data["product_name"].strip(),
                data["sku"].strip(),
                data["category_id"],
                str(Decimal(str(data["unit_price"]))),
                data.get("description"),
                product_id
            )
        )

        if cursor.rowcount == 0:

            cursor.execute(
                "SELECT product_id FROM products WHERE product_id = %s",
                (product_id,)
            )

            if cursor.fetchone() is None:

                return jsonify({
                    "success": False,
                    "error": "Product not found."
                }), 404

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
                "error": "This SKU already exists."
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

        logger.exception("Product update failed")

        return jsonify({
            "success": False,
            "error": "Unable to update product."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# 5. PARTIAL PRODUCT UPDATE USING PATCH
@products_bp.route("/api/products/<int:product_id>", methods=["PATCH"])
def patch_product(product_id):

    data, error_response = require_json_object()

    if error_response:
        return error_response

    validation_error = validate_product(data, partial=True)

    if validation_error:

        return jsonify({
            "success": False,
            "error": validation_error
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

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

                value = data[field]

                if field in ("product_name", "sku"):
                    value = value.strip()

                if field == "unit_price":
                    value = str(Decimal(str(value)))

                values.append(value)

        values.append(product_id)

        cursor.execute(
            "UPDATE products SET " + ", ".join(updates)
            + " WHERE product_id = %s",
            tuple(values)
        )

        if cursor.rowcount == 0:

            cursor.execute(
                "SELECT product_id FROM products WHERE product_id = %s",
                (product_id,)
            )

            if cursor.fetchone() is None:

                return jsonify({
                    "success": False,
                    "error": "Product not found."
                }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Product partially updated successfully."
        }), 200

    except IntegrityError as error:

        if connection:
            connection.rollback()

        if error.errno == 1062:

            return jsonify({
                "success": False,
                "error": "This SKU already exists."
            }), 400

        logger.exception("Product patch integrity error")

        return jsonify({
            "success": False,
            "error": "Unable to update product."
        }), 500

    except Error:

        if connection:
            connection.rollback()

        logger.exception("Product patch failed")

        return jsonify({
            "success": False,
            "error": "Unable to update product."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
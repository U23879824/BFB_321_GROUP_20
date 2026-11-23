from flask import Blueprint, jsonify
from mysql.connector import Error
import logging

from Backend.Database.db import get_db_connection


reference_bp = Blueprint("reference", __name__)

logger = logging.getLogger(__name__)


# GET ALL CATEGORIES
@reference_bp.route("/api/categories", methods=["GET"])
def get_categories():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                category_id,
                category_name,
                description
            FROM categories
            ORDER BY category_name
            """
        )

        categories = cursor.fetchall()

        return jsonify({
            "success": True,
            "data": categories
        }), 200

    except Error:

        logger.exception("Category retrieval failed")

        return jsonify({
            "success": False,
            "error": "Unable to retrieve categories."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# GET ALL STORES
@reference_bp.route("/api/stores", methods=["GET"])
def get_stores():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                store_id,
                store_name,
                address,
                city,
                latitude,
                longitude
            FROM stores
            ORDER BY store_name
            """
        )

        stores = cursor.fetchall()

        return jsonify({
            "success": True,
            "data": stores
        }), 200

    except Error:

        logger.exception("Store retrieval failed")

        return jsonify({
            "success": False,
            "error": "Unable to retrieve stores."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
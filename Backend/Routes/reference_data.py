 
from flask import Blueprint, jsonify
import logging

from Backend.Models import reference_data_M as reference_model

reference_bp = Blueprint("reference", __name__)
logger = logging.getLogger(__name__)


@reference_bp.route("/api/categories", methods=["GET"])
def get_categories():
    try:
        categories = reference_model.get_all_categories()
        return jsonify({"data": categories}), 200

    except Exception:
        logger.exception("Could not retrieve categories")
        return jsonify({"error": "Could not retrieve categories."}), 500


@reference_bp.route("/api/stores", methods=["GET"])
def get_stores():
    try:
        stores = reference_model.get_all_stores()
        return jsonify({"data": stores}), 200

    except Exception:
        logger.exception("Could not retrieve stores")
        return jsonify({"error": "Could not retrieve stores."}), 500

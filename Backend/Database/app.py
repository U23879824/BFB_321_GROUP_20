
import logging
import os
from pathlib import Path

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from Backend.config import configurations
from Backend.Database import db

from Backend.Routes.products import products_bp
from Backend.Routes.inventory import inventory_bp
from Backend.Routes.reference_data import reference_bp


def create_app():S
    app = Flask(__name__)

    environment = os.getenv("FLASK_ENV", "development")
    config_class = configurations.get(
        environment,
        configurations["development"]
    )

    app.config.from_object(config_class)

    log_file = Path(__file__).resolve().parent / "stocksync.log"

    logging.basicConfig(
        filename=str(log_file),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )

    db.init_app(app)

    app.register_blueprint(products_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(reference_bp)

    @app.route("/")
    def home():
        return jsonify({
            "message": "Welcome to Stock Sync API",
            "status": "running"
        }), 200

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy"
        }), 200

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({
            "error": error.name,
            "message": error.description
        }), error.code

    @app.errorhandler(Exception)
    def handle_server_error(error):
        app.logger.exception("Unexpected application error")

        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred."
        }), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])

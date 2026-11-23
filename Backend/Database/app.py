import logging
from pathlib import Path

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from Backend.config import configurations

from Backend.Routes.products import products_bp
from Backend.Routes.inventory import inventory_bp
from Backend.Routes.reference_data import reference_bp


def create_app():

    app = Flask(__name__)

    import os

    environment = os.getenv("FLASK_ENV", "development")

    config_class = configurations.get(
        environment,
        configurations["development"]
    )

    app.config.from_object(config_class)

    # Configure logging
    log_file = Path(__file__).resolve().parent / "stocksync.log"

    logging.basicConfig(

        level=logging.INFO,

        format="%(asctime)s %(levelname)s %(name)s: %(message)s",

        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]

    )

    # Register blueprints
    app.register_blueprint(products_bp)

    app.register_blueprint(inventory_bp)

    app.register_blueprint(reference_bp)

    # Home route
    @app.route("/", methods=["GET"])
    def home():

        return jsonify({

            "success": True,

            "message": "StockSync REST API is running."

        }), 200

    # Health check
    @app.route("/api/health", methods=["GET"])
    def health():

        return jsonify({

            "success": True,

            "status": "healthy"

        }), 200

    # 400 error handler
    @app.errorhandler(400)
    def bad_request(error):

        return jsonify({

            "success": False,

            "error": "Invalid request.",

            "status_code": 400

        }), 400

    # 404 error handler
    @app.errorhandler(404)
    def not_found(error):

        return jsonify({

            "success": False,

            "error": "Requested resource not found.",

            "status_code": 404

        }), 404

    # Other HTTP errors
    @app.errorhandler(HTTPException)
    def handle_http_error(error):

        return jsonify({

            "success": False,

            "error": error.description,

            "status_code": error.code

        }), error.code

    # 500 error handler
    @app.errorhandler(Exception)
    def handle_server_error(error):

        app.logger.exception("Unexpected application error")

        return jsonify({

            "success": False,

            "error": "An unexpected server error occurred.",

            "status_code": 500

        }), 500

    return app


app = create_app()


if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=app.config["DEBUG"]

    )
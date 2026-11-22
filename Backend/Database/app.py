from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from config import configurations
from Routes.products import products_bp
from Routes.inventory import inventory_bp
import logging
import os


def create_app():

    app = Flask(__name__)

    environment = os.getenv("FLASK_ENV", "development")

    app.config.from_object(
        configurations.get(environment, configurations["development"])
    )

    # Configure application logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("stocksync.log"),
            logging.StreamHandler()
        ]
    )

    # Register API Blueprints
    app.register_blueprint(products_bp)
    app.register_blueprint(inventory_bp)

    # Home route
    @app.route("/")
    def home():
        return jsonify({
            "success": True,
            "message": "Welcome to the StockSync REST API."
        }), 200

    # Handle HTTP errors centrally
    @app.errorhandler(HTTPException)
    def handle_http_error(error):

        return jsonify({
            "success": False,
            "error": error.description,
            "status_code": error.code
        }), error.code

    # Handle unexpected server errors
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
    app.run(debug=app.config["DEBUG"])
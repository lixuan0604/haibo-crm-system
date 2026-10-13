import logging

from flask import Flask, request
from flask_cors import CORS

from haibo.controllers import register_controllers


def create_app():
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    register_controllers(app)

    @app.after_request
    def no_cache(response):
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    return app

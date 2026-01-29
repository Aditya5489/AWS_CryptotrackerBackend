from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import jwt

from routes.auth_routes import auth_bp
from routes.coin_routes import coin_bp
from routes.watchlist_routes import watchlist_bp
from routes.alert_routes import alert_bp
from routes.admin_routes import admin_bp

import boto3
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(
        app,
        origins=["http://localhost:5173"],
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "Accept"],
        supports_credentials=True
    )

    jwt.init_app(app)

   
    app.dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-east-1"
    )

   

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(coin_bp, url_prefix="/api")
    app.register_blueprint(watchlist_bp, url_prefix="/api")
    app.register_blueprint(alert_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

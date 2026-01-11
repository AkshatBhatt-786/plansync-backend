from flask import Flask
from flask_cors import CORS
from .config import config

# Author: @AkshatBhatt-786
def create_app(config_name: str = "default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    CORS(app)

    # Register blueprints
    from .routes.auth import auth_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth/accounts')

    return app

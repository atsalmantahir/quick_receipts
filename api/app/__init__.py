from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os

# Extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_object='app.config.Config'):
    app = Flask(__name__)
    # Enable CORS for all routes
    CORS(app)

    app.config.from_object(config_object)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)


    # Configure file upload settings
    app.config['UPLOAD_FOLDER'] = 'uploads/receipts'  # Folder to save uploaded files
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}  # Allowed file extensions

    # Create the upload folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Initialize API
    api = Api(app, doc='/swagger/')

    # Define the common API prefix
    api_prefix = '/api'

    # Register Blueprints
    from .controllers.auth_controller import api as auth_api
    from .controllers.users_controller import api as users_api
    from .controllers.roles_controller import api as roles_api
    from .controllers.receipts_controller import api as receipts_api

    # Add namespaces with the '/api' prefix
    api.add_namespace(auth_api, path=f'{api_prefix}/auth')
    api.add_namespace(users_api, path=f'{api_prefix}/users')
    api.add_namespace(roles_api, path=f'{api_prefix}/roles')
    api.add_namespace(receipts_api, path=f'{api_prefix}/receipts')

    return app
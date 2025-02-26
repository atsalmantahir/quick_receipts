from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_object='app.config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_object)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Initialize API
    api = Api(app, doc='/swagger/')

    # Define the common API prefix
    api_prefix = '/api'

    # Register Blueprints
    from .controllers.users_controller import api as users_api
    from .controllers.roles_controller import api as roles_api
    from .controllers.receipts_controller import api as receipts_api

    # Add namespaces with the '/api' prefix
    api.add_namespace(users_api, path=f'{api_prefix}/users')
    api.add_namespace(roles_api, path=f'{api_prefix}/roles')
    api.add_namespace(receipts_api, path=f'{api_prefix}/receipts')  # Fixed typo

    return app
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

    # Register Blueprints
    from .controllers.auth_controller import api as auth_api
    from .controllers.user_controller import api as user_api

    app.register_blueprint(auth_api, url_prefix='/auth')
    app.register_blueprint(user_api, url_prefix='/users')

    return app

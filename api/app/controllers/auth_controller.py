from flask import Blueprint, request
from flask_restx import Api, Resource, fields
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from app.models import User
from app import db

# Initialize Blueprint and API
api = Blueprint('auth', __name__)
auth_ns = Api(api, doc='/swagger/')

# Define Login Model for Swagger documentation
login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

# AuthController for handling login functionality
class AuthController(Resource):
    @auth_ns.expect(login_model)  # Expecting the login model input
    def post(self):
        data = request.get_json()  # Get JSON data from the request
        user = User.query.filter_by(email=data['email']).first()  # Check if user exists
        if user and check_password_hash(user.password_hash, data['password']):
            # Generate JWT token on successful login
            token = create_access_token(identity=user.user_id)
            return {'access_token': token}, 200
        return {'message': 'Invalid credentials'}, 401

# Add the AuthController as a resource under the /login endpoint
auth_ns.add_resource(AuthController, '/login')

# In your app's main initialization code, register the Blueprint:
# app.register_blueprint(api, url_prefix='/auth')  # Register blueprint under /auth

from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.models import User
from app import db

# Initialize Blueprint and API
api = Namespace('auth', description="Auth operations")

# Define Login Model for Swagger documentation
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

# Define Register Model for Swagger documentation
register_model = api.model('Register', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

# LoginController for handling login functionality
@api.route('/login')
class LoginController(Resource):
    @api.expect(login_model)  # Expecting the login model input
    def post(self):
        """
        Authenticate a user and return a JWT token.
        """
        data = request.get_json()  # Get JSON data from the request
        user = User.query.filter_by(email=data['email']).first()  # Check if user exists

        # Validate user credentials
        if user and check_password_hash(user.password_hash, data['password']):
            # Generate JWT token on successful login
            token = create_access_token(identity=user.user_id)
            return {'access_token': token}, 200
        return {'message': 'Invalid credentials'}, 401

# RegisterController for handling registration functionality
@api.route('/register')
class RegisterController(Resource):
    @api.expect(register_model)  # Expecting the register model input
    def post(self):
        """
        Register a new user.
        """
        data = request.get_json()  # Get JSON data from the request

        # Check if the user already exists
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'User already exists'}, 400

        try:
            # Hash the password before saving it to the database
            hashed_password = generate_password_hash(data['password'])

            # Create a new user
            new_user = User(
                email=data['email'],
                password_hash=hashed_password
            )

            # Save the new user to the database
            db.session.add(new_user)
            db.session.commit()

            return {'message': 'User registered successfully', 'user_id': new_user.user_id}, 201

        except Exception as e:
            db.session.rollback()
            return {'message': f'Error registering user: {str(e)}'}, 500
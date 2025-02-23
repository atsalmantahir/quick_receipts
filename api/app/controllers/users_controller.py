from flask_restx import Namespace, Resource, fields
from flask import request
from app.models import User, Role
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.audit_log_helper import log_api_action, log_audit 

api = Namespace('users', description="Users operations")

# Updated user model with role_id
user_model = api.model('User', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'role_id': fields.Integer(required=True, description='ID of the role assigned to the user')
})

user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'password': fields.String(description='Password'),
    'role_id': fields.Integer(description='Role ID')
})

@api.route('/')
class UserController(Resource):
    @log_api_action('create')  # Log when creating a new user
    @api.expect(user_model)
    def post(self):
        data = request.get_json()

        # Validate email uniqueness
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already registered'}, 400

        # Validate the provided role_id
        role = Role.query.get(data['role_id'])
        if not role:
            return {'message': 'Invalid role ID provided'}, 400

        # Create a new user with the validated role_id
        new_user = User(
            email=data['email'],
            password_hash=generate_password_hash(data['password']),  # Password should be hashed before storing
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role  # Assign the validated role to the user
        )
        
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User created successfully'}, 201

    def get(self):
        users = User.query.all()
        return [{'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name} for user in users], 200


@api.route('/<int:user_id>')
class UserDetailController(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role_id': user.role_id  # Include role_id in the user details
        }, 200

    @api.expect(user_update_model)
    def put(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        data = request.get_json()

        # Validate role_id if provided
        if 'role_id' in data:
            role = Role.query.get(data['role_id'])
            if not role:
                return {'message': 'Invalid role ID provided'}, 400
            user.role_id = data['role_id']  # Update role_id

        # Update other fields if provided
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        
        if 'password' in data:
            user.password_hash = generate_password_hash(data['password'])  # Update hashed password

        db.session.commit()
        return {'message': 'User updated successfully'}, 200

    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200

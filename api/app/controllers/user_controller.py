from flask import Blueprint, request
from flask_restx import Api, Resource, fields
from app.models import User, Role
from app import db

api = Blueprint('user', __name__)
user_ns = Api(api, doc='/swagger/')

user_model = user_ns.model('User', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
})

class UserController(Resource):
    @user_ns.expect(user_model)
    def post(self):
        data = request.get_json()
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already registered'}, 400
        role = Role.query.filter_by(role_name='user').first()  # Assuming 'user' is the default role
        new_user = User(
            email=data['email'],
            password_hash=data['password'],  # You should hash the password before saving
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User created successfully'}, 201

user_ns.add_resource(UserController, '/register')

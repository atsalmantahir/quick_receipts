from flask_restx import Namespace, Resource, fields
from flask import request
from app import db
from app.models import Role

api = Namespace('roles', description="Roles operations")

# Define the model for the Role
role_model = api.model('Role', {
    'role_name': fields.String(required=True, description='Role name'),
    'description': fields.String(description='Role description'),
})

role_update_model = api.model('RoleUpdate', {
    'role_name': fields.String(description='Role name'),
    'description': fields.String(description='Role description'),
})

# Create a Role controller
@api.route('/')
class RoleController(Resource):
    # POST method to create a new role
    @api.expect(role_model)
    def post(self):
        data = request.get_json()
        if Role.query.filter_by(role_name=data['role_name']).first():
            return {'message': 'Role already exists'}, 400
        new_role = Role(
            role_name=data['role_name'],
            description=data.get('description', '')
        )
        db.session.add(new_role)
        db.session.commit()
        return {'message': 'Role created successfully'}, 201

    # GET method to get all roles
    def get(self):
        roles = Role.query.all()
        return [
            {
                'role_id': role.role_id,
                'role_name': role.role_name,
                'description': role.description
            }
            for role in roles
        ], 200

# Create a Role detail controller
@api.route('/<int:role_id>')
class RoleDetailController(Resource):
    # GET method to get details of a specific role
    def get(self, role_id):
        role = Role.query.get(role_id)
        if not role:
            return {'message': 'Role not found'}, 404
        return {
            'role_id': role.role_id,
            'role_name': role.role_name,
            'description': role.description
        }, 200

    # PUT method to update a role
    @api.expect(role_update_model)
    def put(self, role_id):
        role = Role.query.get(role_id)
        if not role:
            return {'message': 'Role not found'}, 404

        data = request.get_json()
        role.role_name = data.get('role_name', role.role_name)
        role.description = data.get('description', role.description)

        db.session.commit()
        return {'message': 'Role updated successfully'}, 200

    # DELETE method to delete a role
    def delete(self, role_id):
        role = Role.query.get(role_id)
        if not role:
            return {'message': 'Role not found'}, 404

        db.session.delete(role)
        db.session.commit()
        return {'message': 'Role deleted successfully'}, 200

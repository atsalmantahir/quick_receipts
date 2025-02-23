from app.models import db, User, Role, RolePermission
from datetime import datetime
from werkzeug.security import generate_password_hash

from werkzeug.security import generate_password_hash

def seed_data():
    # Check if roles exist, otherwise add them
    if not db.session.query(Role).filter_by(role_name="Super Admin").first():
        super_admin_role = Role(role_name="Super Admin", description="Has full access to all resources.")
        db.session.add(super_admin_role)

    if not db.session.query(Role).filter_by(role_name="Admin").first():
        admin_role = Role(role_name="Admin", description="Has access to manage users and content.")
        db.session.add(admin_role)

    if not db.session.query(Role).filter_by(role_name="User").first():
        user_role = Role(role_name="User", description="Regular user with limited access.")
        db.session.add(user_role)

    db.session.commit()

    # Check if role permissions exist, otherwise add them
    super_admin_role = db.session.query(Role).filter_by(role_name="Super Admin").first()
    admin_role = db.session.query(Role).filter_by(role_name="Admin").first()
    user_role = db.session.query(Role).filter_by(role_name="User").first()

    super_admin_permissions = [
        "view_all_users", "create_user", "delete_user", "view_all_content", "edit_content"
    ]
    admin_permissions = [
        "view_all_users", "create_user", "edit_content"
    ]
    user_permissions = [
        "view_content"
    ]

    # Add permissions if not already present
    for permission in super_admin_permissions:
        if not db.session.query(RolePermission).filter_by(role_id=super_admin_role.role_id, permission=permission).first():
            db.session.add(RolePermission(role_id=super_admin_role.role_id, permission=permission))
    
    for permission in admin_permissions:
        if not db.session.query(RolePermission).filter_by(role_id=admin_role.role_id, permission=permission).first():
            db.session.add(RolePermission(role_id=admin_role.role_id, permission=permission))

    for permission in user_permissions:
        if not db.session.query(RolePermission).filter_by(role_id=user_role.role_id, permission=permission).first():
            db.session.add(RolePermission(role_id=user_role.role_id, permission=permission))

    db.session.commit()

    # Check if users exist, otherwise add them
    if not db.session.query(User).filter_by(email="superadmin@example.com").first():
        super_admin_user = User(
            email="superadmin@example.com",
            password_hash=generate_password_hash("superadminpassword"),
            first_name="Super",
            last_name="Admin",
            role_id=super_admin_role.role_id
        )
        db.session.add(super_admin_user)

    if not db.session.query(User).filter_by(email="admin@example.com").first():
        admin_user = User(
            email="admin@example.com",
            password_hash=generate_password_hash("adminpassword"),
            first_name="Admin",
            last_name="User",
            role_id=admin_role.role_id
        )
        db.session.add(admin_user)

    if not db.session.query(User).filter_by(email="user@example.com").first():
        regular_user = User(
            email="user@example.com",
            password_hash=generate_password_hash("userpassword"),
            first_name="Regular",
            last_name="User",
            role_id=user_role.role_id
        )
        db.session.add(regular_user)

    db.session.commit()

    print("Seed data inserted.")


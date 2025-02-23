# app/utils/audit_log_helper.py

from functools import wraps
from flask import request
from app import db
from app.models import AuditLog
from datetime import datetime

def log_api_action(action_name):
    """Decorator to log actions automatically to the audit log"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract user_id from JWT or request context (you might have authentication)
            user_id = None
            if hasattr(request, 'user') and request.user:
                user_id = request.user.get('user_id')  # Modify based on your JWT payload
                user_id = 6
            
            user_id = 6
            # Log the action before executing the actual function
            log_audit(user_id, action_name, details=request.get_json())

            # Call the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_audit(user_id, action, details=None):
    """Helper function to log actions to the audit log."""
    if details is None:
        details = {}

    # Create a new audit log entry
    log = AuditLog(
        user_id=user_id,
        action=action,
        details=details
    )
    
    # Commit the log entry to the database
    db.session.add(log)
    db.session.commit()

    return log

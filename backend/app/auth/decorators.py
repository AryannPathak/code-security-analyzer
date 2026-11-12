"""JWT Authentication & Role-Based Authorization Guards for SmartFlow."""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from backend.app.models.user import User


def role_required(*allowed_roles):
    """Decorator ensuring current JWT identity belongs to one of allowed_roles.
    Usage:
        @role_required('ADMIN')
        @role_required('ADMIN', 'EMPLOYEE')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')

            if user_role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': f"Access restricted. Required role(s): {', '.join(allowed_roles)}. Your role: {user_role}"
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required():
    return role_required('ADMIN')


def employee_required():
    return role_required('ADMIN', 'EMPLOYEE')


def customer_required():
    return role_required('ADMIN', 'CUSTOMER')


def get_current_user():
    """Retrieve the current logged in User model object from JWT identity."""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return None
        return User.query.get(int(user_id))
    except Exception:
        return None

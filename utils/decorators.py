from flask_jwt_extended import get_jwt_identity
from functools import wraps
from flask import jsonify

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()

        # Identity MUST be a dict
        if not isinstance(identity, dict):
            return jsonify({"message": "Invalid token"}), 401

        if identity.get("role") != "admin":
            return jsonify({"message": "Admin access required"}), 403

        return fn(*args, **kwargs)

    return wrapper

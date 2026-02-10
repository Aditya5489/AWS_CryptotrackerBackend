from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt,
    create_access_token
)
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True)

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "All fields required"}), 400

    table = current_app.dynamodb.Table("Users")

    # Check if user already exists
    if "Item" in table.get_item(Key={"email": email}):
        return jsonify({"message": "User already exists"}), 409

    table.put_item(
        Item={
            "email": email,
            "username": username,
            "password": generate_password_hash(password),
            "role": "user"
        }
    )

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    table = current_app.dynamodb.Table("Users")
    response = table.get_item(Key={"email": email})
    user = response.get("Item")

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid email or password"}), 401

    access_token = create_access_token(
        identity=user["email"],
        additional_claims={"role": user["role"]}
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "username": user.get("username", ""),
            "email": user["email"],
            "role": user["role"]
        }
    }), 200


@auth_bp.route("/check", methods=["GET"])
@jwt_required()
def check_login():
    email = get_jwt_identity()
    claims = get_jwt()

    table = current_app.dynamodb.Table("Users")
    user = table.get_item(Key={"email": email}).get("Item")

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "message": "User is logged in",
        "user": {
            "username": user.get("username", ""),
            "email": email,
            "role": claims.get("role")
        }
    }), 200


@auth_bp.route("/logout", methods=["POST", "OPTIONS"])
@jwt_required(optional=True)
def logout():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    identity = get_jwt_identity()
    claims = get_jwt()

    return jsonify({
        "success": True,
        "message": "Logged out successfully",
        "user": identity,
        "role": claims.get("role") if claims else None
    }), 200

from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from functools import wraps
from boto3.dynamodb.conditions import Key

admin_bp = Blueprint("admin", __name__)

# ============================
# ADMIN ROLE DECORATOR
# ============================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # identity is EMAIL (string)
            email = get_jwt_identity()
            claims = get_jwt()
            role = claims.get("role")

            if role != "admin":
                return jsonify({"error": "Admin access required"}), 403

            # verify admin still exists in DB
            users_table = current_app.dynamodb.Table("Users")
            response = users_table.get_item(Key={"email": email})

            if "Item" not in response:
                return jsonify({"error": "Admin not found"}), 404

            if response["Item"].get("role") != "admin":
                return jsonify({"error": "Admin privileges revoked"}), 403

            kwargs["admin_email"] = email
            return f(*args, **kwargs)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return decorated_function


# ============================
# GET ALL USERS
# ============================
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def get_all_users(admin_email):
    try:
        users_table = current_app.dynamodb.Table("Users")
        response = users_table.scan()

        users = []
        for user in response.get("Items", []):
            if user.get("role") == "admin":
                continue

            users.append({
                "email": user.get("email"),
                "username": user.get("username", "N/A"),
                "name": user.get("name", user.get("username", "N/A")),
                "role": user.get("role", "user"),
                "created_at": user.get("created_at", "N/A")
            })

        return jsonify({
            "success": True,
            "users": users,
            "count": len(users)
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================
# GET USER ALERTS
# ============================
@admin_bp.route("/user/<email>/alerts", methods=["GET"])
@jwt_required()
@admin_required
def get_user_alerts(email, admin_email):
    try:
        users_table = current_app.dynamodb.Table("Users")
        if "Item" not in users_table.get_item(Key={"email": email}):
            return jsonify({"error": "User not found"}), 404

        alerts_table = current_app.dynamodb.Table("CryptoAlerts")
        response = alerts_table.query(
            KeyConditionExpression=Key("email").eq(email)
        )

        alerts = response.get("Items", [])

        return jsonify({
            "success": True,
            "email": email,
            "alerts": alerts,
            "count": len(alerts)
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================
# GET USER WATCHLIST
# ============================
@admin_bp.route("/user/<email>/watchlist", methods=["GET"])
@jwt_required()
@admin_required
def get_user_watchlist(email, admin_email):
    try:
        users_table = current_app.dynamodb.Table("Users")
        if "Item" not in users_table.get_item(Key={"email": email}):
            return jsonify({"error": "User not found"}), 404

        watchlist_table = current_app.dynamodb.Table("Watchlist")
        response = watchlist_table.get_item(Key={"email": email})

        watchlist = response.get("Item", {}).get("coins", [])
        if isinstance(watchlist, set):
            watchlist = list(watchlist)

        return jsonify({
            "success": True,
            "email": email,
            "watchlist": watchlist,
            "count": len(watchlist)
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================
# DELETE USER
# ============================
@admin_bp.route("/user/<email>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(email, admin_email):
    try:
        if email == admin_email:
            return jsonify({"error": "Cannot delete own admin account"}), 400

        users_table = current_app.dynamodb.Table("Users")
        user = users_table.get_item(Key={"email": email}).get("Item")

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.get("role") == "admin":
            return jsonify({"error": "Cannot delete another admin"}), 400

        users_table.delete_item(Key={"email": email})

        alerts_table = current_app.dynamodb.Table("CryptoAlerts")
        alerts = alerts_table.query(
            KeyConditionExpression=Key("email").eq(email)
        ).get("Items", [])

        for alert in alerts:
            alerts_table.delete_item(
                Key={
                    "email": email,
                    "alertId": alert["alertId"]
                }
            )

        watchlist_table = current_app.dynamodb.Table("Watchlist")
        watchlist_table.delete_item(Key={"email": email})

        return jsonify({
            "success": True,
            "message": f"User {email} deleted successfully"
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

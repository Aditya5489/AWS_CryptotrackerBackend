from flask import Blueprint, request, jsonify, current_app
import uuid
from datetime import datetime
from boto3.dynamodb.conditions import Key

alert_bp = Blueprint("alerts", __name__)

def get_alert_table():
    return current_app.dynamodb.Table("CryptoAlerts")

@alert_bp.route("/alerts", methods=["POST"])
def create_alert():
    table = get_alert_table()
    data = request.json

    alert = {
        "email": data["email"],
        "alertId": str(uuid.uuid4()),
        "coinId": data["coin"]["id"],
        "coinName": data["coin"]["name"],
        "symbol": data["coin"]["symbol"],
        "image": data["coin"]["image"],
        "condition": data["condition"],
        "targetPrice": data["targetPrice"],
        "status": "active",
        "createdAt": datetime.utcnow().strftime("%Y-%m-%d")
    }

    table.put_item(Item=alert)
    return jsonify(alert), 201

@alert_bp.route("/alerts/<email>", methods=["GET"])
def get_alerts(email):
    table = get_alert_table()
    response = table.query(
        KeyConditionExpression=Key("email").eq(email)
    )
    return jsonify(response["Items"]), 200

@alert_bp.route("/alerts/<email>/<alert_id>/toggle", methods=["PATCH"])
def toggle_alert(email, alert_id):
    table = get_alert_table()

    response = table.get_item(
        Key={"email": email, "alertId": alert_id}
    )

    if "Item" not in response:
        return jsonify({"error": "Alert not found"}), 404

    current_status = response["Item"].get("status", "active")
    new_status = "active" if current_status == "disabled" else "disabled"

    response = table.update_item(
        Key={"email": email, "alertId": alert_id},
        UpdateExpression="SET #s = :val",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":val": new_status},
        ReturnValues="UPDATED_NEW"
    )

    return jsonify(response["Attributes"]), 200

@alert_bp.route("/alerts/<email>/<alert_id>", methods=["DELETE"])
def delete_alert(email, alert_id):
    table = get_alert_table()
    table.delete_item(
        Key={"email": email, "alertId": alert_id}
    )
    return jsonify({"message": "Alert deleted"}), 200


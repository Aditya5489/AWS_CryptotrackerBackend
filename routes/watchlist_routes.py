from flask import Blueprint, request, jsonify, current_app

watchlist_bp = Blueprint("watchlist", __name__)

# GET watchlist
@watchlist_bp.route("/watchlist", methods=["GET"])
def get_watchlist():
    email = request.args.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    table = current_app.dynamodb.Table("Watchlist")
    response = table.get_item(Key={"email": email})
    item = response.get("Item")

    coins = list(item["coins"]) if item and "coins" in item else []

    return jsonify({
        "email": email,
        "watchlist": coins
    }), 200


# ADD coin
@watchlist_bp.route("/watchlist/add", methods=["POST"])
def add_to_watchlist():
    data = request.get_json(force=True)
    email = data.get("email")
    coin_id = data.get("coinId")

    if not email or not coin_id:
        return jsonify({"error": "Email and coinId required"}), 400

    table = current_app.dynamodb.Table("Watchlist")

    # Create item if not exists, then ADD
    table.update_item(
        Key={"email": email},
        UpdateExpression="ADD coins :c",
        ExpressionAttributeValues={":c": {coin_id}},
        ReturnValues="UPDATED_NEW"
    )

    response = table.get_item(Key={"email": email})
    coins = list(response["Item"]["coins"])

    return jsonify({
        "message": "Coin added",
        "watchlist": coins
    }), 200


# REMOVE coin
@watchlist_bp.route("/watchlist/remove", methods=["POST"])
def remove_from_watchlist():
    data = request.get_json(force=True)
    email = data.get("email")
    coin_id = data.get("coinId")

    if not email or not coin_id:
        return jsonify({"error": "Email and coinId required"}), 400

    table = current_app.dynamodb.Table("Watchlist")

    table.update_item(
        Key={"email": email},
        UpdateExpression="DELETE coins :c",
        ExpressionAttributeValues={":c": {coin_id}},
        ReturnValues="UPDATED_NEW"
    )

    response = table.get_item(Key={"email": email})
    item = response.get("Item", {})
    coins = list(item.get("coins", []))


    return jsonify({
        "message": "Coin removed",
        "watchlist": coins
    }), 200

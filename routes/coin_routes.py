import requests
from flask import Blueprint, jsonify, current_app

coin_bp = Blueprint("coin", __name__)

@coin_bp.route("/coins/<string:coin_id>", methods=["GET"])
def get_coin_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"

    headers = {
        "x-cg-demo-api-key": current_app.config["COINGECKO_API_KEY"]
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return jsonify(res.json()), 200
    except Exception as e:
        return jsonify({
            "message": "Coin data fetch failed",
            "error": str(e)
        }), 500

@coin_bp.route("/coins/markets", methods=["GET"])
def get_100_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 120,
        "page": 1,
        "sparkline": "false"
    }

    headers = {
        "x-cg-demo-api-key": current_app.config["COINGECKO_API_KEY"]
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), 200

    except requests.exceptions.RequestException as e:
        return jsonify({
            "message": "Failed to fetch coins",
            "error": str(e)
        }), 500
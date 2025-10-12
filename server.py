from flask import Flask, render_template, jsonify, request
import json
import time
from datetime import datetime

app = Flask(__name__)

coin_data = {
    "current_price": 0.01,
    "price_history": []
}

def initialize_history():
    for i in range(50):
        coin_data["price_history"].append({
            "timestamp": time.time() - (50 - i) * 3600,
            "price": 0.01,
            "date": datetime.fromtimestamp(time.time() - (50 - i) * 3600).strftime('%H:%M')
        })

initialize_history()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/price_data')
def price_data():
    return jsonify(coin_data["price_history"][-20:])

@app.route('/api/current_price')
def current_price():
    return jsonify({
        "price": coin_data["current_price"],
        "market_cap": coin_data["current_price"] * 10000
    })

@app.route('/admin/update_price', methods=['POST'])
def update_price():
    data = request.json
    if data.get("secret_key") != "ADMIN_SECRET_KEY":
        return jsonify({"error": "Unauthorized"}), 401
    
    new_price = float(data["new_price"])
    coin_data["current_price"] = new_price
    
    coin_data["price_history"].append({
        "timestamp": time.time(),
        "price": new_price,
        "date": datetime.now().strftime('%H:%M')
    })
    
    if len(coin_data["price_history"]) > 100:
        coin_data["price_history"] = coin_data["price_history"][-100:]
    
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

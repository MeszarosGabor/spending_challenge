from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime


app = Flask(__name__)
CORS(app)


IN_MEMORY_STORAGE = []

@app.route("/spendings", methods=["GET"])
def get_spendings():
    return jsonify(IN_MEMORY_STORAGE)

@app.route("/add_spending", methods=["POST"])
def add_spending():
    new_spending= request.get_json()
    IN_MEMORY_STORAGE.append(new_spending)
    return jsonify({"Response": 200})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

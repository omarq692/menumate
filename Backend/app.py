from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["menumate"]

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to MenuMate Backend!"})

@app.route('/api/healthlogs', methods=['POST'])
def add_health_log():
    try:
        data = request.get_json()
        required_fields = ['user_id', 'food_name', 'calories', 'protein', 'carbs', 'fats', 'meal_type', 'date']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing fields in request"}), 400
        db.healthlogs.insert_one(data)
        return jsonify({"message": "Health log added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/healthlogs/<user_id>', methods=['GET'])
def get_health_logs(user_id):
    try:
        logs = list(db.healthlogs.find({"user_id": user_id}, {"_id": 0}))
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

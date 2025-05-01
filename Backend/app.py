from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["menumate"]

# Nutritionix credentials
nutritionix_app_id = os.getenv("NUTRITIONIX_APP_ID")
nutritionix_api_key = os.getenv("NUTRITIONIX_API_KEY")

# ---------------------- Auto-Fill + Log Nutrition ----------------------

@app.route('/api/autofill-nutrition', methods=['POST'])
def autofill_nutrition():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        meal_type = data.get("meal_type", "Unspecified")
        description = data.get("description")

        if not user_id or not description:
            return jsonify({"error": "Missing user_id or description"}), 400

        url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        headers = {
            "x-app-id": nutritionix_app_id,
            "x-app-key": nutritionix_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "query": description
        }

        response = requests.post(url, json=payload, headers=headers)
        result = response.json()

        if "foods" not in result:
            return jsonify({"error": "No nutrition data found"}), 500

        logs = []
        date_today = datetime.now().strftime("%Y-%m-%d")

        for item in result["foods"]:
            log = {
                "user_id": user_id,
                "food_name": item["food_name"],
                "calories": item["nf_calories"],
                "protein": item["nf_protein"],
                "carbs": item["nf_total_carbohydrate"],
                "fats": item["nf_total_fat"],
                "meal_type": meal_type,
                "date": date_today
            }
            logs.append(log)

        db.healthlogs.insert_many(logs)

        return jsonify({"message": "Food logged successfully", "logged_items": logs}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------- Daily Summary ----------------------

@app.route('/api/daily-summary/<user_id>', methods=['GET'])
def daily_summary(user_id):
    try:
        date_today = datetime.now().strftime("%Y-%m-%d")

        pipeline = [
            { "$match": { "user_id": user_id, "date": date_today } },
            { "$group": {
                "_id": None,
                "total_calories": { "$sum": "$calories" },
                "total_protein": { "$sum": "$protein" },
                "total_carbs": { "$sum": "$carbs" },
                "total_fats": { "$sum": "$fats" }
            }}
        ]

        result = list(db.healthlogs.aggregate(pipeline))
        if not result:
            return jsonify({"message": "No food logs found for today."}), 200

        summary = result[0]
        return jsonify({
            "date": date_today,
            "calories": summary["total_calories"],
            "protein": summary["total_protein"],
            "carbs": summary["total_carbs"],
            "fats": summary["total_fats"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------- Root Route ----------------------

@app.route('/')
def home():
    return jsonify({"message": "Welcome to MenuMate Backend!"})

# ---------------------- Run ----------------------

if __name__ == '__main__':
    app.run(debug=True, port=5000)

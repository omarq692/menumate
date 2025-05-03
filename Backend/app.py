from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os
import requests
from datetime import datetime

# Load env variables
load_dotenv()

# ---------- Define Paths to Frontend templates and static files (css/js) ----------
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Frontend'))

app = Flask(
    __name__,
    template_folder = os.path.join(frontend_path, 'templates'),
    static_folder = os.path.join(frontend_path, 'static')
)

CORS(app)

# Route to Landing page
@app.route('/')
def index():
    return render_template('index.html')
# Route to Explore Page
@app.route('/explore')
def explore():
    return render_template('explore.html')
# Route to Profile Page
@app.route('/profile')
def profile():
    return render_template('profile.html')
# Route to SignUp Page
@app.route('/signup')
def signup():
    return render_template('signup.html')

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["menumate"]

# Nutritionix credentials
nutritionix_app_id = os.getenv("NUTRITIONIX_APP_ID")
nutritionix_api_key = os.getenv("NUTRITIONIX_API_KEY")

# Helper
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    if "user_id" in doc:
        doc["user_id"] = str(doc["user_id"])
    if "likes" in doc:
        doc["likes"] = [str(uid) for uid in doc["likes"]]
    if "comments" in doc:
        for comment in doc["comments"]:
            if "user_id" in comment:
                comment["user_id"] = str(comment["user_id"])
    return doc

# ---------- User Routes ----------

@app.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    bio = data.get('bio', '')

    if not username:
        return jsonify({"error": "Username is required"}), 400

    user = {
        "username": username,
        "bio": bio,
        "followers": [],
        "following": []
    }

    result = db.users.insert_one(user)
    user['_id'] = str(result.inserted_id)
    return jsonify(user), 201

# ---------- Post Routes ----------

@app.route('/api/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    user_id = data.get('user_id')
    text = data.get('text')
    media_url = data.get('media_url', '')

    if not user_id or not text:
        return jsonify({"error": "User ID and text are required"}), 400

    post = {
        "user_id": ObjectId(user_id),
        "text": text,
        "media_url": media_url,
        "likes": [],
        "comments": [],
        "timestamp": data.get('timestamp')
    }

    result = db.posts.insert_one(post)
    inserted_post = db.posts.find_one({"_id": result.inserted_id})
    return jsonify(serialize_doc(inserted_post)), 201

@app.route('/api/posts', methods=['GET'])
def get_all_posts():
    posts = list(db.posts.find().sort("timestamp", -1))
    result = []
    for post in posts:
        post = serialize_doc(post)
        user = db.users.find_one({"_id": ObjectId(post["user_id"])})
        post["username"] = user.get("username", "Unknown User") if user else "Unknown User"
        result.append(post)
    return jsonify(result), 200

@app.route('/api/posts/<post_id>/like', methods=['POST'])
def like_post(post_id):
    user_id = request.get_json().get('user_id')
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
    db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$addToSet": {"likes": ObjectId(user_id)}}
    )
    return jsonify({"message": "Post liked!"}), 200

@app.route('/api/posts/<post_id>/comment', methods=['POST'])
def comment_post(post_id):
    data = request.get_json()
    comment = {
        "user_id": ObjectId(data.get("user_id")),
        "text": data.get("comment"),
        "timestamp": data.get("timestamp")
    }
    db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": comment}}
    )
    return jsonify({"message": "Comment added!"}), 201

# ---------- Health Log Routes ----------

@app.route('/api/healthlogs', methods=['POST'])
def add_health_log():
    try:
        data = request.get_json()
        required_fields = ['user_id', 'food_name', 'calories', 'protein', 'carbs', 'fats', 'meal_type', 'date']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing fields"}), 400
        db.healthlogs.insert_one(data)
        return jsonify({"message": "Health log added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/healthlogs/<user_id>', methods=['GET'])
def get_health_logs(user_id):
    logs = list(db.healthlogs.find({"user_id": user_id}, {"_id": 0}))
    return jsonify(logs), 200

# ---------- Nutritionix + Logging Route ----------

@app.route('/api/autofill-nutrition', methods=['POST'])
def autofill_nutrition():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        description = data.get("description")
        meal_type = data.get("meal_type", "Unspecified")

        if not user_id or not description:
            return jsonify({"error": "Missing user_id or description"}), 400

        headers = {
            "x-app-id": nutritionix_app_id,
            "x-app-key": nutritionix_api_key,
            "Content-Type": "application/json"
        }

        payload = {"query": description}
        url = "https://trackapi.nutritionix.com/v2/natural/nutrients"

        response = requests.post(url, json=payload, headers=headers)
        result = response.json()

        if "foods" not in result:
            return jsonify({"error": "No nutrition data returned"}), 500

        logs = []
        today = datetime.now().strftime("%Y-%m-%d")
        for food in result["foods"]:
            entry = {
                "user_id": user_id,
                "food_name": food["food_name"],
                "calories": food["nf_calories"],
                "protein": food["nf_protein"],
                "carbs": food["nf_total_carbohydrate"],
                "fats": food["nf_total_fat"],
                "meal_type": meal_type,
                "date": today
            }
            logs.append(entry)

        db.healthlogs.insert_many(logs)
        return jsonify({"message": "Nutrition logged", "data": logs}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Daily Summary ----------

@app.route('/api/daily-summary/<user_id>', methods=['GET'])
def daily_summary(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    pipeline = [
        { "$match": { "user_id": user_id, "date": today } },
        { "$group": {
            "_id": None,
            "calories": { "$sum": "$calories" },
            "protein": { "$sum": "$protein" },
            "carbs": { "$sum": "$carbs" },
            "fats": { "$sum": "$fats" }
        }}
    ]
    result = list(db.healthlogs.aggregate(pipeline))
    if result:
        return jsonify(result[0]), 200
    else:
        return jsonify({"message": "No logs for today"}), 200

# ---------- Run App ----------

if __name__ == '__main__':
    app.run(debug=True, port=5000)

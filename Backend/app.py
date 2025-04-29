from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Connect to MongoDB Atlas
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["menumate"]

# Helper: Convert MongoDB ObjectId to string
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

# User Routes
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

# Post Routes
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

    # Fetch and return the inserted post
    inserted_post = db.posts.find_one({"_id": result.inserted_id})
    return jsonify(serialize_doc(inserted_post)), 201

@app.route('/api/posts', methods=['GET'])
def get_all_posts():
    posts = list(db.posts.find().sort("timestamp", -1))
    posts_with_usernames = []

    for post in posts:
        post = serialize_doc(post)

        # Lookup the username
        try:
            user = db.users.find_one({"_id": ObjectId(post["user_id"])})
            if user:
                post["username"] = user.get("username", "Unknown User")
            else:
                post["username"] = "Unknown User"
        except Exception as e:
            post["username"] = "Unknown User"

        posts_with_usernames.append(post)

    return jsonify(posts_with_usernames), 200

@app.route('/api/posts/<post_id>/like', methods=['POST'])
def like_post(post_id):
    user_id = request.get_json().get('user_id')
    if not user_id:
        return jsonify({"error": "User ID required"}), 400

    try:
        db.posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$addToSet": {"likes": ObjectId(user_id)}}
        )
        return jsonify({"message": "Post liked!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/posts/<post_id>/comment', methods=['POST'])
def comment_post(post_id):
    data = request.get_json()
    user_id = data.get('user_id')
    comment_text = data.get('comment')

    if not user_id or not comment_text:
        return jsonify({"error": "User ID and comment are required"}), 400

    comment = {
        "user_id": ObjectId(user_id),
        "text": comment_text,
        "timestamp": data.get('timestamp')
    }

    try:
        db.posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$push": {"comments": comment}}
        )
        return jsonify({"message": "Comment added!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Basic Routes
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to MenuMate Backend!"})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5000)

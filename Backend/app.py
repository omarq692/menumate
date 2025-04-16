from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Initialize Flask app
app = Flask(__name__)
CORS(app)

# ✅ Get MongoDB URI from .env
mongo_uri = os.getenv("MONGO_URI")
print("MONGO URI:", mongo_uri)  # Debug: Make sure it's not None or localhost

# ✅ Connect to MongoDB Atlas
client = MongoClient(mongo_uri)
db = client["menumate"]  # You can rename the database if desired

# ✅ Route to test MongoDB connection
@app.route('/api/testdb', methods=['GET'])
def test_db():
    try:
        # Insert test document
        db.test.insert_one({"message": "MongoDB is connected!", "status": True})
        # Return all test documents (hide _id)
        data = list(db.test.find({}, {"_id": 0}))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Optional root route
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to MenuMate Backend!"})

# ✅ Run Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5000)

from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["menumate"]  # You can change the DB name if needed

# Test route for MongoDB
@app.route('/api/testdb', methods=['GET'])
def test_db():
    db.test.insert_one({"message": "MongoDB is connected!", "status": True})
    data = list(db.test.find({}, {"_id": 0}))
    return jsonify(data)

# Existing imports and routes
# from auth import auth_bp
# app.register_blueprint(auth_bp)
# etc...

if __name__ == '__main__':
    app.run(debug=True, port=5000)

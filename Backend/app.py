from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["menumate"]  # Use whatever name you want

# Your original test route
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'message': 'Backend Connected!'})

# MongoDB test route
@app.route('/api/testdb', methods=['GET'])
def test_db():
    db.test.insert_one({"msg": "Mongo is connected!", "status": True})
    result = list(db.test.find({}, {"_id": 0}))
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

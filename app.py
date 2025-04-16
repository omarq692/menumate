from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow frontend requests (from React)

# Connect to MongoDB using URI from .env
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["menumate"]  # Your database name

# Test route to confirm everything is working
@app.route('/api/testdb', methods=['GET'])
def test_db():
    test_data = {
        "message": "MongoDB is connected!",
        "status": True
    }
    # Insert test data into 'test' collection
    db.test.insert_one(test_data)

    # Return all entries from 'test' collection, hiding _id
    all_data = list(db.test.find({}, {"_id": 0}))
    return jsonify(all_data)

# Run the server
if __name__ == '__main__':
    app.run(debug=True, port=5000)


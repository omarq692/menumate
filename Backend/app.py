from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import os

from healthlogs import get_all_healthlogs

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["menumate"]

@app.route("/")
def home():
    return jsonify({"message": "MenuMate backend is running!"})

@app.route("/api/healthlogs", methods=["GET"])
def healthlogs():
    logs = get_all_healthlogs(db)
    return jsonify(logs)

if __name__ == "__main__":
    app.run(debug=True)

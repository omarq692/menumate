import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_FILE = os.path.join(BASE_DIR, "users.json")

def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as f:
            json.dump([], f)
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def add_user(email, password=None, source="manual"):
    users = load_users()
    users.append({
        "email": email,
        "password": password,
        "source": source
    })
    save_users(users)

def find_user(email):
    users = load_users()
    return next((user for user in users if user["email"] == email), None)

from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from authlib.integrations.base_client.errors import OAuthError
from users import add_user, find_user
from oauth_config import oauth, init_oauth
import os
import json
import secrets
import time
from math import radians, cos, sin, asin, sqrt
from dotenv import load_dotenv

# ---------------------- Load Environment ----------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

CORS(app, supports_credentials=True)

app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True
)

bcrypt = Bcrypt(app)
init_oauth(app)

# ---------------------- Paths ----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_REDIRECT_BASE = "https://kerolosassad.github.io/MenuMate/"
USER_EXPERIENCE_FILE = os.path.join(BASE_DIR, "users_experiences.json")
SHARED_EXPERIENCE_FILE = os.path.join(BASE_DIR, "shared_experiences.json")
USER_PROFILE_FILE = os.path.join(BASE_DIR, "users_profiles.json")
user_locations = {}  # email -> {lat, lon, last_seen}

# ---------------------- Helper Functions ----------------------

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# ---------------------- Auth Endpoints ----------------------

@app.route("/api/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return '', 204
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    first_name = data.get("firstName", "").strip()
    last_name = data.get("lastName", "").strip()
    dob = data.get("dob", "")
    height_feet = data.get("heightFeet")
    height_inches = data.get("heightInches")
    weight_lbs = data.get("weightLbs")
    gender = data.get("gender")
    activity_level = data.get("activityLevel")
    dietary_goal = data.get("dietaryGoal", "").strip()
    dietary_restrictions = data.get("dietaryRestrictions", "").strip()
    experience_pass = data.get("experiencePassOptIn", False)

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400
    if find_user(email):
        return jsonify({"message": "User already exists."}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    add_user(email, hashed_password)

    profiles = load_json(USER_PROFILE_FILE, {})
    profiles[email] = {
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": dob,
        "height_feet": height_feet,
        "height_inches": height_inches,
        "weight_lbs": weight_lbs,
        "gender": gender,
        "activity_level": activity_level,
        "dietary_goal": dietary_goal,
        "dietary_restrictions": dietary_restrictions,
        "experience_pass": experience_pass
    }
    save_json(USER_PROFILE_FILE, profiles)

    return jsonify({"message": "User registered successfully."}), 201

@app.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return '', 204
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user = find_user(email)
    if not user or not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid credentials."}), 401
    session.clear()
    session["user_email"] = email
    session["login_method"] = "manual"
    return jsonify({"message": "Login successful", "email": email}), 200

@app.route("/auth/google")
def google_login():
    nonce = secrets.token_urlsafe(16)
    session["oauth_nonce"] = nonce
    redirect_uri = FRONTEND_REDIRECT_BASE + "POC_Logging_info.html"
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)

@app.route("/auth/google/callback")
def google_callback():
    try:
        if "error" in request.args:
            return redirect(FRONTEND_REDIRECT_BASE)

        token = oauth.google.authorize_access_token()
        nonce = session.pop("oauth_nonce", None)
        if not nonce:
            return "Missing nonce", 400

        user_info = oauth.google.parse_id_token(token, nonce=nonce)
        email = user_info["email"]

        if not find_user(email):
            add_user(email, password=None, source="google")

        session.clear()
        session["user_email"] = email
        session["login_method"] = "google"

        return redirect(FRONTEND_REDIRECT_BASE + "POC_Logging_info.html")

    except OAuthError as e:
        print("OAuthError:", e)
        return redirect(FRONTEND_REDIRECT_BASE)
    except Exception as e:
        print("Unexpected error:", e)
        return redirect(FRONTEND_REDIRECT_BASE)

@app.route("/api/user")
def get_user():
    email = session.get("user_email")
    login_method = session.get("login_method")
    if not email:
        return jsonify({"logged_in": False}), 200

    if login_method == "manual":
        profiles = load_json(USER_PROFILE_FILE, {})
        user_profile = profiles.get(email)
        if user_profile:
            name = user_profile.get("first_name", "") + " " + user_profile.get("last_name", "")
        else:
            name = email.split("@")[0]
    else:
        name = email.split("@")[0]

    return jsonify({"logged_in": True, "email": email, "display_name": name})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(FRONTEND_REDIRECT_BASE)

# ---------------------- Experience and Share Logic ----------------------

@app.route("/api/experience", methods=["POST"])
def save_experience():
    email = session.get("user_email")
    if not email:
        return jsonify({"message": "Unauthorized"}), 401
    data = request.get_json()
    all_data = load_json(USER_EXPERIENCE_FILE, {})
    all_data[email] = {
        "experience": data,
        "last_updated": int(time.time())
    }
    save_json(USER_EXPERIENCE_FILE, all_data)
    return jsonify({"message": "Experience saved."}), 200

@app.route("/api/shared_experiences")
def get_shared_experiences():
    email = session.get("user_email")
    shared = load_json(SHARED_EXPERIENCE_FILE, {})
    return jsonify(shared.get(email, []))

@app.route("/api/shared/delete", methods=["POST"])
def delete_shared():
    email = session.get("user_email")
    if not email:
        return jsonify({"message": "Unauthorized"}), 401
    shared = load_json(SHARED_EXPERIENCE_FILE, {})
    shared[email] = []
    save_json(SHARED_EXPERIENCE_FILE, shared)
    return jsonify({"message": "Deleted"}), 200

@app.route("/api/shared/star", methods=["POST"])
def toggle_star():
    email = session.get("user_email")
    if not email:
        return jsonify({"message": "Unauthorized"}), 401
    data = request.get_json()
    target_email = data.get("email")
    shared = load_json(SHARED_EXPERIENCE_FILE, {})
    for exp in shared.get(email, []):
        if exp.get("email") == target_email:
            exp["starred"] = not exp.get("starred", False)
            break
    save_json(SHARED_EXPERIENCE_FILE, shared)
    return jsonify({"message": "Toggled starred"}), 200

# ---------------------- Live Location-Based Sharing ----------------------

@app.route("/api/track_location", methods=["POST"])
def track_location():
    email = session.get("user_email")
    if not email:
        return jsonify({"message": "Unauthorized"}), 401

    profiles = load_json(USER_PROFILE_FILE, {})
    user_profile = profiles.get(email, {})
    opted_in = user_profile.get("experience_pass", False)

    if not opted_in:
        return jsonify({"message": "ExperiencePass not opted in."}), 200

    data = request.get_json()
    lat = data.get("latitude")
    lon = data.get("longitude")
    if lat is None or lon is None:
        return jsonify({"message": "Missing coordinates"}), 400

    user_locations[email] = {"lat": lat, "lon": lon, "last_seen": time.time()}

    experiences = load_json(USER_EXPERIENCE_FILE, {})
    shared = load_json(SHARED_EXPERIENCE_FILE, {})

    now = time.time()
    sender_experience = experiences.get(email)
    if not sender_experience:
        return jsonify({"message": "Location updated (no experience)."}), 200

    for receiver, info in user_locations.items():
        if receiver == email or now - info["last_seen"] > 300:
            continue
        dist = haversine(lat, lon, info["lat"], info["lon"])
        if dist <= 1:
            receiver_profile = profiles.get(receiver, {})
            if not receiver_profile.get("experience_pass", False):
                continue
            if receiver not in shared:
                shared[receiver] = []
            if not any(e.get("email") == email for e in shared[receiver]):
                if len(shared[receiver]) >= 10:
                    for i, exp in enumerate(shared[receiver]):
                        if not exp.get("starred"):
                            shared[receiver].pop(i)
                            break
                shared[receiver].append({**sender_experience["experience"], "email": email, "starred": False})

    save_json(SHARED_EXPERIENCE_FILE, shared)
    return jsonify({"message": "Location updated and nearby sharing checked."}), 200

# ---------------------- Run App ----------------------

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from authlib.integrations.base_client.errors import OAuthError
from users import add_user, find_user
from oauth_config import oauth, init_oauth
from dotenv import load_dotenv
import os, json, secrets, time, redis, traceback, sys

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)
init_oauth(app)

app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True
)

REDIS_URL = os.getenv("REDIS_URL")
try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    print("✅ Connected to Redis")
except Exception as e:
    print(f"[Redis Error] Could not connect to Redis: {e}")
    redis_client = None

GEO_KEY = "user_locations"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_REDIRECT_BASE = "https://kerolosassad.github.io/MenuMate/"
USER_EXPERIENCE_FILE = os.path.join(BASE_DIR, "users_experiences.json")
SHARED_EXPERIENCE_FILE = os.path.join(BASE_DIR, "shared_experiences.json")
USER_PROFILE_FILE = os.path.join(BASE_DIR, "users_profiles.json")

def load_json(path, default): return json.load(open(path)) if os.path.exists(path) else default
def save_json(path, data): json.dump(data, open(path, "w"), indent=2)
def get_logged_in_email(): return session.get("user_email")
def get_user_profile():
    email = get_logged_in_email()
    profiles = load_json(USER_PROFILE_FILE, {})
    return email, profiles.get(email, {})
def ensure_logged_in():
    email = get_logged_in_email()
    if not email: return None, {"message": "Unauthorized"}, 401
    return email, None, None

@app.route("/redis_ping")
def redis_ping():
    try:
        if not redis_client:
            return "Redis client not initialized", 500
        redis_client.set("ping_test", "pong")
        return "Redis connected and working", 200
    except Exception as e:
        return f"Redis ping failed: {e}", 500

@app.route("/api/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS": return '', 204
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or (not password and session.get("login_method") != "google"):
        return jsonify({"message": "Email and password are required."}), 400
    if find_user(email): return jsonify({"message": "User already exists."}), 400
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8") if password else None
    add_user(email, hashed_password)
    profiles = load_json(USER_PROFILE_FILE, {})
    profiles[email] = {
        "first_name": data.get("firstName", "").strip(),
        "last_name": data.get("lastName", "").strip(),
        "date_of_birth": data.get("dob", ""),
        "height_feet": data.get("heightFeet"),
        "height_inches": data.get("heightInches"),
        "weight_lbs": data.get("weightLbs"),
        "gender": data.get("gender"),
        "activity_level": data.get("activityLevel"),
        "dietary_goal": data.get("dietaryGoal", "").strip(),
        "dietary_restrictions": data.get("dietaryRestrictions", "").strip(),
        "experience_pass": data.get("experiencePassOptIn", False)
    }
    save_json(USER_PROFILE_FILE, profiles)
    return jsonify({"message": "User registered successfully."}), 201

@app.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS": return '', 204
    data = request.get_json()
    email, password = data.get("email"), data.get("password")
    user = find_user(email)
    if not user or not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid credentials."}), 401
    session.clear()
    session["user_email"] = email
    session["login_method"] = "manual"
    return jsonify({"message": "Login successful", "email": email}), 200

@app.route("/auth/google")
def google_login():
    session["oauth_nonce"] = secrets.token_urlsafe(16)
    print("[Google Login] Initiating redirect to Google login...")
    return oauth.google.authorize_redirect(
        nonce=session["oauth_nonce"],
        prompt="select_account"  # ✅ forces account selection
    )

@app.route("/auth/google/callback")
def google_callback():
    try:
        if "error" in request.args:
            return redirect(FRONTEND_REDIRECT_BASE)

        token = oauth.google.authorize_access_token()
        nonce = session.pop("oauth_nonce", None)
        user_info = oauth.google.parse_id_token(token, nonce=nonce)
        email = user_info["email"]

        # Debug log for troubleshooting Google login state
        print(f"[Google Login] Email: {email}")

        session.clear()
        session["user_email"] = email
        session["login_method"] = "google"
        session["google_name"] = user_info.get("name", email.split("@")[0])

        profiles = load_json(USER_PROFILE_FILE, {})
        user_data = find_user(email)
        is_new = email not in profiles and not (user_data and user_data.get("password"))

        print(f"[Google Login] is_new: {is_new}")

        if is_new:
            return redirect(f"{FRONTEND_REDIRECT_BASE}MenuMate_Registration_Page_Main.html?email={email}&fromGoogle=true")

        return redirect(FRONTEND_REDIRECT_BASE + "POC_Logging_info.html")
    except OAuthError:
        return redirect(FRONTEND_REDIRECT_BASE)

@app.route("/api/user")
def get_user():
    email = get_logged_in_email()
    if not email:
        return jsonify({"logged_in": False}), 200

    profiles = load_json(USER_PROFILE_FILE, {})
    profile = profiles.get(email)

    if profile:
        name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
    else:
        name = session.get("google_name", email.split("@")[0])

    return jsonify({
        "logged_in": True,
        "email": email,
        "display_name": name
    }), 200

@app.route("/logout")
def logout():
    session.clear()
    return redirect(FRONTEND_REDIRECT_BASE)

# Experience
@app.route("/api/experience", methods=["POST"])
def save_experience():
    email, err, status = ensure_logged_in()
    if err: return jsonify(err), status
    data = request.get_json()
    all_data = load_json(USER_EXPERIENCE_FILE, {})
    all_data[email] = {"experience": data, "last_updated": int(time.time())}
    save_json(USER_EXPERIENCE_FILE, all_data)
    return jsonify({"message": "Experience saved."}), 200

@app.route("/api/experience/get")
def get_experience():
    email, err, status = ensure_logged_in()
    if err: return jsonify(err), status
    all_data = load_json(USER_EXPERIENCE_FILE, {})
    entry = all_data.get(email)
    return jsonify(entry["experience"] if entry else {}), 200

# Sharing
@app.route("/api/shared_experiences")
def get_shared_experiences():
    email = get_logged_in_email()
    shared = load_json(SHARED_EXPERIENCE_FILE, {})
    return jsonify(shared.get(email, []))

@app.route("/api/shared/delete_one", methods=["POST"])
def delete_one_shared():
    email, err, status = ensure_logged_in()
    if err: return jsonify(err), status
    data = request.get_json()
    shared = load_json(SHARED_EXPERIENCE_FILE, {})
    shared[email] = [e for e in shared.get(email, []) if e.get("email") != data.get("email")]
    save_json(SHARED_EXPERIENCE_FILE, shared)
    return jsonify({"message": "Deleted one experience"}), 200

@app.route("/api/shared/star", methods=["POST"])
def toggle_star():
    email, err, status = ensure_logged_in()
    if err: return jsonify(err), status
    data = request.get_json()
    shared = load_json(SHARED_EXPERIENCE_FILE, {})
    for exp in shared.get(email, []):
        if exp.get("email") == data.get("email"):
            exp["starred"] = not exp.get("starred", False)
            break
    save_json(SHARED_EXPERIENCE_FILE, shared)
    return jsonify({"message": "Toggled starred"}), 200

@app.route("/api/track_location", methods=["POST"])
def track_location():
    email, profile = get_user_profile()
    if not email or not profile.get("experience_pass"):
        return jsonify({"message": "ExperiencePass not opted in or unauthorized."}), 200

    data = request.get_json()
    try:
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
    except (TypeError, ValueError):
        return jsonify({"message": "Invalid coordinates"}), 400

    if not redis_client:
        return jsonify({"message": "Redis not available on server."}), 500

    try:
        redis_client.execute_command("GEOADD", GEO_KEY, lon, lat, email)
        redis_client.expire(GEO_KEY, 300)

        nearby_users = redis_client.georadius(GEO_KEY, lon, lat, 1, unit='km')
        experiences = load_json(USER_EXPERIENCE_FILE, {})
        shared = load_json(SHARED_EXPERIENCE_FILE, {})
        sender_experience = experiences.get(email)
        if not sender_experience:
            return jsonify({"message": "Location updated (no experience)."}), 200

        for receiver in nearby_users:
            if receiver == email:
                continue
            receiver_profile = load_json(USER_PROFILE_FILE, {}).get(receiver, {})
            if not receiver_profile.get("experience_pass"):
                continue
            shared.setdefault(receiver, [])
            if any(e.get("email") == email for e in shared[receiver]):
                continue
            if len(shared[receiver]) >= 10:
                for i, exp in enumerate(shared[receiver]):
                    if not exp.get("starred"):
                        shared[receiver].pop(i)
                        break
                else:
                    continue
            shared[receiver].append({**sender_experience["experience"], "email": email, "starred": False})

        save_json(SHARED_EXPERIENCE_FILE, shared)
        return jsonify({"message": "Location updated and nearby sharing checked."}), 200
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({"message": "Internal server error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

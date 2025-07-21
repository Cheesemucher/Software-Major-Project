from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response
from flask_sqlalchemy import SQLAlchemy
import traceback # Temorary debugging exception message tool, not necessary for actual functionality
import secrets
import re
import json
from utils.auth import *
from data import db, User, lookup_user_by_email, Build
from utils.shapes import *
from utils.builds import *
from utils.blackjack import * # Import blackjack functions to use in the blackjack game
from utils.reccomender import *
from datetime import timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(16)  # Create session token cookie for session management by default (thank you Flask)
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XXS and JS from accessing the session cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  # Helps prevent CSRF attacks from other sites
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Set session lifetime to 30 mins of inactivity


# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per hour"],  # Set default rate limits
)


# Initialize databases
db.init_app(app)
#migrate.init_app(app, db)

# Create tables if they don't exist
with app.app_context():
    db.create_all()


# Store placed shapes in session (convert to proper caching strategy later)
def get_placed_shapes():
    if 'placed_shapes' not in session:
        session['placed_shapes'] = []
    return session['placed_shapes']

def add_placed_shape(shape_data):
    shapes = get_placed_shapes()
    shapes.append(shape_data)
    session['placed_shapes'] = shapes

def clear_shapes():
    session['placed_shapes'] = []


# Verify CSRF token before all api requests
@app.before_request
def csrf_protect():
    exempt_routes = ['/register', '/login'] # Routes to not check for CSRF tokens in (namely the ones that are run before CSRF token is generated as the user logs in)

    if request.method in ['POST', 'PUT', 'DELETE'] and request.path not in exempt_routes:
        CSRF_token = request.headers.get('X-CSRF-Token')
        if not CSRF_token or CSRF_token != session.get('csrf_token'):
            return jsonify({'success': False, 'message': 'CSRF token missing or invalid'}), 403


# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self';"
    return response



# Override default error handler for 429 (rate limit exceeded)
@app.errorhandler(429)
def ratelimit_handler(e):
    return {"error": "Rate limit exceeded. Try again later."}, 429


# Routes
@app.route("/") # Immediately redirect to login from root
def home():
    return redirect(url_for("login"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # Serve the registration HTML template
        return render_template('Register.html')

    # POST: handle registration. Expect JSON or fallback to form data.
    try:
        # Parse JSON data
        data = request.get_json()
        if data is None:
            # JSON parse failed or no JSON sent
            return jsonify({'success': False, 'message': 'Invalid JSON payload.'}), 400
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Normalize email
        normalized_email = email.strip().lower()

        status, message, code = register_user(normalized_email, password)

        if status == "failure":
            return jsonify({'success': False, 'message': message}), code

        # Success
        next_url = url_for('login')
        return jsonify({'success': True, 'next_url': next_url}), code

    except Exception as e:

        app.logger.error("Exception in /register: %s", e)
        traceback.print_exc()  # Use traceback to log issue with more detail

        app.logger.error("Request content-type: %s, data: %s", request.content_type, request.get_data())
        return jsonify({'success': False, 'message': 'Server error. Please try again.'}), 500

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute") # Limit login attempts to 5 per minute to prevent brute force attacks
def login():
    if request.method == 'GET':
        session.clear()
        return render_template('Login.html')

    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        status, result, code = login_user(email, password)

        if status == "failure":
            return jsonify({'success': False, 'message': result}), code

        # Establish session on success
        user = result
        session.clear()
        session.permanent = True
        session['user_id'] = user.id
        session['csrf_token'] = str(user.id) + str(secrets.token_hex(32))

        next_url = url_for('saves')
        response = make_response(jsonify({'success': True, 'next_url': next_url}))
        response.set_cookie('csrf_token', session['csrf_token'], httponly=False, secure=False, samesite='Strict')
        return response

    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Server error. Please try again.'}), 500


@app.route('/logout', methods=['POST'])
def logout():
    session.clear() # Clear the session data on logout
    return redirect(url_for("login"))

@app.route("/build", methods=["GET"])
def build():
    build_id = request.args.get("id") # Forwards the build ID through the redirect request, which this retrieves    
    session['current_build_ID'] = build_id # Store the current build ID in the session to enable selection of what build to work on

    return render_template("Build.html") 

@app.route("/saves")
def saves():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    builds = Build.query.filter_by(linked_user_id=user_id).all()
    return render_template("Save.html", user_builds=builds)

@app.route("/selected-build", methods=["POST"])
def selected_build():
    try:
        user_id = session.get("user_id")
        build_id = session.get("current_build_ID")
        if not user_id or not build_id:
            return jsonify({"success": False, "message": "Session data missing"}), 400

        build_data = get_selected_build_data(user_id, build_id)
        return jsonify({"success": True, **build_data})

    except Exception:
        return jsonify({"success": False, "message": "Server error"}), 500
    
@app.route("/get-current-bID", methods=["GET"])
def getBID():
    current_build_ID = session.get("current_build_ID")
    if not current_build_ID:
        return jsonify({"success": False, "message": "No build selected"}), 404
    return jsonify({"success": True, "build_id": current_build_ID}), 200


@app.route("/place-shape", methods=["POST"])
def place_shape():
    data = request.get_json()
    existing_shapes = get_placed_shapes()
    
    new_shape_data = handle_place_shape_request(data, existing_shapes)

    # Add it to the session array for caching purposes
    if new_shape_data["placed"]:
        add_placed_shape(new_shape_data["placed"][0])
    
    return jsonify(handle_place_shape_request(data, existing_shapes))


@app.route("/store-settings", methods=["POST"])
def store():
    try:
        user_id = session.get("user_id")
        data = request.get_json()
        if not user_id or not data:
            return jsonify({"success": False, "message": "Missing session or data"}), 400

        store_visual_preferences(user_id, data)
        return jsonify({"success": True})

    except Exception:
        return jsonify({"success": False, "message": "Server error"}), 500


@app.route("/create-build", methods=["POST"])
def create():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Not logged in."}), 403

    try:
        data = request.get_json()
        build_name = data.get("build_name", "Untitled Build")
        generation_data = data.get("generation_data", {})

        build = create_new_build(user_id, build_name, generation_data)
        return jsonify({"success": True, "build_id": build.id}), 200

    except Exception:
        return jsonify({"success": False, "message": "Failed to save build."}), 500


@app.route("/save-build", methods=["POST"])
def save_build():
    try:
        user_id = session.get("user_id")
        build_id = session.get("current_build_ID")
        data = request.get_json()

        if not user_id or not build_id or not data:
            return jsonify({"success": False, "message": "Missing session or data"}), 400

        update_existing_build(user_id, build_id, data["generation_data"])
        return jsonify({"success": True})

    except Exception:
        return jsonify({"success": False, "message": "Server error"}), 500


@app.route("/rename-build/<int:build_id>", methods=["POST"])
def rename_build(build_id):
    user_id = session.get("user_id")
    data = request.get_json()
    new_name = data.get("name", "")

    status, new_name = plain_text_processing(new_name)
    if status == "failure":
        return new_name, 400

    if not user_id or not new_name:
        return jsonify({"success": False, "message": "Invalid request"}), 400

    rename_existing_build(user_id, build_id, new_name)
    return jsonify({"success": True})


@app.route('/update-description/<int:build_id>', methods=['POST'])
def update_description(build_id):
    user_id = session.get("user_id")
    data = request.get_json()
    new_desc = data.get("description", "")

    status, new_desc = plain_text_processing(new_desc)
    if status == "failure":
        return new_desc, 400

    if not user_id or not new_desc:
        return jsonify({"success": False, "message": "Invalid request"}), 400

    update_build_description(user_id, build_id, new_desc)
    return jsonify(success=True)


@app.route('/delete-build/<int:build_id>', methods=['POST'])
def delete_build(build_id):
    user_id = session.get("user_id")
    delete_user_build(user_id, build_id)
    return jsonify(success=True)


@app.route("/copy-build", methods=["POST"])
def copy_build():
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Not logged in"}), 401

        data = request.get_json()
        text = data.get("name", "")
        generation_data = data.get("generation_data", {})
        copy_user_build(user_id, text, generation_data)
        return jsonify({"success": True}), 200

    except Exception:
        return jsonify({"success": False, "message": "Server error"}), 500


@app.route("/get-player-balance", methods=["GET"])
def get_balance():
    try:
        user_id = session.get("user_id")
        balance = get_user_balance(user_id)
        return jsonify({"success": True, "balance": balance}), 200

    except Exception:
        return jsonify({"success": False, "message": "Server error"}), 500
    
@app.route("/blackjack")
def blackjack():
    return render_template("Blackjack.html")


@app.route("/update-player-balance", methods=["POST"])
def update_balance():
    try:
        data = request.get_json()
        new_bal = data.get("new_balance")
        user_id = session.get("user_id")
        update_user_balance(user_id, new_bal)
        return jsonify({"success": True}), 200

    except Exception:
        return jsonify({"success": False, "message": "Server error"}), 500


@app.route("/blackjack/resolve-game", methods=["POST"])
def resolveGame():
    try:
        data = request.get_json()
        player_cards = data.get("playerHand", [])
        dealer_cards = data.get("dealerHand", [])

        result = resolve_blackjack_game(player_cards, dealer_cards)
        return jsonify({"success": True, **result}), 200

    except Exception:
        return jsonify({"success": False, "message": "Server error"}), 500


@app.route("/recs")
def recs():
    user_id = session.get("user_id")
    current_build_ID = session.get("current_build_ID")
    build = Build.query.filter_by(id=current_build_ID, linked_user_id=user_id).first()
    top_matches, relevant_builds = generate_build_recommendations(build.get_generation_data())
    return render_template("Recs.html", top_matches=top_matches, relevant_builds=relevant_builds)


if __name__ == "__main__":
    app.run(debug=False,port=5000)

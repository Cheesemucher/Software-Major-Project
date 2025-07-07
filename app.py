from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response
from flask_sqlalchemy import SQLAlchemy
import traceback # Temorary debugging exception message tool, not necessary for actual functionality
import secrets
import re
import json
#import hashlib using werkzeug instead as an experiemnt
from auth import login_processing, register_processing
from data import db, User, lookup_user_by_email, Build
from utils.shapes import (
    get_square_centre, get_triangle_centre,
    get_square_edge_positions, get_triangle_edge_positions,
    check_overlap, TILE_SIDE_LENGTH
)

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(16)  # Create session token cookie for session management by default (thank you Flask)
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XXS and JS from accessing the session cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  # Helps prevent CSRF attacks from other sites
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize databases
db.init_app(app)
#migrate.init_app(app, db)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# + Bonus: Look into adding/using Flask blueprints



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

def check_shape_overlap(new_shape, existing_shapes): # Need to adjust this upon creating a database
    """Check if a new shape would overlap with any existing shapes"""
    for shape in existing_shapes:
        if check_overlap(new_shape, shape):
            return False # Should be set to true to prevent overlap, disabled for testing purposes
    return False 


# Verify CSRF token before all api requests
@app.before_request
def csrf_protect():
    exempt_routes = ['/register', '/login'] # Routes to not check for CSRF tokens in (namely the ones that are run before CSRF token is generated as the user logs in)

    if request.method in ['POST', 'PUT', 'DELETE'] and request.path not in exempt_routes:
        CSRF_token = request.headers.get('X-CSRF-Token')
        if not CSRF_token or CSRF_token != session.get('csrf_token'):
            return jsonify({'success': False, 'message': 'CSRF token missing or invalid'}), 403


# Routes
@app.route("/") # Immediately redirect to login from root
def home():
    return redirect(url_for("register"))

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

        # Input validation and sanitisation
        status, result, code = register_processing(email, password)
        if status == "failure":
            return result, code
        else:
            email, password = result
            print("Result:", code) # Prints "Yippee"
        
        # Normalize email
        normalized_email = email.strip().lower()

        # Check existing
        existing = User.query.filter_by(email=normalized_email).first()
        if existing:
            return jsonify({'success': False, 'message': 'Email already registered.'}), 409

        # Create user
        user = User(email=normalized_email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Success
        next_url = url_for('login')
        return jsonify({'success': True, 'next_url': next_url}), 201

    except Exception as e:

        app.logger.error("Exception in /register: %s", e)
        traceback.print_exc()  # Use traceback to log issue with more detail

        app.logger.error("Request content-type: %s, data: %s", request.content_type, request.get_data())
        return jsonify({'success': False, 'message': 'Server error. Please try again.'}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        session.clear()  # Clear session on GET as this happens during a logout
        return render_template('Login.html')

    # POST
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')

         # Input validation and sanitisation
        status, result, code = login_processing(email, password)
        if status == "failure":
            return result, code
        else:
            email, password = result
            print("Result:", code) # Prints "Yippee"

        user = lookup_user_by_email(email)

        if not user:
            print("user not found")
            return jsonify({'success': False, 'message': 'User not found.'}), 401
        
        elif not user.check_password(password):
            print("wrong password")
            return jsonify({'success': False, 'message': 'Invalid credentials.'}), 401

        # Establish session on success
        session.clear()
        session['user_id'] = user.id # Store the current user ID in the session for later use to check who this is when loading builds
        session['csrf_token'] = str(user.id) + str(secrets.token_hex(32))

        next_url = url_for('saves') # Redirect to the saves page after login

        response = make_response(jsonify({'success': True, 'next_url': next_url}))
        response.set_cookie('csrf_token', session['csrf_token'], httponly=False, secure=False, samesite='Strict') # Idk if secure should be set to true or false
        return response

    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error. Please try again.'}), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.clear() # Clear the session data on logout
    return redirect(url_for("login"))

@app.route("/build", methods=["GET"])
def build():
    build_id = request.args.get("id") # Forwards the build ID through the redirect request, which this retrieves    
    session['current_build_ID'] = build_id # Store the current build ID in the session to enable selection of what build to work on
    
    print("picked build", build_id)

    return render_template("Build.html") 


@app.route("/selected-build", methods=["POST"]) # TODO fetch this info from a function on build.js that runs when that page is loaded. The build data returned should just be whatever is set as the selected build in the session by the 'load build' stuff which means you will also have to remove the build page as a selectable page instead making it accessible only throguh loading a build.
def selected_build(): 
    try:
        user_id = session.get("user_id")
        print("Current user logged in: ", user_id)
        build_id = session.get("current_build_ID")
        print("Current build ID:", build_id)

        if not user_id or not build_id:
            return jsonify({"success": False, "message": "Session data missing"}), 400

        build = Build.query.filter_by(id=build_id, linked_user_id=user_id).first()
        if not build:
            return jsonify({"success": False, "message": "Build not found"}), 404

        print("Selected build:", build_id)
        print("Raw encrypted data:", build.generation_data)
        print("Build generation data:", build.get_generation_data())

        return jsonify({
        "success": True,
        "generation_data": json.loads(build.get_generation_data()) # Encode it into a dict as it needs to be that way to be used by the frontend
        })


    except Exception as e:
        print("Error retrieving build:", e)
        return jsonify({"success": False, "message": "Server error"}), 500




@app.route("/create-build", methods=["POST"])
def create():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Not logged in."}), 403

    try:
        data = request.get_json()
        build_name = data.get("build_name", "Untitled Build")
        generation_data = json.dumps(data.get("generation_data", {})) # Convert dictionary data to JSON string for storage

        new_build = Build(build_name=build_name, generation_data=None, linked_user_id=user_id) # Set generation data with setter to default to encryption
        new_build.set_generation_data(generation_data)  # Encrypt and set generation data

        db.session.add(new_build)
        db.session.commit()

        return jsonify({"success": True, "build_id": new_build.id}), 200

    except Exception as e:
        print("Error saving build:", e)
        return jsonify({"success": False, "message": "Failed to save build."}), 500

@app.route("/save-build", methods=["POST"])
def save_build():
    try:
        user_id = session.get("user_id")
        build_id = session.get("current_build_ID")
        data = request.get_json()

        if not user_id or not build_id or not data:
            return jsonify({"success": False, "message": "Missing session or data"}), 400

        build = Build.query.filter_by(id=build_id, linked_user_id=user_id).first()
        if not build:
            return jsonify({"success": False, "message": "Build not found"}), 404

        # Update and save
        generation_data = json.dumps(data["generation_data"])
        build.set_generation_data(data=generation_data)  # Encrypt and set generation data
        db.session.commit()

        return jsonify({"success": True})

    except Exception as e:
        print("Error saving build:", e)
        return jsonify({"success": False, "message": "Server error"}), 500



@app.route("/place-shape", methods=["POST"]) # Calculate and store location of placed shape
def place_shape():
    data = request.get_json()
    shape_type = data.get("type")
    side_length = data.get("size")
    x = data.get("x")
    y = data.get("y")
    rotation = data.get("rotation")


    new_plus_signs = []

    if shape_type == "square":
        centre = get_square_centre(x, y, rotation)
        new_plus_signs = get_square_edge_positions(centre, rotation)



    elif shape_type == "triangle":
        centre = get_triangle_centre(x, y, rotation)
        new_plus_signs = get_triangle_edge_positions(centre, rotation)
    else:
        return jsonify({"error": "Invalid shape type", "placed": [], "plus_points": []})

    # Check if this shape would overlap with existing shapes
    new_shape = {"x": centre["x"], "y": centre["y"], "type": shape_type, "rotation": rotation}
    existing_shapes = get_placed_shapes()
    
    
    if check_shape_overlap(new_shape, existing_shapes):
        # Shape would overlap - don't place it
        return jsonify({
            "error": "Shape would overlap with existing shapes",
            "placed": [],
            "plus_points": []
        })
    
    # Add the shape to the build session tracking array -> Make this permanantly stored in a database later
    add_placed_shape(new_shape)
    
    # Filter plus signs - remove any that would cause overlaps
    filtered_plus_signs = []
    for plus_sign in new_plus_signs:
        # Check if placing a square at this plus sign would overlap
        potential_square = get_square_centre(plus_sign["x"], plus_sign["y"], plus_sign["rotation"])
        potential_square["type"] = "square"
        
        # Check if placing a triangle at this plus sign would overlap
        potential_triangle = get_triangle_centre(plus_sign["x"], plus_sign["y"], plus_sign["rotation"])
        potential_triangle["type"] = "triangle"
        
        # Only include plus sign if at least one shape type can be placed without overlap
        square_overlaps = check_shape_overlap(potential_square, existing_shapes)
        triangle_overlaps = check_shape_overlap(potential_triangle, existing_shapes)
        
        if not square_overlaps or not triangle_overlaps:
            filtered_plus_signs.append(plus_sign)
    
    return jsonify({
        "placed": [new_shape],
        "plus_points": filtered_plus_signs
    })


@app.route("/saves")
def saves():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    builds = Build.query.filter_by(linked_user_id=user_id).all()
    return render_template("Save.html", user_builds=builds)

@app.route("/rename-build/<int:build_id>", methods=["POST"]) # Rename a build functionality
def rename_build(build_id):
    user_id = session.get("user_id")
    data = request.get_json()
    new_name = data.get("name", "").strip()

    if not user_id or not new_name:
        return jsonify({"success": False, "message": "Invalid request"}), 400

    build = Build.query.filter_by(id=build_id, linked_user_id=user_id).first()
    if not build:
        return jsonify({"success": False, "message": "Build not found"}), 404

    build.build_name = new_name
    db.session.commit()
    return jsonify({"success": True})



@app.route("/recs")
def recs():
    return render_template("Recs.html")

@app.route("/blackjack")
def blackjack():
    return render_template("Blackjack.html")

if __name__ == "__main__":
    app.run(debug=True,port=5000)

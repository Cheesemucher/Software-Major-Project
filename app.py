from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import traceback # Temorary debugging exception message tool, not necessary for actual functionality
import secrets
import re
import json
#import hashlib using werkzeug instead as an experiemnt
from data import db, User, migrate, lookup_user_by_email, Build
from utils.shapes import (
    get_square_centre, get_triangle_centre,
    get_square_edge_positions, get_triangle_edge_positions,
    check_overlap, TILE_SIDE_LENGTH
)

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(16)  # For session management
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize databases
db.init_app(app)
#migrate.init_app(app, db)

# Create tables if they don't exist (development use only - poses security risks by printing this information)
with app.app_context():
    db.create_all()

with app.app_context():
    # Try querying to test stuff
    try:
        users = User.query.all()
        builds = Build.query.all()
        print("Queried users, table exists. Count:", len(users))
        print("Queried builds, table exists. Count:", len(builds)) 
    except Exception as e:
        print("Error querying User:", e)

# + Bonus: Look into adding/using Flask blueprints


# Regex pattern to validate plaintext inputs
PATTERN = re.compile(r'^[a-zA-Z0-9_]+$')

# Regex pattern to validate email
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9_]+@+.')

# Regex pattern to validate password
PASSWORD_PATTERN = re.compile(r'^[a-zA-Z0-9_]')


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
        # Parse JSON or form data
        if request.is_json:
            data = request.get_json()
            if data is None:
                # JSON parse failed or no JSON sent
                return jsonify({'success': False, 'message': 'Invalid JSON payload.'}), 400
            email = data.get('email', '').strip()
            password = data.get('password', '')
        else:
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')

        # Input sanitisation
        email = re.escape(email)
        password = re.escape(password)

        # Input validation
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required.'}), 400
        if len(email) > 255:
            return jsonify({'success': False, 'message': 'Email cannot have over 255 characters'}), 400
        if len(password) < 8:
            return jsonify({'success': False, 'message': 'Password should have at least 8 characters'}), 400
        if password == password.lower() or password == password.upper():
            return jsonify({'success': False, 'message': 'Password must contain at least 1 uppercase and 1 lowercase letter'}), 400
        if not PASSWORD_PATTERN.match(password):
            return jsonify({'success': False,'message': 'Invalid password format.'}), 400
        if not EMAIL_PATTERN.match(email):
            return jsonify({'success': False, 'message': 'Invalid email format.'}), 400

        # Check existing
        existing = User.query.filter_by(email=email).first()
        if existing:
            return jsonify({'success': False, 'message': 'Email already registered.'}), 409

        # Create user
        user = User(email=email)
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

    # Auto-login on registration, add this properly when sessions and user stuff works
    session.clear()
    session['user_id'] = user.id
    next_url = url_for('build')

    return jsonify({'success': True, 'next_url': next_url}), 201

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('Login.html')

    # POST
    try:
        if request.is_json:
            data = request.get_json()
            email = data.get('email', '').strip()
            password = data.get('password', '')
        else:
            # fallback for form-encoded if JS fails or if someone POSTs directly
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            print("fallback used") 

        # Input sanitisation
        email = re.escape(email)
        password = re.escape(password)

        # Input validation
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required.'}), 400
        if len(email) > 255:
            return jsonify({'success': False, 'message': 'Email cannot have over 255 characters'}), 400
        if len(password) > 255:
            return jsonify({'success': False, 'message': 'Password cannot have over 255 characters'}), 400
        if not PASSWORD_PATTERN.match(password):
            return jsonify({'success': False,'message': 'Invalid password format.'}), 400
        if not EMAIL_PATTERN.match(email):
            return jsonify({'success': False, 'message': 'Invalid email format.'}), 400
        #TODO add the werkzeug security default validation as well

        user = lookup_user_by_email(email)

        if not user:
            print("user not found")
            return jsonify({'success': False, 'message': 'User not found.'}), 401
        
        elif not user.check_password(password):
            return jsonify({'success': False, 'message': 'Invalid credentials.'}), 401

        # Establish session on success
        session.clear()
        session['user_id'] = user.id

        next_url = url_for('build')  # Send them on their way
        return jsonify({'success': True, 'next_url': next_url}), 200

    except Exception as e:
        # Log exception for debugging only, remove for 'production' to not expose sensitive details in error messages
        app.logger.exception("Unhandled exception in /login")
        return jsonify({'success': False, 'message': 'Server error. Please try again.'}), 500


@app.route("/build", methods=["GET"])
def build():
    build_id = request.args.get("id") # Forwards the build ID through the redirect request, which this retrieves    
    session['current_build_ID'] = build_id # Store the current build ID in the session to enable selection of what build to work on

    return render_template("Build.html") # Send the requested build to load to the frontend. TODO Encrypt generation data in the Build model 


@app.route("/selected-build", methods=["POST"]) # TODO fetch this info from a function on build.js that runs when that page is loaded. The build data returned should just be whatever is set as the selected build in the session by the 'load build' stuff which means you will also have to remove the build page as a selectable page instead making it accessible only throguh loading a build.
def selected_build(): 
    try:
        user_id = session.get("user_id")
        build_id = session.get("current_build_ID")

        if not user_id or not build_id:
            return jsonify({"success": False, "message": "Session data missing"}), 400

        build = Build.query.filter_by(id=build_id, linked_user_id=user_id).first()
        if not build:
            return jsonify({"success": False, "message": "Build not found"}), 404

        return jsonify({
        "success": True,
        "generation_data": json.loads(build.generation_data) # Encode it into a dict as it needs to be that way to be used by the frontend
        })


    except Exception as e:
        print("Error retrieving session data:", e) # get rid of this later TODO
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

        new_build = Build(build_name=build_name, generation_data=generation_data, linked_user_id=user_id)
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
        build.generation_data = json.dumps(data["generation_data"])
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

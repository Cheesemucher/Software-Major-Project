from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import traceback # Temorary debugging exception message tool, not necessary for actual functionality
import secrets
import re
#import hashlib using werkzeug instead as an experiemnt
from data import db, User, migrate, lookup_user_by_email
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

# Create tables if they don't exist (development use only)
with app.app_context():
    db.create_all()

with app.app_context():
    # Try querying
    try:
        users = User.query.all()
        print("Queried users, table exists. Count:", len(users))
    except Exception as e:
        print("Error querying User:", e)

# + Bonus: Look into adding/using Flask blueprints

# Store placed shapes in session (use a database later on)
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
            return False # Turned this off for testing it was annoying, this line should "return True"
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

        # Basic validation
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required.'}), 400

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
            print(email, password) # For debugging, make sure it makes it to the Flask
        else:
            # fallback for form-encoded if JS fails or if someone POSTs directly
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            print("fallback") 

        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required.'}), 400


        user = lookup_user_by_email(email)

        if not user:
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


@app.route("/build")
def build():
    # Clear shapes when loading the build page
    clear_shapes()
    return render_template("Build.html")

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
    
    # Add the shape to our tracking
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
        "placed": [{
            "x": centre["x"], 
            "y": centre["y"], 
            "type": shape_type, 
            "rotation": rotation
        }],
        "plus_points": filtered_plus_signs
    })


@app.route("/saves")
def saves():
    return render_template("Save.html")

@app.route("/recs")
def recs():
    return render_template("Recs.html")

@app.route("/blackjack")
def blackjack():
    return render_template("Blackjack.html")

if __name__ == "__main__":
    app.run(debug=True,port=5000)

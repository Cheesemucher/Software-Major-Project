from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from data import db, User
from auth import user_auth_register # apparently the star is evil, change this to import each individual function later
from asyncio import *
import math
import secrets
from utils.shapes import (
    get_square_centre, get_triangle_centre,
    get_square_edge_positions, get_triangle_edge_positions,
    check_overlap, TILE_SIDE_LENGTH
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example_test_db.db'
db.init_app(app)
app.secret_key = secrets.token_hex(16)  # For session management
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XXS and JS 
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  # Helps prevent CSRF attacks from different sites

# Store placed shapes in session (in production, use a database)
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

# Helper function to check for shape overlap, could maybe move to the db helper functions file since it needs to read information from there or at least abstract this function
def check_shape_overlap(new_shape, existing_shapes): # Need to adjust this upon creating a database
    """Check if a new shape would overlap with any existing shapes"""
    for shape in existing_shapes:
        if check_overlap(new_shape, shape):
            return False # Turned this off for testing it was annoying, this line should "return True"
    return False 


# Routes
@app.route("/") # Immediately redirect to login from root
def home():
    return render_template("Login.html")


@app.route("/login", methods=["GET", "POST"])
def login(): #HTTP route to log in a user.
    # Retrieving input
    email = request.form.get('email')
    password = request.form.get('password')


    print(f"email:{email}, password:{password}")
    try:
        # Generating session/CSRF token and passing them to frontend
        session_token, csrf_token = user_auth_register(email, password) # make this an await later it doesnt work rn for some reason
        '''return jsonify({"message": "User registered successfully", 
                        "session_token": session_token, 
                        "csrf_token": csrf_token}), 201''' #put this back when tokens are put in
        return render_template("Build.html")
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": str(e)}), 406

    

@app.route("/register", methods=["POST"])
def register():
    pass

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

    with app.app_context():
        db.create_all()
        app.run()

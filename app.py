from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import secrets
import hashlib
from utils.shapes import (
    get_square_centre, get_triangle_centre,
    get_square_edge_positions, get_triangle_edge_positions,
    check_overlap, TILE_SIDE_LENGTH
)
from data import User

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(16)  # For session management
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#Temporary puttingthis here to see ifthe code works.
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.integer, primary_key=True)
    email = db.Column(db.String(200), nullable = False)
    password = db.Column(db.String(200), nullable = False)

    def __init__(self, email, password):
        self.email = email
        self.password = self.__hash_password(password)

    def __hash_password(password):
        return hashlib.sha256(password.encode('ascii')).hexdigest()

    def __check_password(self,password):
        return hashlib.sha256(password.encode('ascii')).hexdigest() == self.password
    

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

def check_shape_overlap(new_shape, existing_shapes): # Need to adjust this upon creating a database
    """Check if a new shape would overlap with any existing shapes"""
    for shape in existing_shapes:
        if check_overlap(new_shape, shape):
            return False # Turned this off for testing it was annoying, this line should "return True"
    return False 


# Routes
@app.route("/") # Immediately redirect to login from root
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST": # Temporary login functionality to get past the login page
        form = request.form
        new_user = User(form.email, form.password)
        db.session.add(new_user)
        db.session.commit()
        return "Registered yippee"

    return render_template("Login.html")

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

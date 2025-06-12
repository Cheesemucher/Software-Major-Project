from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_wtf.csrf import CSRFProtect
from data import db, User
from auth import user_auth_register, user_auth_login, user_auth_logout, user_auth_validate_token
from forms import LoginForm, RegisterForm
from config import Config
import math
from utils.shapes import (
    get_square_centre, get_triangle_centre,
    get_square_edge_positions, get_triangle_edge_positions,
    check_overlap, TILE_SIDE_LENGTH
)

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
csrf = CSRFProtect(app)

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
def check_shape_overlap(new_shape, existing_shapes):
    """Check if a new shape would overlap with any existing shapes"""
    for shape in existing_shapes:
        if check_overlap(new_shape, shape):
            return True
    return False 


# Routes
@app.route("/")
def home():
    return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
    
    try:
        # Attempt to log in the user
        session_token, csrf_token = user_auth_login(email, password)
        
        # Store tokens in session
        session['session_token'] = session_token
        session['csrf_token'] = csrf_token
        session['user_email'] = email
        
        # Redirect to build page on successful login
        return redirect(url_for('build'))
    
    except ValueError as e:
        # Handle validation errors
        return render_template("Login.html", error="Invalid email or password")
    except Exception as e:
        # Handle unexpected errors
        app.logger.error(f"Login error: {str(e)}")
        return render_template("Login.html", form=form, error="An error occurred. Please try again.")
    
    return render_template("Login.html", form=form)

    

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
    
    try:
        # Register the user
        session_token, csrf_token = user_auth_register(email, password)
        
        # Store tokens in session
        session['session_token'] = session_token
        session['csrf_token'] = csrf_token
        session['user_email'] = email
        
        # Redirect to build page on successful registration
        return redirect(url_for('build'))
    
    except ValueError as e:
        # Handle validation errors (email exists, weak password, etc.)
        error_message = str(e)
        if "already exists" in error_message.lower():
            error_message = "Email already exists"
        return render_template("Register.html", error=error_message)
    except Exception as e:
        # Handle unexpected errors
        app.logger.error(f"Registration error: {str(e)}")
        return render_template("Register.html", form=form, error="An error occurred. Please try again.")
    
    return render_template("Register.html", form=form)

@app.route("/logout")
def logout():
    # Get tokens from session
    session_token = session.get('session_token')
    csrf_token = session.get('csrf_token')
    
    # Logout user if tokens exist
    if session_token and csrf_token:
        try:
            user_auth_logout(session_token, csrf_token)
        except:
            pass  # Ignore errors during logout
    
    # Clear session
    session.clear()
    return redirect(url_for('login'))

@app.route("/build")
def build():
    # Check if user is logged in
    if 'session_token' not in session or 'csrf_token' not in session:
        return redirect(url_for('login'))
    
    # Validate tokens
    if not user_auth_validate_token(session['session_token'], session['csrf_token']):
        session.clear()
        return redirect(url_for('login'))
    
    # Clear shapes when loading the build page
    clear_shapes()
    return render_template("Build.html")

@app.route("/place-shape", methods=["POST"])
def place_shape():
    # Check if user is logged in
    if 'session_token' not in session or 'csrf_token' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Validate tokens
    if not user_auth_validate_token(session['session_token'], session['csrf_token']):
        session.clear()
        return jsonify({"error": "Unauthorized"}), 401
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
    # Check if user is logged in
    if 'session_token' not in session or 'csrf_token' not in session:
        return redirect(url_for('login'))
    
    # Validate tokens
    if not user_auth_validate_token(session['session_token'], session['csrf_token']):
        session.clear()
        return redirect(url_for('login'))
    
    return render_template("Save.html")

@app.route("/recs")
def recs():
    # Check if user is logged in
    if 'session_token' not in session or 'csrf_token' not in session:
        return redirect(url_for('login'))
    
    # Validate tokens
    if not user_auth_validate_token(session['session_token'], session['csrf_token']):
        session.clear()
        return redirect(url_for('login'))
    
    return render_template("Recs.html")

@app.route("/blackjack")
def blackjack():
    # Check if user is logged in
    if 'session_token' not in session or 'csrf_token' not in session:
        return redirect(url_for('login'))
    
    # Validate tokens
    if not user_auth_validate_token(session['session_token'], session['csrf_token']):
        session.clear()
        return redirect(url_for('login'))
    
    return render_template("Blackjack.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)

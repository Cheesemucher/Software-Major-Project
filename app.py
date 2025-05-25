from flask import Flask, render_template, request, redirect, url_for, jsonify
import math

app = Flask(__name__, template_folder="Frontend - HTML") # Link to template folder which has a funny name


# Routes
@app.route("/") # Immediately redirect to login from root
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST": # Temporary login functionality to get past the login page
        return render_template("Build.html")

    return render_template("Login.html")

@app.route("/build")
def build():
    return render_template("Build.html")

@app.route("/place-shape", methods=["POST"]) # Calculate and store location of placed shape
def place_shape():
    data = request.get_json()
    shape_type = data.get("type")
    side_length = data.get("size")
    x = data.get("x")
    y = data.get("y")
    rotation = data.get("rotation")

    print("Received shape:", shape_type, "at", x, y, "with rotation", rotation)

    new_plus_signs = [] # each sign should be in the format:  { "x": 0, "y": 200, "rotation": 0 } for example

    if shape_type == "square":
        # Find centre coordinates of where generated shape should be (assuming given coordinates of existing + is the base/bottom side)
        rotation_rad = rotation * math.pi / 180
        shiftX = side_length/2 * math.cos(rotation_rad) # Finds horizontal and vertical components of distance from midpoint on one side to the centre of the shape
        shiftY = side_length/2 * math.sin(rotation_rad)

        centre = {"x":x+shiftX, "y":y+shiftY} # Finds centre coords by shifting x and y values respectively to the centre

        # Find Midpoints of each side
        for k in range(4): # Iterate through an angle for each of the sides
            angle_to_point = rotation_rad + k * (math.pi/2) # Find an angle from the center to the midpoint based on rotation
            mX = centre["x"] + side_length/2 * math.sin(angle_to_point)
            mY = centre["y"] - side_length/2 * math.cos(angle_to_point) # y value needs subtracting as top left is 0 so adding makes it go down
            #if mY != y and mX != x: # Only add it to the list if it isnt the original + sign the user clicked on to generate the shape
            new_plus_signs.append({"x": mX, "y": mY, "rotation": angle_to_point * 180 / math.pi}) # Angle needs to be sent back in degrees tragic

            print(f"plus {k} angle: {angle_to_point} or {angle_to_point * 180 / math.pi} degrees")


    elif shape_type == "triangle": # Gonna have different maths for different shapes innit
        # Find centre coordinates of where generated shape should be
        height = math.sqrt(3)/2 * side_length
        dist_to_centre = height / 3  # oh yea medians of a triangle are concurrent

        rotation_rad = rotation * math.pi / 180
        shiftX = dist_to_centre * math.cos(rotation_rad) # How much you need to shift the coordinates to find the centre of where the generated shape will be
        shiftY = dist_to_centre * math.sin(rotation_rad) # Same but y-axis

        centre = {"x":x+shiftX, "y":y+shiftY}
        print(centre)

        # Find Midpoints of each side
        for k in range(3): # Same deal but with 3 sides
            angle_to_point = rotation_rad - math.pi/3 + k * (2*math.pi/3)
            mX = centre["x"] + side_length/2 * math.cos(angle_to_point)
            mY = centre["y"] + side_length/2 * math.sin(angle_to_point)
            new_plus_signs.append({"x": mX, "y": mY, "rotation": angle_to_point})

            #if mY != y and mX != x: 
            new_plus_signs.append({"x": mX, "y": mY, "rotation": angle_to_point * 180 / math.pi})

    else:
        print("Not supposed to be here bro")

    # Necessary output: information about shape to be placed and + signs to be generated
    return jsonify({
        "placed": [ # information about shape to be placed
            { "x": centre["x"], "y": centre["y"], "type": shape_type, "rotation": rotation} # eg: { "x": 0, "y": 0, "type": "square", "rotation": 90 }   
        ],
        "plus_points": new_plus_signs
        # location and rotations of plus signs to be generated
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
    app.run(debug=True,port=5001)

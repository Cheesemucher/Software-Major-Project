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
    origin = data.get("origin", {"x": 0, "y": 0})
    x, y = origin["x"], origin["y"]
    rotation = data.get("rotation")

    print("Received shape:", shape_type, "at", x, y)

    center = {"x": x, "y": y}

    # Necessary output: information about shape to be placed and + signs to be generated
    return jsonify({
        "placed": [ # information about shape to be placed
            { "x": center["x"], "y": center["y"], "type": shape_type, "rotation": rotation} # eg: { "x": 0, "y": 0, "type": "square", "rotation": 90 }   
        ],
        "plus_points": [ # location and rotations of plus signs to be generated
            { "x": x+1, "y": y, "rotation": 0 } # eg:  { "x": 0, "y": -1, "rotation": 0 }
        ]
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
    app.run(debug=True)

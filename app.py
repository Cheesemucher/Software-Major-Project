from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, template_folder="Frontend - HTML") # Specify template folder


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

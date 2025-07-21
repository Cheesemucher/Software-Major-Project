import re
import unicodedata
import json
import werkzeug.security
from data import db, User, lookup_user_by_email

# Regex pattern to validate plaintext inputs
TEXT_PATTERN = re.compile(r'^[\w\s.,!?()\[\]{}\n\r\'\"-]*$') # Allows alphanumeric characters, spaces, punctuation, and some special characters

# Regex pattern to validate email
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9_]+@+.')

# Regex pattern to validate password
PASSWORD_PATTERN = re.compile(r'^[a-zA-Z0-9_]')

def login_processing(email: str, password: str) -> tuple:
    email = re.escape(email)
    password = re.escape(password)

    if not email or not password:
        return "failure", "Email and password are required.", 400
    if len(email) > 255:
        return "failure", "Email cannot have over 255 characters.", 400
    if len(password) > 255:
        return "failure", "Password cannot have over 255 characters.", 400
    if not PASSWORD_PATTERN.match(password):
        return "failure", "Invalid password format.", 400
    if not EMAIL_PATTERN.match(email):
        return "failure", "Invalid email format.", 400

    return "success", [email, password], 200

def register_processing(email: str, password: str) -> tuple:
    email = re.escape(email)
    password = re.escape(password)

    if not email or not password:
        return "failure", "Email and password are required.", 400
    if len(email) > 255:
        return "failure", "Email cannot have over 255 characters.", 400
    if len(password) < 8:
        return "failure", "Password should have at least 8 characters.", 400
    if password == password.lower() or password == password.upper():
        return "failure", "Password must contain both uppercase and lowercase letters.", 400
    if not any(char.isdigit() for char in password):
        return "failure", "Password must contain at least 1 number.", 400
    if password.isalnum():
        return "failure", "Password must contain at least 1 special character.", 400
    if not PASSWORD_PATTERN.match(password):
        return "failure", "Invalid password format.", 400
    if not EMAIL_PATTERN.match(email):
        return "failure", "Invalid email format.", 400

    return "success", [email, password], 200

def plain_text_processing(text: str) -> tuple:
    if not text:
        return "failure", "Text is required.", 400
    if len(text) > 550:
        return "failure", "Text cannot have over 550 characters.", 400
    if not TEXT_PATTERN.fullmatch(text):
        return "failure", "Text contains invalid characters.", 400

    text = re.escape(text)
    return "success", text, 200

def register_user(email: str, password: str) -> tuple:
    status, result, code = register_processing(email, password)
    if status == "failure":
        return status, result, code
    email, password = result

    existing_user = lookup_user_by_email(email)
    if existing_user:
        return "failure", "User with this email already exists.", 409

    new_user = User(
        email=email,
        password_hash=None,
        visual_settings=json.dumps({ # Default tile settings
            "squareColour": "#e26a4a",
            "triangleColour": "#e26a4a",
            "deleteButtonColour": "#ff8400",
            "plusSize": "30",
            "deleteSize": "22"
        }),
        blackjack_balance=1000
    )
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return "success", "User registered successfully.", 201
    except Exception:
        db.session.rollback()
        return "failure", "Server error. Please try again.", 500

def login_user(email: str, password: str) -> tuple:
    status, result, code = login_processing(email, password)
    if status == "failure":
        return status, result, code
    email, password = result

    user = lookup_user_by_email(email)
    if not user:
        return "failure", "User not found.", 401
    if not user.check_password(password):
        return "failure", "Invalid credentials.", 401

    return "success", user, 200

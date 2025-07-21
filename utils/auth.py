import re
import unicodedata
from flask import jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import json
import werkzeug.security
import flask_wtf
from data import db, User, lookup_user_by_email 


# Regex pattern to validate plaintext inputs
TEXT_PATTERN = re.compile(r'^[\w\s.,!?()\[\]{}\n\r\'\"-]*$') # Allows alphanumeric characters, spaces, punctuation, and some special characters

# Regex pattern to validate email
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9_]+@+.')

# Regex pattern to validate password
PASSWORD_PATTERN = re.compile(r'^[a-zA-Z0-9_]')


def login_processing(email: str, password: str)->tuple:
    email = re.escape(email)
    password = re.escape(password)

    # Input validation
    if not email or not password:
        return "failure", jsonify({'success': False, 'message': 'Email and password are required.'}), 400
    if len(email) > 255:
        return "failure", jsonify({'success': False, 'message': 'Email cannot have over 255 characters'}), 400
    if len(password) > 255:
        return "failure", jsonify({'success': False, 'message': 'Password cannot have over 255 characters'}), 400
    if not PASSWORD_PATTERN.match(password):
        return "failure", jsonify({'success': False,'message': 'Invalid password format.'}), 400
    if not EMAIL_PATTERN.match(email):
        return "failure", jsonify({'success': False, 'message': 'Invalid email format.'}), 400

    return "success", [email, password], "Yippee"

def register_processing(email: str, password: str) -> tuple:
    # Input sanitisation
    email = re.escape(email)
    password = re.escape(password)

    # Input validation
    if not email or not password:
        return "failure", jsonify({'success': False, 'message': 'Email and password are required.'}), 400
    if len(email) > 255:
        return "failure", jsonify({'success': False, 'message': 'Email cannot have over 255 characters'}), 400
    if len(password) < 8:
        return "failure", jsonify({'success': False, 'message': 'Password should have at least 8 characters'}), 400
    if password == password.lower() or password == password.upper(): # Checks if password contains both uppercase and lowercase letters
        return "failure", jsonify({'success': False, 'message': 'Password must contain at least 1 uppercase and 1 lowercase letter'}), 400
    if not any(char.isdigit() for char in password): # Checks if password contains at least 1 number
        return "failure", jsonify({'success': False, 'message': 'Password must contain at least 1 number'}), 400
    if password.isalnum(): # Checks if password contains only alphanumeric characters
        return "failure", jsonify({'success': False, 'message': 'Password must contain at least 1 special character'}), 400
    if not PASSWORD_PATTERN.match(password):
        return "failure", jsonify({'success': False,'message': 'Invalid password format.'}), 400
    if not EMAIL_PATTERN.match(email):
        return "failure", jsonify({'success': False, 'message': 'Invalid email format.'}), 400

    return "success", [email, password], "Yippee"

def plain_text_processing(text: str) -> str:
    # Input validation
    if not text:
        return "failure", jsonify({'success': False, 'message': 'Text is required.'})
    if len(text) > 550:
        return "failure", jsonify({'success': False, 'message': 'Text cannot have over 550 characters'})
    if not TEXT_PATTERN.fullmatch(text):
        return "failure", jsonify({'success': False, 'message': 'Text contains invalid characters.'})

    text = re.escape(text)

    return "success", text


def register_user(email:str, password:str) -> tuple:
    # Input validation and sanitisation
    status, result, code = register_processing(email, password)
    if status == "failure":
        return status, code
    else:
        email, password = result
        print("Result:", code) # Prints "Yippee"

    
    # Check if user already exists
    existing_user = lookup_user_by_email(email)
    if existing_user:
        return "failure", {'message': 'User with this email already exists.'}, 400

    # Create new user
    new_user = User(email=email, password_hash=None, visual_settings=json.dumps({"squareColour": "#e26a4a", "triangleColour": "#e26a4a", "deleteButtonColour": "#ff8400", "plusSize": "30", "deleteSize": "22"}), blackjack_balance=1000)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()

        return "success", {'message': 'User registered successfully.'}, 201
    except Exception as e:
        db.session.rollback()
        return "failure", {'message': 'Server error. Please try again.'}, 500

def login_user(email: str, password: str) -> tuple:
     # Input validation and sanitisation
    status, result, code = login_processing(email, password)
    if status == "failure":
        return status, code
    else:
        email, password = result
        print("Result:", code) # Prints "Yippee"

    user = lookup_user_by_email(email)

    if not user:
        return "failure", {'message': 'User not found.'}, 401

    if not user.check_password(password):
        return "failure", {'message': 'Invalid credentials.'}, 401

    return "success", user, 200

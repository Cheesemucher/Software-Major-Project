import re
import unicodedata
from flask import jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import json
import werkzeug.security
import flask_wtf


# Regex pattern to validate plaintext inputs
TEXT_PATTERN = re.compile(r'^[a-zA-Z0-9_ .,!?-]+$')

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
    text = re.escape(text)

    # Input validation
    if not text:
        return "failure", jsonify({'success': False, 'message': 'Text is required.'})
    if len(text) > 550:
        return "failure", jsonify({'success': False, 'message': 'Text cannot have over 2550 characters'})
    stripped = text.strip()

    # Check for control characters (e.g., \x00, \x1B) rather than regex to preserve whitespace
    for char in stripped:
        if unicodedata.category(char)[0] == "C" and char not in ('\n', '\r'):
            return "failure", jsonify({'success': False, 'message': 'Text contains invalid characters'})

    return "success", text
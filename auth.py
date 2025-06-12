from flask import abort
from data import db, User


def user_auth_register(email, password):
    """Register user and generate session token and CSRF token"""
    email = email.lower()
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValueError("Email already exists")
    
    # Create new user
    new_user = User(email, password)
    db.session.add(new_user)
    db.session.commit()
    
    return new_user.session_token, new_user.csrf_token


def user_auth_login(email, password_input):
    """Log in user and generate session token and CSRF token"""
    email = email.lower()
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ValueError("Invalid email or password")
    
    # Verify password
    if not user.verify_password(password_input):
        raise ValueError("Invalid email or password")
    
    # Generate new tokens
    user.assign_tokens()
    
    return user.session_token, user.csrf_token


def user_auth_logout(session_token, csrf_token):
    """Log out the user with provided session token and CSRF token"""
    # Find user by session token
    user = User.query.filter_by(session_token=session_token).first()
    
    if user and user.validate_tokens(session_token, csrf_token):
        user.revoke_tokens()
        return
    
    raise ValueError("Invalid or expired tokens")


def user_auth_validate_token(session_token, csrf_token):
    """Validate whether session token and CSRF token exist and are valid"""
    # Find user by session token
    user = User.query.filter_by(session_token=session_token).first()
    
    if user and user.validate_tokens(session_token, csrf_token):
        return True
    
    return False
from flask import abort
from data import db, User
from asyncio import *


async def user_auth_register(email, password):
    """Registering user and generating session token and CSRF token"""
    email = email.lower()  # Normalize the email to lowercase
    if email in db:
        abort(400, description="Email already exists")
    new_user = User(email, password)
    
    db[email] = new_user  # Store the user object by email
    return new_user.session_token, new_user.csrf_token

async def user_auth_login(email, password_input):
    """Logging in user, and generating session token and CSRF token"""
    email = email.lower()  # Normalize the email to lowercase
    if email not in db:
        abort(401, description="Email does not exist")
    user = db[email]
    if not await user.verify_password(password_input):
        abort(401, description="Invalid password")

    user.assign_tokens()
    return user.session_token, user.csrf_token

async def user_auth_logout(session_token, csrf_token):
    """Logging out the user with provided session token and CSRF token"""
    for user in db.values():
        if await user.validate_tokens(session_token, csrf_token):
            await user.revoke_tokens()
            return
    abort(401, description="Token does not exist")

async def user_auth_validate_token(session_token, csrf_token):
    """Validating whether session token and CSRF token exist"""
    # Debugging email - session_token - csrf_token relationships
    for user in db.values():
        print(f'{user.email} is for {user.session_token} and {user.csrf_token}')

    for user in db.values():
        if await user.validate_tokens(session_token, csrf_token):
            print("Valid tokens")
            return True

    print("Invalid tokens")
    abort(401, description="Token does not exist")
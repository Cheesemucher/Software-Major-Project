from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate() # For database migration (idk what it is but it looked cool)

class User(db.Model): # Message for the teach: Followed a tutorial, if something is strange lmk
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


    def set_password(self, plain_password: str):
        # Use werkzeug.security to hash
        self.password_hash = generate_password_hash(plain_password, method='pbkdf2:sha256')

    def check_password(self, plain_password: str) -> bool:
        return check_password_hash(self.password_hash, plain_password)
    
# Helper functions for querying database:
def lookup_user_by_email(email):
    if not email:
        return None # Return none if email is not found in the database
    
    normalized_email = email.strip().lower()
    return User.query.filter_by(email=normalized_email).first()
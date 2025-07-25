from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet

db = SQLAlchemy()

key = b'ZpFP_-UuAaK6yU_Sdy5byX6Ax1PX3KQqJkTvuKpZlEA=' # Constant, hardcoded encryption key for testing pruposes (can be properly stored as an env key after the assignment is marked)
fernet = Fernet(key) # Encruption key for generation data

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    visual_settings = db.Column(db.String(255), nullable=True)
    blackjack_balance = db.Column(db.Integer, nullable=True)

    # Relationship to Build
    builds = db.relationship('Build', backref='user', lazy=True, cascade='all, delete-orphan') 


    def set_password(self, plain_password: str):
        # Use werkzeug.security to hash
        self.password_hash = generate_password_hash(plain_password, method='pbkdf2:sha256')

    def check_password(self, plain_password: str) -> bool:
        return check_password_hash(self.password_hash, plain_password)
    
    
    
# Helper functions for querying database:
def lookup_user_by_email(email):
    if not email:
        return None # Return none if no email was entered
    
    normalized_email = email.strip().lower()
    return User.query.filter_by(email=normalized_email).first()
    

# Stored builds database

class Build(db.Model):
    __tablename__ = 'builds'
    id = db.Column(db.Integer, primary_key=True)
    build_name = db.Column(db.String(255), nullable=False)
    build_description = db.Column(db.String(550), nullable=True)
    generation_data = db.Column(db.Text, nullable=False)
    linked_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def set_build_name(self, name: str):
        self.build_name = name

    def set_generation_data(self, data: str):
        self.generation_data = fernet.encrypt(data.encode())
    
    def get_generation_data(self) -> str:
        decrypted_data = fernet.decrypt(self.generation_data).decode()
        return decrypted_data
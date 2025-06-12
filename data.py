from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    session_token = db.Column(db.String(64), unique=True, nullable=True)
    csrf_token = db.Column(db.String(64), unique=True, nullable=True)

    def __init__(self, email, password):
        self.email = email.lower()
        self.set_password(password)
        self.assign_tokens()
    
    def set_password(self, password):
        """Hash and store password"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self, length=32):
        """Generate a secure random token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def assign_tokens(self):
        """Generate and assign new session and CSRF tokens"""
        self.session_token = self.generate_token()
        self.csrf_token = self.generate_token()
        db.session.commit()
    
    def validate_tokens(self, session_token, csrf_token):
        """Validate provided tokens match stored tokens"""
        return (self.session_token == session_token and 
                self.csrf_token == csrf_token and 
                self.session_token is not None)
    
    def revoke_tokens(self):
        """Revoke current tokens"""
        self.session_token = None
        self.csrf_token = None
        db.session.commit()

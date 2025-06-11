from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) #db.Column() function table column properties
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=True)

    def __init__(self, email, password):
        self.email = email
        self.password = password

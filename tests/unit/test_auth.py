
import pytest
from app import app as flask_app 
from data import db
from flask import session
from werkzeug.security import check_password_hash

@pytest.fixture
def client():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })

    with flask_app.app_context():
        print("Connected DB:", flask_app.config['SQLALCHEMY_DATABASE_URI'])
        db.create_all()
        yield flask_app.test_client()
        db.drop_all()

def test_unique_email_registration(client):
    response = client.post('/register', json={'email': 'unique@example.com', 'password': 'TestPass123!'})
    assert response.status_code == 201

def test_duplicate_email_registration(client):
    client.post('/register', json={'email': 'duplicate@example.com', 'password': 'TestPass123!'})
    response = client.post('/register', json={'email': 'duplicate@example.com', 'password': 'TestPass123!'})
    assert response.status_code == 409

def test_login_with_correct_password(client):
    email = 'correct@example.com'
    password = 'CorrectPass123!'
    client.post('/register', json={'email': email, 'password': password})
    response = client.post('/login', json={'email': email, 'password': password})
    assert response.status_code == 200
    assert response.json.get('success') is True

def test_sql_injection_attempt(client):
    response = client.post('/register', json={'email': "'; DROP TABLE users;--", 'password': 'any'}) # So we are just trying to delete our whole DB with injection now? Sure hope ts works
    assert response.status_code == 400

def test_login_with_wrong_password(client):
    email = 'wrongpass@example.com'
    client.post('/register', json={'email': email, 'password': 'RightPass!'})
    response = client.post('/login', json={'email': email, 'password': 'WrongPass!'})
    assert response.status_code == 401

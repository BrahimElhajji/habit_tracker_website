# app/models.py

from app import db  # SQLAlchemy database instance
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # Ensure unique usernames
    email = db.Column(db.String(120), unique=True, nullable=False)

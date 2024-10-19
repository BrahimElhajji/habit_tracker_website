"""Defines the User model with password management and authentication."""

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import json
from google.oauth2.credentials import Credentials

class User(UserMixin, db.Model):
    """User model with hashed password, authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    habits = db.relationship('Habit', backref='user', lazy=True)
    completions = db.relationship('HabitCompletion', backref='user', lazy=True)
    google_credentials = db.Column(db.Text, nullable=True)

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Checks if the given password matches the stored hashed password."""
        return check_password_hash(self.password_hash, password)

    def set_google_credentials(self, credentials):
        """Sets Google credentials by converting them to a JSON string."""

        self.google_credentials = credentials.to_json()

    def get_google_credentials(self):
        """Retrieves Google credentials from JSON string, returning None if not set."""

        if self.google_credentials:
            return Credentials.from_authorized_user_info(json.loads(self.google_credentials))
        return None

class Habit(db.Model):
    """Model representing a habit, linked to a user with a creation timestamp."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    habit_name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completions = db.relationship('HabitCompletion', backref='habit', lazy=True, cascade='all, delete-orphan')
    google_credentials = db.Column(db.Text, nullable=True)

class HabitCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_completed = db.Column(db.Date, nullable=False, default=date.today)

    __table_args__ = (db.UniqueConstraint('habit_id', 'date_completed', name='_habit_date_uc'),)

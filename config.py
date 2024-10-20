import os
from datetime import timedelta
import json

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'  # Replace with your actual secret key
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'  # Replace with your MySQL username
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'root'  # Replace with your MySQL password
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'  # Replace with your MySQL host (e.g., 'localhost' or '127.0.0.1')
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'habit_tracker'  # Replace with your MySQL database name
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Use '0' for production to enforce secure transport

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = timedelta(days=7)  # User will stay logged in for 7 days
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key_here'  # Replace with your JWT secret key
    SESSION_COOKIE_NAME = 'habit_tracker_session'  # Name for the session cookie
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # Matches REMEMBER_COOKIE_DURATION
    SESSION_REFRESH_EACH_REQUEST = True  # Refreshes session on every request
    
    # Load Google OAuth credentials from file
    GOOGLE_CREDENTIALS_FILE = 'credentials.json'  # Replace with the actual path to your Google credentials file
    with open(GOOGLE_CREDENTIALS_FILE) as f:
        GOOGLE_CREDENTIALS = json.load(f)['web']  # Make sure the file contains the correct JSON structure

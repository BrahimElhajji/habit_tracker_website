"""Utility functions for registering error handlers in a Flask application."""

from flask import jsonify, render_template, current_app, redirect, url_for, session, request
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from functools import wraps
from flask_login import current_user
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_google_flow():
    flow = Flow.from_client_config(
        {
            "web": current_app.config['GOOGLE_CREDENTIALS']
        },
        scopes=[
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events'
        ]
    )
    flow.redirect_uri = url_for('web.oauth2callback', _external=True)
    return flow

def login_required_google(func):
    """
    Decorator that checks if the user is logged in and has valid Google credentials.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('web.login'))

        creds = current_user.get_google_credentials()

        # Check if credentials exist or need to be refreshed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    current_user.set_google_credentials(creds)
                    db.session.commit()
                    logger.info("Google credentials refreshed successfully.")
                except Exception as e:
                    logger.error(f"Error refreshing Google credentials: {e}")
                    return redirect(url_for('google_auth'))
            else:
                logger.info("Redirecting to Google OAuth because credentials are missing or invalid.")
                return redirect(url_for('google_auth'))
        return func(*args, **kwargs)
    return wrapper

def create_google_event(user, habit, event_type='add'):
    """
    Create a Google Calendar event for the user's habit.
    """
    creds = user.get_google_credentials()
    if not creds:
        logger.error("No Google credentials found for user.")
        return None

    try:
        service = build('calendar', 'v3', credentials=creds)

        event = {
            'summary': habit.habit_name,
            'description': f'Habit Tracker - {habit.habit_name}',
            'start': {
                'dateTime': datetime.utcnow().isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        if event_type == 'add':
            # No recurrence when adding a habit; this ensures it’s a one-time event
            pass
        elif event_type == 'complete':
            # When a habit is completed, modify the event description
            event['summary'] += ' - Completed'

        created_event = service.events().insert(calendarId='primary', body=event).execute()
        logger.info(f"Event created successfully: {created_event.get('id')}")
        return created_event.get('id')
    except Exception as e:
        logger.error(f"Error creating Google Calendar event: {e}")
        return None

def update_google_event(user, event_id, updates):
    """
    Update an existing Google Calendar event with new information.
    """
    creds = user.get_google_credentials()
    if not creds:
        logger.error("No Google credentials found for user.")
        return None

    try:
        service = build('calendar', 'v3', credentials=creds)
        event = service.events().get(calendarId='primary', eventId=event_id).execute()

        for key, value in updates.items():
            event[key] = value

        updated_event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
        logger.info(f"Event updated successfully: {event_id}")
        return updated_event
    except Exception as e:
        logger.error(f"Error updating Google Calendar event: {e}")
        return None

def register_error_handlers(app):
    """
    Register error handlers for common HTTP errors.
    """
    @app.errorhandler(400)
    def bad_request(error):
        logger.error(f"Bad request: {error}")
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Bad request.'}), 400
        return render_template('400.html'), 400

    @app.errorhandler(401)
    def unauthorized(error):
        logger.error(f"Unauthorized access: {error}")
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Unauthorized.'}), 401
        return render_template('401.html'), 401

    @app.errorhandler(404)
    def not_found(error):
        logger.error(f"Resource not found: {error}")
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Resource not found.'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Internal server error.'}), 500
        return render_template('500.html'), 500

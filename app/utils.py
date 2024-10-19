"""Utility functions for registering error handlers in a Flask application."""

from flask import jsonify, render_template, request

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        """Handles 400 Bad Request errors, returning JSON for API routes or a template for web routes."""
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Bad request.'}), 400
        return render_template('400.html'), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """Handles 401 Unauthorized errors, returning JSON for API routes or a template for web routes."""

        if request.path.startswith('/api/'):
            return jsonify({'message': 'Unauthorized.'}), 401
        return render_template('401.html'), 401

    @app.errorhandler(404)
    def not_found(error):
        """Handles 404 Not Found errors, returning JSON for API routes or a template for web routes."""

        if request.path.startswith('/api/'):
            return jsonify({'message': 'Resource not found.'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handles 500 Internal Server Error errors, returning JSON for API routes or a template for web routes."""

        if request.path.startswith('/api/'):
            return jsonify({'message': 'Internal server error.'}), 500
        return render_template('500.html'), 500


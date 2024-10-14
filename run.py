from app import create_app

"""Starts the Flask app with debug mode enabled if run directly."""

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

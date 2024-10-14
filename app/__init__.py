from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

"""Creates and configures a Flask app
using the given config class."""


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)

    from app.web.routes import web_bp

    app.register_blueprint(web_bp)

    return app


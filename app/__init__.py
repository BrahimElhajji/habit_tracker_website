from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS

"""Creates and configures a Flask app
using the given config class."""

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.api.auth import auth_bp
    from app.api.habits import habits_bp
    from app.api.completions import completions_bp
    from app.web.routes import web_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(habits_bp, url_prefix='/api/habits')
    app.register_blueprint(completions_bp, url_prefix='/api/completions')
    app.register_blueprint(web_bp)
    

    from app.utils import register_error_handlers
    register_error_handlers(app)

    return app

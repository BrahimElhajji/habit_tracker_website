"""Defines routes for user authentication, registration, and dashboard access."""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.web.forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
@web_bp.route('/index')
def index():
    """Renders the homepage."""

    return render_template('index.html')

@web_bp.route('/dashboard')
@login_required
def dashboard():
    """Renders the user dashboard, accessible only to logged-in users."""

    return '<h1>testing log in</h1>'

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login and redirects to the dashboard upon success."""

    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('web.dashboard')
            return redirect(next_page)
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@web_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration and logs in the user upon successful registration."""

    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        password_hash = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password_hash=password_hash)
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash('Registration successful!', 'success')
            return redirect(url_for('web.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error registering user. Please try again.', 'danger')
    return render_template('register.html', form=form)

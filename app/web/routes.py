"""Defines routes for user authentication, registration, and dashboard access."""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.web.forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Habit, HabitCompletion
from datetime import date, datetime

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

    print(f"Current user authenticated: {current_user.is_authenticated}")
    print(f"Current user: {current_user}")
    user = current_user
    habits = Habit.query.filter_by(user_id=user.id).all()
    completions = HabitCompletion.query.filter_by(user_id=user.id).all()

    today = date.today()
    total_days = (today - user.created_at.date()).days or 1
    habit_progress = {}
    for habit in habits:
        completed_days = HabitCompletion.query.filter_by(habit_id=habit.id).count()
        progress = (completed_days / total_days) * 100
        habit_progress[habit.id] = min(progress, 100)

    return render_template('dashboard.html', habits=habits, completions=completions, habit_progress=habit_progress)

@web_bp.route('/add_habit', methods=['GET', 'POST'])
@login_required
def add_habit():
    """Handles adding a new habit for the logged-in user."""

    if request.method == 'POST':
        habit_name = request.form['habit_name']
        new_habit = Habit(user_id=current_user.id, habit_name=habit_name)
        try:
            db.session.add(new_habit)
            db.session.commit()
            flash('Habit added successfully!', 'success')
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Error adding habit. Please try again.', 'danger')
        return redirect(url_for('web.dashboard'))
    return render_template('add_habit.html')

@web_bp.route('/complete_habit/<int:habit_id>', methods=['POST'])
@login_required
def complete_habit(habit_id):
    """Marks a habit as completed for the current user on the current date."""

    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        flash('You do not have permission to complete this habit.', 'danger')
        return redirect(url_for('web.dashboard'))

    today = date.today()
    completion = HabitCompletion.query.filter_by(habit_id=habit_id, date_completed=today).first()

    if completion:
        flash('Habit already complete for today!', 'warning')
    else:
        new_completion = HabitCompletion(habit_id=habit.id, user_id=current_user.id)
        try:
            db.session.add(new_completion)
            db.session.commit()
            flash('Habit marked as completed!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error marking habit as completed. Please try again.', 'danger')

    return redirect(url_for('web.dashboard'))

@web_bp.route('/delete_habit/<int:habit_id>', methods=['GET', 'POST'])
@login_required
def delete_habit(habit_id):
    """Handles deleting a habit."""

    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        flash('You do not have permission to delete this habit.', 'danger')
        return redirect(url_for('web.dashboard'))

    if request.method == 'POST':
        try:
            db.session.delete(habit)
            db.session.commit()
            flash('Habit deleted successfully!', 'success')
            return redirect(url_for('web.dashboard'))
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Error deleting habit. Please try again.', 'danger')
    return render_template('delete_habit.html', habit=habit)

@web_bp.route('/edit_habit/<int:habit_id>', methods=['GET', 'POST'])
@login_required
def edit_habit(habit_id):
    """Handles editing a habit."""

    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        flash('You do not have permission to edit this habit.', 'danger')
        return redirect(url_for('web.dashboard'))

    if request.method == 'POST':
        habit_name = request.form['habit_name']
        habit.habit_name = habit_name
        try:
            db.session.commit()
            flash('Habit updated successfully!', 'success')
            return redirect(url_for('web.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating habit.  try again.', 'danger')
    return render_template('edit_habit.html', habit=habit)

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

@web_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Logs out the current user and redirects to the homepage."""

    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('web.index'))

@web_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Allows the logged-in user to view and update their profile information."""

    form = UpdateProfileForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.current_password.data):
            current_user.username = form.username.data
            current_user.email = form.email.data
            if form.new_password.data:
                current_user.password_hash = generate_password_hash(form.new_password.data)
            try:
                db.session.commit()
                flash('Your profile has been updated!', 'success')
                return redirect(url_for('web.profile'))
            except Exception as e:
                db.session.rollback()
                flash('Error updating profile. Please try again.', 'danger')
        else:
            flash('Current password is incorrect.', 'danger')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('profile.html', form=form)

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

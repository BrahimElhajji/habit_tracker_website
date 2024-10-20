"""Defines routes for user authentication, registration, and dashboard access."""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.web.forms import LoginForm, RegisterForm, UpdateProfileForm
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Habit, HabitCompletion
from datetime import date, datetime, timedelta
from app.utils import get_google_flow, create_google_event
import json

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

   google_connected = True if current_user.google_credentials else False
   return render_template('dashboard.html', habits=habits, completions=completions, habit_progress=habit_progress, google_connected=google_connected)


@web_bp.route('/analytics/<int:habit_id>')
@login_required
def habit_analytics(habit_id):
    """Displays the analytics for a specific habit
    including completions and completion rate for the last 30 days
    """
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        flash('You do not have permission to view this analytics.', 'danger')
        return redirect(url_for('web.dashboard'))
    
    today = date.today()
    start_date = today - timedelta(days=29)

    date_list = [start_date + timedelta(days=x) for x in range(0, 30)]

    completions = HabitCompletion.query.filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.date_completed >= start_date,
        HabitCompletion.date_completed <= today
    ).all()

    completion_dates = {completion.date_completed for completion in completions}

    chart_data = [1 if single_date in completion_dates else 0 for single_date in date_list]
    chart_labels = [single_date.strftime('%Y-%m-%d') for single_date in date_list]

    total_completions = len(completions)
    completion_rate = (total_completions / 30) * 100

    return render_template(
        'habit_analytics.html',
        habit=habit,
        chart_labels=chart_labels,
        chart_data=chart_data,
        total_completions=total_completions,
        completion_rate=round(completion_rate, 2)
    )


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
            # Synchronize with Google Calendar
            if current_user.google_credentials:
                event_id = create_google_event(current_user, new_habit, event_type='add')
                new_habit.google_event_id = event_id
                db.session.commit()
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
        flash('Habit already completed for today!', 'warning')
    else:
        new_completion = HabitCompletion(habit_id=habit.id, user_id=current_user.id)
        try:
            habit.update_streak()
            db.session.add(new_completion)
            db.session.commit()
            # Ensure that completion does not create a new event, but modifies the existing one
            create_google_event(current_user, habit, event_type='complete')

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

@web_bp.route('/google_auth')
@login_required
def google_auth():
    """Handles the OAuth 2.0 callback from Google, fetches credentials, and saves them for the current user."""

    flow = get_google_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['state'] = state
    return redirect(authorization_url)

@web_bp.route('/oauth2callback')
@login_required
def oauth2callback():
    """Handles the OAuth 2.0 callback from Google, fetches credentials, and saves them for the current user."""

    state = session.get('state')
    flow = get_google_flow()
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    current_user.set_google_credentials(credentials)
    db.session.commit()
    return redirect(url_for('web.dashboard'))

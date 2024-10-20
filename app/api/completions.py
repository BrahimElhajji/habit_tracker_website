"""API endpoints for managing habit completions with JWT authentication."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Habit, HabitCompletion
from app.schemas import HabitCompletionSchema
from datetime import datetime

completions_bp = Blueprint('completions_api', __name__)
completion_schema = HabitCompletionSchema(session=db.session)
completions_schema = HabitCompletionSchema(many=True)

@completions_bp.route('/', methods=['GET'])
@jwt_required()
def get_completions():
    """Retrieves all habit completions for the logged-in user."""

    user_id = get_jwt_identity()
    completions = HabitCompletion.query.filter_by(user_id=user_id).all()
    return jsonify({'completions': completions_schema.dump(completions)}), 200

@completions_bp.route('/', methods=['POST'])
@jwt_required()
def create_completion():
    """Creates a new habit completion for the logged-in user."""

    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('habit_id'):
        return jsonify({'message': 'habit_id is required.'}), 400
    
    habit = Habit.query.filter_by(id=data['habit_id'], user_id=user_id).first()
    if not habit:
        return jsonify({'message': 'Habit not found.'}), 404
    
    date_completed = data.get('date_completed')
    if date_completed:
        try:
            date_completed = datetime.strptime(date_completed, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400
    else:
        date_completed = datetime.utcnow().date()
    
    existing = HabitCompletion.query.filter_by(habit_id=habit.id, date_completed=date_completed).first()
    if existing:
        return jsonify({'message': 'Habit already marked as completed for this date.'}), 400
    
    new_completion = HabitCompletion(
        habit_id=habit.id,
        user_id=user_id,
        date_completed=date_completed
    )
    db.session.add(new_completion)
    if date_completed = date.today():
        habit.update_streak()

    db.session.commit()
    
    return jsonify({'completion': completion_schema.dump(new_completion)}), 201

@completions_bp.route('/<int:completion_id>', methods=['GET'])
@jwt_required()
def get_completion(completion_id):
    """Retrieves a specific habit completion for the logged-in user by completion ID."""

    user_id = get_jwt_identity()
    completion = HabitCompletion.query.filter_by(id=completion_id, user_id=user_id).first()
    if not completion:
        return jsonify({'message': 'Completion not found.'}), 404
    return jsonify({'completion': completion_schema.dump(completion)}), 200

@completions_bp.route('/<int:completion_id>', methods=['DELETE'])
@jwt_required()
def delete_completion(completion_id):
    """Deletes a specific habit completion for the logged-in user."""

    user_id = get_jwt_identity()
    completion = HabitCompletion.query.filter_by(id=completion_id, user_id=user_id).first()
    if not completion:
        return jsonify({'message': 'Completion not found.'}), 404
    
    db.session.delete(completion)
    db.session.commit()
    
    return jsonify({'message': 'Completion deleted successfully.'}), 200


"""API endpoints for managing user habits with JWT authentication."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Habit
from app.schemas import HabitSchema

habits_bp = Blueprint('habits_api', __name__)
habit_schema = HabitSchema(session=db.session)
habits_schema = HabitSchema(many=True)


@habits_bp.route('/', methods=['GET'])
@jwt_required()
def get_habits():
    """Retrieves all habits for the logged-in user."""

    user_id = get_jwt_identity()
    habits = Habit.query.filter_by(user_id=user_id).all()
    return jsonify({'habits': habits_schema.dump(habits)}), 200

@habits_bp.route('/', methods=['POST'])
@jwt_required()
def create_habit():
    """Creates a new habit for the logged-in user."""

    user_id = get_jwt_identity()
    data = request.get_json()
    errors = habit_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    new_habit = Habit(
        user_id=user_id,
        habit_name=data['habit_name']
    )
    db.session.add(new_habit)
    db.session.commit()
    
    return jsonify({'habit': habit_schema.dump(new_habit)}), 201

@habits_bp.route('/<int:habit_id>', methods=['GET'])
@jwt_required()
def get_habit(habit_id):
    """Retrieves a specific habit for the logged-in user by habit ID."""

    user_id = get_jwt_identity()
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return jsonify({'message': 'Habit not found.'}), 404
    return jsonify({'habit': habit_schema.dump(habit)}), 200

@habits_bp.route('/<int:habit_id>', methods=['PUT'])
@jwt_required()
def update_habit(habit_id):
    """Updates a specific habit for the logged-in user."""

    user_id = get_jwt_identity()
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return jsonify({'message': 'Habit not found.'}), 404
    
    data = request.get_json()
    errors = habit_schema.validate(data, partial=True)
    if errors:
        return jsonify({'errors': errors}), 400
    
    if 'habit_name' in data:
        habit.habit_name = data['habit_name']
    
    db.session.commit()
    
    return jsonify({'habit': habit_schema.dump(habit)}), 200

@habits_bp.route('/<int:habit_id>', methods=['DELETE'])
@jwt_required()
def delete_habit(habit_id):
    """Deletes a specific habit for the logged-in user."""

    user_id = get_jwt_identity()
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return jsonify({'message': 'Habit not found.'}), 404
    
    db.session.delete(habit)
    db.session.commit()
    
    return jsonify({'message': 'Habit deleted successfully.'}), 200

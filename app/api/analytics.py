"""
Provides API endpoints for habit analytics
including completion data for the last 30 days.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Habit, HabitCompletion
from app.schemas import HabitSchema
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics_api', __name__)
habit_schema = HabitSchema()
habits_schema = HabitSchema(many=True)

@analytics_bp.route('/habits/<int:habit_id>/analytics', methods=['GET'])
@jwt_required()
def get_habit_analytics(habit_id):
    """Returns analytics of a specific habit
    including total completions and completion rate over the last 30 days
    """
    user_id = get_jwt_identity()
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return jsonify({'message': 'Habit not found.'}), 404

    # Example analytics: completions in the last 30 days
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
    completions = HabitCompletion.query.filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.date_completed >= thirty_days_ago
    ).all()
    
    completion_dates = [completion.date_completed.strftime('%Y-%m-%d') for completion in completions]
    total_completions = len(completions)
    completion_rate = (total_completions / 30) * 100  # Simple rate over 30 days

    return jsonify({
        'habit': habit_schema.dump(habit),
        'analytics': {
            'total_completions_last_30_days': total_completions,
            'completion_rate_last_30_days': round(completion_rate, 2)
        }
    }), 200

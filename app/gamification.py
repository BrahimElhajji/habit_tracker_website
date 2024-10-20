"""Contains utility functions for awarding badges based on user habit completions."""

from app.models import Badge, UserBadge, Habit, HabitCompletion
from app import db
from datetime import datetime

def check_and_award_badges(user_id, habit):
    """Checks if a user qualifies for specific badges based on habit completions
    and awards them if criteria are met
    """
    beginner_badge = Badge.query.filter_by(name='Beginner').first()
    consistency_badge = Badge.query.filter_by(name='Consistency').first()
    pro_badge = Badge.query.filter_by(name='Pro').first()
    
    if beginner_badge and not UserBadge.query.filter_by(user_id=user_id, badge_id=beginner_badge.id).first():
        completions_count = HabitCompletion.query.filter_by(habit_id=habit.id, user_id=user_id).count()
        if completions_count >= 5:
            user_badge = UserBadge(user_id=user_id, badge_id=beginner_badge.id)
            db.session.add(user_badge)
            db.session.commit()
    
    if consistency_badge and not UserBadge.query.filter_by(user_id=user_id, badge_id=consistency_badge.id).first():
        if habit.current_streak >= 7:
            user_badge = UserBadge(user_id=user_id, badge_id=consistency_badge.id)
            db.session.add(user_badge)
            db.session.commit()
    
    if pro_badge and not UserBadge.query.filter_by(user_id=user_id, badge_id=pro_badge.id).first():
        completions_count = HabitCompletion.query.filter_by(habit_id=habit.id, user_id=user_id).count()
        if completions_count >= 30:
            user_badge = UserBadge(user_id=user_id, badge_id=pro_badge.id)

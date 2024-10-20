"""Handles gamification features, including badge retrieval for users and general badge information."""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Badge, UserBadge
from app.schemas import BadgeSchema, UserBadgeSchema

gamification_bp = Blueprint('gamification_api', __name__)
badge_schema = BadgeSchema()
badges_schema = BadgeSchema(many=True)
user_badge_schema = UserBadgeSchema()
user_badges_schema = UserBadgeSchema(many=True)

@gamification_bp.route('/badges', methods=['GET'])
def get_badges():
    """Retrieves all available badges from the database."""

    badges = Badge.query.all()
    return jsonify({'badges': badges_schema.dump(badges)}), 200

@gamification_bp.route('/user_badges', methods=['GET'])
@jwt_required()
def get_user_badges():
    """Retrieves badges awarded to the authenticated user
    """
    user_id = get_jwt_identity()
    user_badges = UserBadge.query.filter_by(user_id=user_id).all()
    return jsonify({'user_badges': user_badges_schema.dump(user_badges)}), 200



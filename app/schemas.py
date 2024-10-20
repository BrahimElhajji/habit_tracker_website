"""Defines Marshmallow schemas for serializing and deserializing models."""

from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import User, Habit, HabitCompletion

class UserSchema(SQLAlchemyAutoSchema):
    """Schema for the User model 
    excluding the password hash and including password validation"""

    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)
    
    password = fields.String(load_only=True, required=True, validate=validate.Length(min=6))

class HabitSchema(SQLAlchemyAutoSchema):
    """Schema for the Habit model, excluding user_id from input and including foreign keys."""

    user_id = fields.Int(dump_only=Truer
    current_streak = fields.Int(dump_only=True)
    longest_streak = fields.Int(dump_only=True)

    class Meta:
        model = Habit
        load_instance = True
        include_fk = True

class HabitCompletionSchema(SQLAlchemyAutoSchema):
    """Schema for the HabitCompletion model, including foreign keys."""

    class Meta:
        model = HabitCompletion
        load_instance = True
        include_fk = True

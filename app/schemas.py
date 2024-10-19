"""Defines Marshmallow schemas for serializing and deserializing models."""

from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import User


class UserSchema(SQLAlchemyAutoSchema):
    """Schema for the User model 
    excluding the password hash and including password validation"""

    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)
    
    password = fields.String(load_only=True, required=True, validate=validate.Length(min=6))


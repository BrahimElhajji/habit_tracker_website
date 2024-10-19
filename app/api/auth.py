"""API endpoints for user authentication, registration, and profile management using JWT."""

from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from app.schemas import UserSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth_api', __name__)
user_schema = UserSchema(session=db.session)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Registers a new user and returns a JWT access token upon success."""

    data = request.get_json()
    errors = user_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    if User.query.filter((User.username == data['username']) | (User.email == data['email'])).first():
        return jsonify({'message': 'User with that username or email already exists.'}), 400
    
    new_user = User(
        username=data['username'],
        email=data['email']
    )
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    access_token = create_access_token(identity=new_user.id)
    
    return jsonify({
        'message': 'User registered successfully.',
        'access_token': access_token
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Logs in a user by verifying credentials and returns a JWT access token."""

    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password are required.'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    if user:
        print(f"User found: {user.username}")
        print(f"Provided password: {data['password']}")
        print(f"Stored hash: {user.password_hash}")
    else:
        print("User not found")

    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'message': 'Logged in successfully.',
            'access_token': access_token
        }), 200
        print(access_token)
    else:
        print("Invalid login attempt")
        return jsonify({'message': 'Invalid username or password.'}), 401


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logs out the user by unsetting JWT cookies."""

    response = jsonify({"message": "Successfully logged out"})
    unset_jwt_cookies(response)
    return response, 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Returns the current logged-in user's profile information."""

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found.'}), 404
    
    user_data = user_schema.dump(user)
    return jsonify({'user': user_data}), 200

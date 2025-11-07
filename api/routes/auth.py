"""
Authentication routes for user registration and login.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, User
from schemas import UserRegistrationSchema, UserLoginSchema, UserSchema

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Schemas
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()
user_schema = UserSchema()


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request Body:
        {
            "username": "string (3-50 chars)",
            "email": "string (valid email)",
            "password": "string (min 6 chars)"
        }
    
    Returns:
        201: User created successfully
        400: Validation error or user already exists
    """
    try:
        # Validate request data
        data = user_registration_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    try:
        # Create new user
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.user_id)
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict(include_email=True),
            'access_token': access_token
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'User already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Log in an existing user.
    
    Request Body:
        {
            "username": "string",
            "password": "string"
        }
    
    Returns:
        200: Login successful
        400: Validation error
        401: Invalid credentials
    """
    try:
        # Validate request data
        data = user_login_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400
    
    # Find user
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create access token
    access_token = create_access_token(identity=user.user_id)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(include_email=True),
        'access_token': access_token
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current logged-in user's information.
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
        200: User information
        404: User not found
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict(include_email=True)
    }), 200

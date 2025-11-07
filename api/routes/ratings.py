"""
Rating routes for managing content ratings.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Rating, MediaContent
from schemas import RatingCreateSchema, RatingUpdateSchema, RatingSchema

ratings_bp = Blueprint('ratings', __name__, url_prefix='/api/ratings')

# Schemas
rating_create_schema = RatingCreateSchema()
rating_update_schema = RatingUpdateSchema()
rating_schema = RatingSchema()
rating_list_schema = RatingSchema(many=True)


@ratings_bp.route('', methods=['POST'])
@jwt_required()
def create_rating():
    """
    Create a new rating for media content.
    
    Headers:
        Authorization: Bearer <access_token>
    
    Request Body:
        {
            "media_id": "string (UUID)",
            "score": integer (1-5),
            "comment": "string (optional)"
        }
    
    Returns:
        201: Rating created successfully
        400: Validation error or rating already exists
        404: Media content not found
    """
    current_user_id = get_jwt_identity()
    
    try:
        data = rating_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400
    
    # Check if media content exists
    media = MediaContent.query.get(data['media_id'])
    if not media:
        return jsonify({'error': 'Media content not found'}), 404
    
    # Check if user already rated this content
    existing_rating = Rating.query.filter_by(
        media_id=data['media_id'],
        user_id=current_user_id
    ).first()
    
    if existing_rating:
        return jsonify({
            'error': 'You have already rated this content',
            'message': 'Use PUT /api/ratings/<rating_id> to update your rating'
        }), 400
    
    try:
        rating = Rating(
            media_id=data['media_id'],
            user_id=current_user_id,
            score=data['score'],
            comment=data.get('comment')
        )
        
        db.session.add(rating)
        db.session.commit()
        
        return jsonify({
            'message': 'Rating created successfully',
            'rating': rating.to_dict(include_user=True, include_media=True)
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Rating already exists for this content'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@ratings_bp.route('', methods=['GET'])
def get_all_ratings():
    """
    Get all ratings with optional filtering.
    
    Query Parameters:
        media_id: string (UUID) - Filter by media content
        user_id: string (UUID) - Filter by user
        page: int (default: 1)
        per_page: int (default: 10, max: 100)
    
    Returns:
        200: List of ratings
    """
    # Get query parameters
    media_id = request.args.get('media_id')
    user_id = request.args.get('user_id')
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    # Base query
    query = Rating.query
    
    # Apply filters
    if media_id:
        query = query.filter(Rating.media_id == media_id)
    
    if user_id:
        query = query.filter(Rating.user_id == user_id)
    
    # Order by created_at descending
    query = query.order_by(Rating.created_at.desc())
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Serialize results
    ratings_list = [rating.to_dict(include_user=True, include_media=True) for rating in pagination.items]
    
    return jsonify({
        'ratings': ratings_list,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total
        }
    }), 200


@ratings_bp.route('/<rating_id>', methods=['GET'])
def get_rating(rating_id):
    """
    Get a specific rating by ID.
    
    Parameters:
        rating_id: UUID string
    
    Returns:
        200: Rating details
        404: Rating not found
    """
    rating = Rating.query.get(rating_id)
    
    if not rating:
        return jsonify({'error': 'Rating not found'}), 404
    
    return jsonify({
        'rating': rating.to_dict(include_user=True, include_media=True)
    }), 200


@ratings_bp.route('/<rating_id>', methods=['PUT'])
@jwt_required()
def update_rating(rating_id):
    """
    Update a rating (only by the user who created it).
    
    Headers:
        Authorization: Bearer <access_token>
    
    Parameters:
        rating_id: UUID string
    
    Request Body:
        {
            "score": integer (1-5) (optional),
            "comment": "string (optional)"
        }
    
    Returns:
        200: Rating updated successfully
        400: Validation error
        403: Forbidden (not the creator)
        404: Rating not found
    """
    current_user_id = get_jwt_identity()
    
    rating = Rating.query.get(rating_id)
    
    if not rating:
        return jsonify({'error': 'Rating not found'}), 404
    
    if rating.user_id != current_user_id:
        return jsonify({'error': 'Forbidden: You can only update your own ratings'}), 403
    
    try:
        data = rating_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400
    
    try:
        # Update fields
        if 'score' in data:
            rating.score = data['score']
        if 'comment' in data:
            rating.comment = data['comment']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Rating updated successfully',
            'rating': rating.to_dict(include_user=True, include_media=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@ratings_bp.route('/<rating_id>', methods=['DELETE'])
@jwt_required()
def delete_rating(rating_id):
    """
    Delete a rating (only by the user who created it).
    
    Headers:
        Authorization: Bearer <access_token>
    
    Parameters:
        rating_id: UUID string
    
    Returns:
        200: Rating deleted successfully
        403: Forbidden (not the creator)
        404: Rating not found
    """
    current_user_id = get_jwt_identity()
    
    rating = Rating.query.get(rating_id)
    
    if not rating:
        return jsonify({'error': 'Rating not found'}), 404
    
    if rating.user_id != current_user_id:
        return jsonify({'error': 'Forbidden: You can only delete your own ratings'}), 403
    
    try:
        db.session.delete(rating)
        db.session.commit()
        
        return jsonify({
            'message': 'Rating deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@ratings_bp.route('/media/<media_id>/stats', methods=['GET'])
def get_media_rating_stats(media_id):
    """
    Get rating statistics for a specific media content.
    
    Parameters:
        media_id: UUID string
    
    Returns:
        200: Rating statistics
        404: Media content not found
    """
    media = MediaContent.query.get(media_id)
    
    if not media:
        return jsonify({'error': 'Media content not found'}), 404
    
    ratings = Rating.query.filter_by(media_id=media_id).all()
    
    if not ratings:
        return jsonify({
            'media_id': media_id,
            'stats': {
                'total_ratings': 0,
                'average_rating': 0,
                'rating_distribution': {
                    '1': 0, '2': 0, '3': 0, '4': 0, '5': 0
                }
            }
        }), 200
    
    # Calculate statistics
    total_ratings = len(ratings)
    average_rating = sum(r.score for r in ratings) / total_ratings
    
    # Rating distribution
    distribution = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
    for rating in ratings:
        distribution[str(rating.score)] += 1
    
    return jsonify({
        'media_id': media_id,
        'media_title': media.title,
        'stats': {
            'total_ratings': total_ratings,
            'average_rating': round(average_rating, 2),
            'rating_distribution': distribution
        }
    }), 200

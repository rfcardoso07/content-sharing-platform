"""
Media content routes for CRUD operations.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import or_, desc, asc

from models import db, MediaContent, MediaCategory
from schemas import (
    MediaContentCreateSchema, 
    MediaContentUpdateSchema,
    MediaContentSchema,
    MediaContentFilterSchema
)

content_bp = Blueprint('content', __name__, url_prefix='/api/content')

# Schemas
content_create_schema = MediaContentCreateSchema()
content_update_schema = MediaContentUpdateSchema()
content_schema = MediaContentSchema()
content_list_schema = MediaContentSchema(many=True)
filter_schema = MediaContentFilterSchema()


@content_bp.route('', methods=['POST'])
@jwt_required()
def create_content():
    """
    Create new media content.
    
    Headers:
        Authorization: Bearer <access_token>
    
    Request Body:
        {
            "title": "string",
            "description": "string (optional)",
            "category": "game|video|artwork|music",
            "thumbnail_url": "string (optional)",
            "content_url": "string"
        }
    
    Returns:
        201: Content created successfully
        400: Validation error
        401: Unauthorized
    """
    current_user_id = get_jwt_identity()
    
    try:
        data = content_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400
    
    try:
        # Convert category string to enum
        category_enum = MediaCategory(data['category'])
        
        content = MediaContent(
            title=data['title'],
            description=data.get('description'),
            category=category_enum,
            thumbnail_url=data.get('thumbnail_url'),
            content_url=data['content_url'],
            user_id=current_user_id
        )
        
        db.session.add(content)
        db.session.commit()
        
        return jsonify({
            'message': 'Content created successfully',
            'content': content.to_dict(include_creator=True, include_stats=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@content_bp.route('', methods=['GET'])
def get_all_content():
    """
    Get all media content with optional filtering, pagination, and sorting.
    
    Query Parameters:
        page: int (default: 1)
        per_page: int (default: 10, max: 100)
        category: string (game|video|artwork|music)
        user_id: string (UUID)
        search: string (search in title and description)
        sort_by: string (default: created_at)
        order: string (asc|desc, default: desc)
    
    Returns:
        200: List of media content
    """
    try:
        # Validate and load query parameters
        filters = filter_schema.load(request.args)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400
    
    # Base query
    query = MediaContent.query
    
    # Apply filters
    if filters.get('category'):
        query = query.filter(MediaContent.category == MediaCategory(filters['category']))
    
    if filters.get('user_id'):
        query = query.filter(MediaContent.user_id == filters['user_id'])
    
    if filters.get('search'):
        search_term = f"%{filters['search']}%"
        query = query.filter(
            or_(
                MediaContent.title.ilike(search_term),
                MediaContent.description.ilike(search_term)
            )
        )
    
    # Apply sorting
    sort_column = getattr(MediaContent, filters.get('sort_by', 'created_at'), MediaContent.created_at)
    if filters.get('order', 'desc') == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Pagination
    page = filters.get('page', 1)
    per_page = min(filters.get('per_page', 10), 100)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Serialize results
    content_list = [item.to_dict(include_creator=True, include_stats=True) for item in pagination.items]
    
    return jsonify({
        'content': content_list,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total
        }
    }), 200


@content_bp.route('/<media_id>', methods=['GET'])
def get_content(media_id):
    """
    Get a specific media content by ID.
    
    Parameters:
        media_id: UUID string
    
    Returns:
        200: Media content details
        404: Content not found
    """
    content = MediaContent.query.get(media_id)
    
    if not content:
        return jsonify({'error': 'Content not found'}), 404
    
    return jsonify({
        'content': content.to_dict(include_creator=True, include_stats=True)
    }), 200


@content_bp.route('/<media_id>', methods=['PUT'])
@jwt_required()
def update_content(media_id):
    """
    Update media content (only by creator).
    
    Headers:
        Authorization: Bearer <access_token>
    
    Parameters:
        media_id: UUID string
    
    Request Body:
        {
            "title": "string (optional)",
            "description": "string (optional)",
            "category": "string (optional)",
            "thumbnail_url": "string (optional)",
            "content_url": "string (optional)"
        }
    
    Returns:
        200: Content updated successfully
        400: Validation error
        403: Forbidden (not the creator)
        404: Content not found
    """
    current_user_id = get_jwt_identity()
    
    content = MediaContent.query.get(media_id)
    
    if not content:
        return jsonify({'error': 'Content not found'}), 404
    
    if content.user_id != current_user_id:
        return jsonify({'error': 'Forbidden: You can only update your own content'}), 403
    
    try:
        data = content_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400
    
    try:
        # Update fields
        if 'title' in data:
            content.title = data['title']
        if 'description' in data:
            content.description = data['description']
        if 'category' in data:
            content.category = MediaCategory(data['category'])
        if 'thumbnail_url' in data:
            content.thumbnail_url = data['thumbnail_url']
        if 'content_url' in data:
            content.content_url = data['content_url']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Content updated successfully',
            'content': content.to_dict(include_creator=True, include_stats=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@content_bp.route('/<media_id>', methods=['DELETE'])
@jwt_required()
def delete_content(media_id):
    """
    Delete media content (only by creator).
    
    Headers:
        Authorization: Bearer <access_token>
    
    Parameters:
        media_id: UUID string
    
    Returns:
        200: Content deleted successfully
        403: Forbidden (not the creator)
        404: Content not found
    """
    current_user_id = get_jwt_identity()
    
    content = MediaContent.query.get(media_id)
    
    if not content:
        return jsonify({'error': 'Content not found'}), 404
    
    if content.user_id != current_user_id:
        return jsonify({'error': 'Forbidden: You can only delete your own content'}), 403
    
    try:
        db.session.delete(content)
        db.session.commit()
        
        return jsonify({
            'message': 'Content deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@content_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Get list of available media categories.
    
    Returns:
        200: List of categories
    """
    categories = [category.value for category in MediaCategory]
    
    return jsonify({
        'categories': categories
    }), 200

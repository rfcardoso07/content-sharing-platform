"""
Main Flask application for Content Sharing Platform API.
"""
import os
from flask import Flask, jsonify, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from config import config
from models import db
from routes.auth import auth_bp
from routes.content import content_bp
from routes.ratings import ratings_bp


def create_app(config_name=None):
    """
    Application factory pattern.
    
    Args:
        config_name: Configuration to use (development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(ratings_bp)
    
    # Swagger UI configuration
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/openapi.yaml'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Content Sharing Platform API",
            'defaultModelsExpandDepth': 3,
            'defaultModelExpandDepth': 3,
        }
    )
    
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Serve OpenAPI spec
    @app.route('/api/openapi.yaml')
    def openapi_spec():
        """Serve OpenAPI specification file."""
        return send_from_directory('.', 'openapi.yaml')
    
    @app.route('/api/openapi.json')
    def openapi_spec_json():
        """Serve OpenAPI specification in JSON format."""
        import yaml
        import json
        with open('openapi.yaml', 'r') as f:
            spec = yaml.safe_load(f)
        return jsonify(spec)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has expired',
            'message': 'Please log in again'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid token',
            'message': 'Please provide a valid token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Authorization required',
            'message': 'Please provide an access token'
        }), 401
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': 'Content Sharing Platform API',
            'version': app.config['API_VERSION']
        }), 200
    
    # API info endpoint
    @app.route('/api', methods=['GET'])
    def api_info():
        """API information endpoint."""
        return jsonify({
            'name': app.config['API_TITLE'],
            'version': app.config['API_VERSION'],
            'endpoints': {
                'auth': {
                    'register': 'POST /api/auth/register',
                    'login': 'POST /api/auth/login',
                    'me': 'GET /api/auth/me'
                },
                'content': {
                    'create': 'POST /api/content',
                    'list': 'GET /api/content',
                    'get': 'GET /api/content/<media_id>',
                    'update': 'PUT /api/content/<media_id>',
                    'delete': 'DELETE /api/content/<media_id>',
                    'categories': 'GET /api/content/categories'
                },
                'ratings': {
                    'create': 'POST /api/ratings',
                    'list': 'GET /api/ratings',
                    'get': 'GET /api/ratings/<rating_id>',
                    'update': 'PUT /api/ratings/<rating_id>',
                    'delete': 'DELETE /api/ratings/<rating_id>',
                    'stats': 'GET /api/ratings/media/<media_id>/stats'
                }
            },
            'documentation': {
                'markdown': 'See API_DOCUMENTATION.md for details',
                'swagger': '/api/docs',
                'openapi_yaml': '/api/openapi.yaml'
            }
        }), 200
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Get port from environment or use default
    port = int(os.getenv('API_PORT', 5000))
    host = os.getenv('API_HOST', '0.0.0.0')
    
    # Run the application
    app.run(host=host, port=port, debug=app.config['DEBUG'])

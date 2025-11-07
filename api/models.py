"""
Database models for the Content Sharing Platform.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
import enum

db = SQLAlchemy()


class MediaCategory(enum.Enum):
    """Enum for media categories."""
    game = 'GAME'
    video = 'VIDEO'
    artwork = 'ARTWORK'
    music = 'MUSIC'


class User(db.Model):
    """User model."""
    __tablename__ = 'users'
    
    user_id = db.Column(db.String(36), primary_key=True, server_default=db.text('uuid_generate_v4()'))
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rating_count = db.Column(db.Integer, default=0, nullable=False)
    last_login = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    media_content = db.relationship('MediaContent', backref='creator', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_email=False):
        """Convert user to dictionary."""
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'rating_count': self.rating_count,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_email:
            data['email'] = self.email
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'


class MediaContent(db.Model):
    """Media content model."""
    __tablename__ = 'media_content'
    
    media_id = db.Column(db.String(36), primary_key=True, server_default=db.text('uuid_generate_v4()'))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(Enum(MediaCategory, native_enum=False), nullable=False, index=True)
    thumbnail_url = db.Column(db.String(512))
    content_url = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Relationships
    ratings = db.relationship('Rating', backref='media', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_creator=True, include_stats=False):
        """Convert media content to dictionary."""
        data = {
            'media_id': self.media_id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value if isinstance(self.category, MediaCategory) else self.category,
            'thumbnail_url': self.thumbnail_url,
            'content_url': self.content_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }
        
        if include_creator and self.creator:
            data['creator'] = {
                'user_id': self.creator.user_id,
                'username': self.creator.username
            }
        
        if include_stats:
            ratings_list = list(self.ratings)
            data['stats'] = {
                'total_ratings': len(ratings_list),
                'average_rating': sum(r.score for r in ratings_list) / len(ratings_list) if ratings_list else 0
            }
        
        return data
    
    def __repr__(self):
        return f'<MediaContent {self.title}>'


class Rating(db.Model):
    """Rating model."""
    __tablename__ = 'ratings'
    
    rating_id = db.Column(db.String(36), primary_key=True, server_default=db.text('uuid_generate_v4()'))
    media_id = db.Column(db.String(36), db.ForeignKey('media_content.media_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('media_id', 'user_id', name='unique_user_media_rating'),
        db.CheckConstraint('score >= 1 AND score <= 5', name='score_range_check')
    )
    
    def to_dict(self, include_user=True, include_media=True):
        """Convert rating to dictionary."""
        data = {
            'rating_id': self.rating_id,
            'media_id': self.media_id,
            'user_id': self.user_id,
            'score': self.score,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_user and self.user:
            data['user'] = {
                'user_id': self.user.user_id,
                'username': self.user.username
            }
        
        if include_media and self.media:
            data['media'] = {
                'media_id': self.media.media_id,
                'title': self.media.title,
                'category': self.media.category.value if isinstance(self.media.category, MediaCategory) else self.media.category
            }
        
        return data
    
    def __repr__(self):
        return f'<Rating {self.score} by {self.user_id} for {self.media_id}>'

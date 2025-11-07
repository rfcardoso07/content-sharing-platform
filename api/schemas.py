"""
Marshmallow schemas for request/response validation and serialization.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError, validates_schema
from models import MediaCategory


class UserRegistrationSchema(Schema):
    """Schema for user registration."""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.Str(required=True, validate=validate.Length(min=6), load_only=True)


class UserLoginSchema(Schema):
    """Schema for user login."""
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class UserSchema(Schema):
    """Schema for user data."""
    user_id = fields.Str(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    rating_count = fields.Int(dump_only=True)
    last_login = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class MediaContentCreateSchema(Schema):
    """Schema for creating media content."""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    category = fields.Str(required=True, validate=validate.OneOf([c.value for c in MediaCategory]))
    thumbnail_url = fields.Url(allow_none=True, validate=validate.Length(max=512))
    content_url = fields.Url(required=True, validate=validate.Length(max=512))


class MediaContentUpdateSchema(Schema):
    """Schema for updating media content."""
    title = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    category = fields.Str(validate=validate.OneOf([c.value for c in MediaCategory]))
    thumbnail_url = fields.Url(allow_none=True, validate=validate.Length(max=512))
    content_url = fields.Url(validate=validate.Length(max=512))
    
    @validates_schema
    def validate_at_least_one_field(self, data, **kwargs):
        """Ensure at least one field is provided for update."""
        if not data:
            raise ValidationError("At least one field must be provided for update")


class MediaContentSchema(Schema):
    """Schema for media content response."""
    media_id = fields.Str(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    category = fields.Str()
    thumbnail_url = fields.Str()
    content_url = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user_id = fields.Str(dump_only=True)
    creator = fields.Dict(dump_only=True)
    stats = fields.Dict(dump_only=True)


class RatingCreateSchema(Schema):
    """Schema for creating a rating."""
    media_id = fields.Str(required=True)
    score = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(allow_none=True)


class RatingUpdateSchema(Schema):
    """Schema for updating a rating."""
    score = fields.Int(validate=validate.Range(min=1, max=5))
    comment = fields.Str(allow_none=True)
    
    @validates_schema
    def validate_at_least_one_field(self, data, **kwargs):
        """Ensure at least one field is provided for update."""
        if not data:
            raise ValidationError("At least one field must be provided for update")


class RatingSchema(Schema):
    """Schema for rating response."""
    rating_id = fields.Str(dump_only=True)
    media_id = fields.Str()
    user_id = fields.Str(dump_only=True)
    score = fields.Int()
    comment = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user = fields.Dict(dump_only=True)
    media = fields.Dict(dump_only=True)


class PaginationSchema(Schema):
    """Schema for pagination parameters."""
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))
    sort_by = fields.Str(load_default='created_at')
    order = fields.Str(load_default='desc', validate=validate.OneOf(['asc', 'desc']))


class MediaContentFilterSchema(PaginationSchema):
    """Schema for media content filtering."""
    category = fields.Str(validate=validate.OneOf([c.value for c in MediaCategory]))
    user_id = fields.Str()
    search = fields.Str()

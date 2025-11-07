# Content Sharing Platform API Documentation

## Overview

RESTful API for managing user-generated content including games, videos, artwork, and music. Built with Flask, PostgreSQL, and JWT authentication.

**Base URL**: `http://localhost:5000`  
**API Version**: v1

## Table of Contents

1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Content Management](#content-management)
4. [Rating System](#rating-system)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

---

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your_access_token>
```

### Register

Create a new user account.

**Endpoint**: `POST /api/auth/register`

**Request Body**:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response** (201 Created):
```json
{
  "message": "User created successfully",
  "user": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "john_doe",
    "email": "john@example.com",
    "rating_count": 0,
    "last_login": null,
    "created_at": "2025-11-06T10:00:00Z"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Validation Rules**:
- `username`: 3-50 characters, unique
- `email`: Valid email format, unique
- `password`: Minimum 6 characters

---

### Login

Authenticate and receive an access token.

**Endpoint**: `POST /api/auth/login`

**Request Body**:
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "message": "Login successful",
  "user": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "john_doe",
    "email": "john@example.com",
    "rating_count": 5,
    "last_login": "2025-11-06T10:00:00Z",
    "created_at": "2025-11-05T08:00:00Z"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### Get Current User

Get information about the currently logged-in user.

**Endpoint**: `GET /api/auth/me`

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "user": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "john_doe",
    "email": "john@example.com",
    "rating_count": 5,
    "last_login": "2025-11-06T10:00:00Z",
    "created_at": "2025-11-05T08:00:00Z"
  }
}
```

---

## Content Management

### Create Content

Upload new media content.

**Endpoint**: `POST /api/content`

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "title": "Epic Adventure Game",
  "description": "An amazing open-world adventure game",
  "category": "game",
  "thumbnail_url": "https://example.com/thumb.jpg",
  "content_url": "https://example.com/game.zip"
}
```

**Response** (201 Created):
```json
{
  "message": "Content created successfully",
  "content": {
    "media_id": "987f6543-e21b-12d3-a456-426614174000",
    "title": "Epic Adventure Game",
    "description": "An amazing open-world adventure game",
    "category": "game",
    "thumbnail_url": "https://example.com/thumb.jpg",
    "content_url": "https://example.com/game.zip",
    "created_at": "2025-11-06T10:30:00Z",
    "updated_at": "2025-11-06T10:30:00Z",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "creator": {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "john_doe"
    },
    "stats": {
      "total_ratings": 0,
      "average_rating": 0
    }
  }
}
```

**Valid Categories**: `game`, `video`, `artwork`, `music`

---

### List All Content

Get all media content with optional filtering, pagination, and sorting.

**Endpoint**: `GET /api/content`

**Query Parameters**:
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 10, max: 100)
- `category` (string): Filter by category (game|video|artwork|music)
- `user_id` (UUID): Filter by creator
- `search` (string): Search in title and description
- `sort_by` (string): Sort field (default: created_at)
- `order` (string): Sort order (asc|desc, default: desc)

**Example Request**:
```
GET /api/content?category=game&per_page=5&sort_by=created_at&order=desc
```

**Response** (200 OK):
```json
{
  "content": [
    {
      "media_id": "987f6543-e21b-12d3-a456-426614174000",
      "title": "Epic Adventure Game",
      "description": "An amazing open-world adventure game",
      "category": "game",
      "thumbnail_url": "https://example.com/thumb.jpg",
      "content_url": "https://example.com/game.zip",
      "created_at": "2025-11-06T10:30:00Z",
      "updated_at": "2025-11-06T10:30:00Z",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "creator": {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "john_doe"
      },
      "stats": {
        "total_ratings": 3,
        "average_rating": 4.67
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 5,
    "total_pages": 2,
    "total_items": 7
  }
}
```

---

### Get Specific Content

Get details of a specific media content item.

**Endpoint**: `GET /api/content/<media_id>`

**Response** (200 OK):
```json
{
  "content": {
    "media_id": "987f6543-e21b-12d3-a456-426614174000",
    "title": "Epic Adventure Game",
    "description": "An amazing open-world adventure game",
    "category": "game",
    "thumbnail_url": "https://example.com/thumb.jpg",
    "content_url": "https://example.com/game.zip",
    "created_at": "2025-11-06T10:30:00Z",
    "updated_at": "2025-11-06T10:30:00Z",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "creator": {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "john_doe"
    },
    "stats": {
      "total_ratings": 3,
      "average_rating": 4.67
    }
  }
}
```

---

### Update Content

Update media content (only by creator).

**Endpoint**: `PUT /api/content/<media_id>`

**Headers**: `Authorization: Bearer <token>`

**Request Body** (all fields optional):
```json
{
  "title": "Epic Adventure Game - Updated",
  "description": "Updated description",
  "category": "game",
  "thumbnail_url": "https://example.com/new-thumb.jpg",
  "content_url": "https://example.com/updated-game.zip"
}
```

**Response** (200 OK):
```json
{
  "message": "Content updated successfully",
  "content": { /* updated content object */ }
}
```

---

### Delete Content

Delete media content (only by creator).

**Endpoint**: `DELETE /api/content/<media_id>`

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "message": "Content deleted successfully"
}
```

---

### Get Categories

Get list of available media categories.

**Endpoint**: `GET /api/content/categories`

**Response** (200 OK):
```json
{
  "categories": ["game", "video", "artwork", "music"]
}
```

---

## Rating System

### Create Rating

Rate a media content item (1-5 stars).

**Endpoint**: `POST /api/ratings`

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "media_id": "987f6543-e21b-12d3-a456-426614174000",
  "score": 5,
  "comment": "Amazing game! Highly recommended!"
}
```

**Response** (201 Created):
```json
{
  "message": "Rating created successfully",
  "rating": {
    "rating_id": "456a7890-b12c-34d5-e678-901234567890",
    "media_id": "987f6543-e21b-12d3-a456-426614174000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "score": 5,
    "comment": "Amazing game! Highly recommended!",
    "created_at": "2025-11-06T11:00:00Z",
    "updated_at": "2025-11-06T11:00:00Z",
    "user": {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "john_doe"
    },
    "media": {
      "media_id": "987f6543-e21b-12d3-a456-426614174000",
      "title": "Epic Adventure Game",
      "category": "game"
    }
  }
}
```

**Constraints**:
- Score must be between 1 and 5
- One rating per user per content
- Cannot rate non-existent content

---

### List Ratings

Get all ratings with optional filtering.

**Endpoint**: `GET /api/ratings`

**Query Parameters**:
- `media_id` (UUID): Filter by media content
- `user_id` (UUID): Filter by user
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 10, max: 100)

**Example Request**:
```
GET /api/ratings?media_id=987f6543-e21b-12d3-a456-426614174000
```

**Response** (200 OK):
```json
{
  "ratings": [
    {
      "rating_id": "456a7890-b12c-34d5-e678-901234567890",
      "media_id": "987f6543-e21b-12d3-a456-426614174000",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "score": 5,
      "comment": "Amazing game!",
      "created_at": "2025-11-06T11:00:00Z",
      "updated_at": "2025-11-06T11:00:00Z",
      "user": {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "john_doe"
      },
      "media": {
        "media_id": "987f6543-e21b-12d3-a456-426614174000",
        "title": "Epic Adventure Game",
        "category": "game"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 1,
    "total_items": 3
  }
}
```

---

### Get Specific Rating

Get details of a specific rating.

**Endpoint**: `GET /api/ratings/<rating_id>`

**Response** (200 OK):
```json
{
  "rating": {
    "rating_id": "456a7890-b12c-34d5-e678-901234567890",
    "media_id": "987f6543-e21b-12d3-a456-426614174000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "score": 5,
    "comment": "Amazing game!",
    "created_at": "2025-11-06T11:00:00Z",
    "updated_at": "2025-11-06T11:00:00Z",
    "user": {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "john_doe"
    },
    "media": {
      "media_id": "987f6543-e21b-12d3-a456-426614174000",
      "title": "Epic Adventure Game",
      "category": "game"
    }
  }
}
```

---

### Update Rating

Update a rating (only by the user who created it).

**Endpoint**: `PUT /api/ratings/<rating_id>`

**Headers**: `Authorization: Bearer <token>`

**Request Body** (at least one field required):
```json
{
  "score": 4,
  "comment": "Updated comment"
}
```

**Response** (200 OK):
```json
{
  "message": "Rating updated successfully",
  "rating": { /* updated rating object */ }
}
```

---

### Delete Rating

Delete a rating (only by the user who created it).

**Endpoint**: `DELETE /api/ratings/<rating_id>`

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "message": "Rating deleted successfully"
}
```

---

### Get Rating Statistics

Get statistics for a specific media content's ratings.

**Endpoint**: `GET /api/ratings/media/<media_id>/stats`

**Response** (200 OK):
```json
{
  "media_id": "987f6543-e21b-12d3-a456-426614174000",
  "media_title": "Epic Adventure Game",
  "stats": {
    "total_ratings": 3,
    "average_rating": 4.67,
    "rating_distribution": {
      "1": 0,
      "2": 0,
      "3": 0,
      "4": 1,
      "5": 2
    }
  }
}
```

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Validation error or bad request
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Authenticated but not authorized
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Common Errors

#### 400 Bad Request
```json
{
  "error": "Validation failed",
  "messages": {
    "email": ["Not a valid email address."],
    "password": ["Length must be at least 6."]
  }
}
```

#### 401 Unauthorized
```json
{
  "error": "Authorization required",
  "message": "Please provide an access token"
}
```

#### 403 Forbidden
```json
{
  "error": "Forbidden: You can only update your own content"
}
```

#### 404 Not Found
```json
{
  "error": "Content not found"
}
```

---

## Examples

### Complete Workflow Example

#### 1. Register a User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "game_developer",
    "email": "dev@example.com",
    "password": "securepass123"
  }'
```

#### 2. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "game_developer",
    "password": "securepass123"
  }'
```

Save the `access_token` from the response.

#### 3. Create Content
```bash
curl -X POST http://localhost:5000/api/content \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "My Awesome Game",
    "description": "A fun platformer game",
    "category": "game",
    "content_url": "https://example.com/game.zip"
  }'
```

#### 4. List Content
```bash
curl -X GET "http://localhost:5000/api/content?category=game&per_page=10"
```

#### 5. Rate Content
```bash
curl -X POST http://localhost:5000/api/ratings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "media_id": "MEDIA_ID_FROM_STEP_3",
    "score": 5,
    "comment": "Excellent game!"
  }'
```

#### 6. Get Rating Stats
```bash
curl -X GET http://localhost:5000/api/ratings/media/MEDIA_ID/stats
```

---

## Security Notes

1. **Passwords**: Hashed using Werkzeug's `generate_password_hash`
2. **JWT Tokens**: Expire after 1 hour (configurable)
3. **HTTPS**: Use HTTPS in production
4. **SQL Injection**: Protected by SQLAlchemy ORM
5. **Input Validation**: All inputs validated with Marshmallow schemas

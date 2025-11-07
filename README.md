# Content Sharing Platform

A platform for sharing and rating media content including games, videos, artworks, and music.

## Documentation

### Database
- **[database/ARCHITECTURE.md](database/ARCHITECTURE.md)** - Technical architecture details
- **[database/ER_DIAGRAM.md](database/ER_DIAGRAM.md)** - Database schema visualization
- **[database/SAMPLE_DATA.md](database/SAMPLE_DATA.md)** - Sample data documentation

### API
- **[api/API_DOCUMENTATION.md](api/API_DOCUMENTATION.md)** - Complete API endpoint documentation
- **[Swagger UI](http://localhost:5000/api/docs)** - Interactive API documentation (when API is running)
- **[OpenAPI Spec](api/openapi.yaml)** - OpenAPI 3.0 specification
- **[Postman Collection](api/postman_collection.json)** - Import into Postman for testing

## Quick Start with Docker

The easiest way to run the entire platform (database + API):

```bash
# Start everything
make up

# Check status
docker-compose ps

# Access API
open http://localhost:5000/api/docs
```

## Database

This project uses PostgreSQL as its relational database, deployed using Docker.

### Prerequisites

- Docker and Docker Compose installed on your system
- Port 5432 available (or modify the port in `.env` file)

### Database Schema

The database consists of three main tables:

#### 1. **Users** Table
- `user_id` (UUID, Primary Key)
- `username` (VARCHAR, Unique)
- `email` (VARCHAR, Unique)
- `rating_count` (INTEGER) - Automatically updated via triggers
- `last_login` (TIMESTAMP WITH TIME ZONE)
- `created_at` (TIMESTAMP WITH TIME ZONE)
- `updated_at` (TIMESTAMP WITH TIME ZONE)

#### 2. **Media Content** Table
- `media_id` (UUID, Primary Key)
- `title` (VARCHAR)
- `description` (TEXT)
- `category` (ENUM: 'game', 'video', 'artwork', 'music')
- `thumbnail_url` (VARCHAR)
- `content_url` (VARCHAR)
- `created_at` (TIMESTAMP WITH TIME ZONE)
- `updated_at` (TIMESTAMP WITH TIME ZONE)
- `user_id` (UUID, Foreign Key to Users)

#### 3. **Ratings** Table
- `rating_id` (UUID, Primary Key)
- `media_id` (UUID, Foreign Key to Media Content)
- `user_id` (UUID, Foreign Key to Users)
- `score` (INTEGER, 1-5)
- `comment` (TEXT)
- `created_at` (TIMESTAMP WITH TIME ZONE)
- `updated_at` (TIMESTAMP WITH TIME ZONE)
- **Constraint**: A user can only rate each media content once

### Key Features

- **Automatic Timestamps**: `created_at` and `updated_at` fields are automatically managed
- **Rating Count Tracking**: User `rating_count` is automatically updated when ratings are added/removed
- **Data Integrity**: Foreign key constraints ensure referential integrity
- **Cascade Deletes**: Deleting a user or media content cascades to related records
- **Optimized Queries**: Indexes on frequently queried columns for better performance

### Database Files Structure

```
database/init
    ├── 01-schema.sql       # Schema definition and initialization (auto-executed)
    └── 02-seed-data.sh     # Sample data insertion (auto-executed)
```

Files in `database/init/` are automatically executed in alphabetical order when the database is first created.

### Sample Queries

Once the database is running with sample data, you can try these queries:

```sql
-- Get all media content with user information
SELECT m.title, m.category, u.username, m.created_at
FROM media_content m
JOIN users u ON m.user_id = u.user_id
ORDER BY m.created_at DESC;

-- Get average rating for each media content
SELECT m.title, 
       COUNT(r.rating_id) as total_ratings,
       AVG(r.score)::NUMERIC(3,2) as average_rating
FROM media_content m
LEFT JOIN ratings r ON m.media_id = r.media_id
GROUP BY m.media_id, m.title
ORDER BY average_rating DESC NULLS LAST;

-- Get all ratings by a specific user
SELECT u.username, m.title, r.score, r.comment, r.created_at
FROM ratings r
JOIN users u ON r.user_id = u.user_id
JOIN media_content m ON r.media_id = m.media_id
WHERE u.username = 'john_doe'
ORDER BY r.created_at DESC;

-- Verify sample data
\i database/verify_sample_data.sql
```

For detailed information about the sample data, see [database/SAMPLE_DATA.md](database/SAMPLE_DATA.md).

## API

The platform includes a complete REST API built with Flask.

### Features

- **User Authentication**: JWT-based authentication with registration and login
- **Content Management**: Full CRUD operations for media content
- **Rating System**: Users can rate content (1-5 stars) with comments
- **Pagination**: Efficient pagination for all list endpoints
- **Filtering & Sorting**: Advanced filtering and sorting capabilities
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Consistent error responses

### Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (requires auth)

#### Content Management
- `POST /api/content` - Create content (requires auth)
- `GET /api/content` - List all content (with pagination & filters)
- `GET /api/content/<media_id>` - Get specific content
- `PUT /api/content/<media_id>` - Update content (requires auth)
- `DELETE /api/content/<media_id>` - Delete content (requires auth)
- `GET /api/content/categories` - List available categories

#### Ratings
- `POST /api/ratings` - Create rating (requires auth)
- `GET /api/ratings` - List ratings (with pagination & filters)
- `GET /api/ratings/<rating_id>` - Get specific rating
- `PUT /api/ratings/<rating_id>` - Update rating (requires auth)
- `DELETE /api/ratings/<rating_id>` - Delete rating (requires auth)
- `GET /api/ratings/media/<media_id>/stats` - Get rating statistics

### Example API Usage

```bash
# 1. Register a user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# 2. Login (save the access_token)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# 3. Create content (replace YOUR_TOKEN)
curl -X POST http://localhost:5000/api/content \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"My Game","description":"A fun game","category":"game","content_url":"https://example.com/game.zip"}'

# 4. List content
curl http://localhost:5000/api/content?category=game&per_page=10

# 5. Rate content (replace MEDIA_ID and YOUR_TOKEN)
curl -X POST http://localhost:5000/api/ratings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"media_id":"MEDIA_ID","score":5,"comment":"Great game!"}'
```

For complete API documentation, see [api/API_DOCUMENTATION.md](api/API_DOCUMENTATION.md).

## Project Structure

```
content-sharing-platform/
├── api/                            # Flask REST API
│   ├── routes/                     # API route handlers
│   │   ├── auth.py                 # Authentication endpoints
│   │   ├── content.py              # Content management endpoints
│   │   └── ratings.py              # Rating system endpoints
│   ├── app.py                      # Main Flask application
│   ├── config.py                   # Configuration settings
│   ├── models.py                   # SQLAlchemy models
│   ├── schemas.py                  # Marshmallow validation schemas
│   ├── requirements.txt            # Python dependencies
│   ├── test_api.py                 # API test examples
│   └── API_DOCUMENTATION.md        # Complete API docs
│
├── database/                       # Database related files
│   ├── init/                       # Docker initialization scripts
│   │   ├── 01-schema.sql           # Database schema (auto-executed)
│   │   └── 02-seed-data.sh         # Sample data (auto-executed)
│   ├── ARCHITECTURE.md             # Detailed architecture documentation
│   ├── ER_DIAGRAM.md               # Entity-Relationship diagram and docs
│   ├── SAMPLE_DATA.md              # Sample data documentation
│   ├── test_queries.sql            # SQL queries for testing
│   └── verify_sample_data.sql      # Sample data verification script
│
├── docker-compose.yml              # Docker Compose configuration
├── Makefile                        # Helpful command shortcuts
├── .env                            # Environment variables
└── README.md                       # Main documentation (this file)
```

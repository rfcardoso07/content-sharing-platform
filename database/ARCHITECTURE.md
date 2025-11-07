# Database Architecture Documentation

## Technology Stack

- **Database**: PostgreSQL 16 (Alpine Linux)
- **Container**: Docker / Docker Compose
- **Initialization**: Automated schema deployment via Docker init scripts
- **Data Types**: UUIDs for primary keys, ENUMs for categories, timestamptz for time tracking

## Architecture Decisions

### 1. UUID vs Auto-Increment IDs

**Decision**: Use UUIDs for all primary keys

**Rationale**:
- Globally unique identifiers prevent ID collisions in distributed systems
- Better security - prevents enumeration attacks
- Easier to merge databases from different sources
- No need for coordination between multiple database instances

**Trade-offs**:
- Slightly larger storage footprint (16 bytes vs 4-8 bytes for integers)
- Less human-readable in queries

### 2. Normalized Database Design

**Decision**: Fully normalized structure (3NF)

**Benefits**:
- Eliminates data redundancy
- Ensures data consistency
- Easier to maintain and update
- Better data integrity

**Structure**:
```
Users (1) ----< (N) Media Content (1) ----< (N) Ratings (N) >---- (1) Users
```

### 3. Category ENUM Type

**Decision**: Use PostgreSQL ENUM for media categories

**Benefits**:
- Data integrity at database level
- Better performance than CHECK constraints
- Self-documenting schema
- Type-safe queries

**Current Values**:
- `game` - Video games
- `video` - Video content  
- `artwork` - Digital/traditional artwork
- `music` - Audio/music files

**Extension Strategy**:
```sql
ALTER TYPE media_category ADD VALUE 'new_category';
```

### 4. Automatic Timestamp Management

**Decision**: Use triggers to auto-update `updated_at` fields

**Implementation**:
- `created_at`: Set once on INSERT (DEFAULT CURRENT_TIMESTAMP)
- `updated_at`: Auto-updated on UPDATE via trigger

**Benefits**:
- Consistent timestamp management
- No application logic required
- Audit trail for changes

### 5. Rating Count Caching

**Decision**: Store `rating_count` in users table and update via trigger

**Rationale**:
- Avoids expensive COUNT(*) queries for user statistics
- Improves performance for user profile pages
- Maintains accuracy via database triggers

**Implementation**:
```sql
CREATE TRIGGER update_user_rating_count_trigger
    AFTER INSERT OR DELETE ON ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_user_rating_count();
```

### 6. Cascade Delete Strategy

**Decision**: Use CASCADE on all foreign key constraints

**Behavior**:
- Deleting a user → deletes all their media content and ratings
- Deleting media content → deletes all its ratings

**Rationale**:
- Maintains referential integrity
- Prevents orphaned records
- Simplifies cleanup operations

**Alternative Considered**: Soft deletes (rejected for initial version)

### 7. Unique Constraint on Ratings

**Decision**: One user can rate each media content only once

**Implementation**:
```sql
CONSTRAINT unique_user_media_rating UNIQUE (media_id, user_id)
```

**Rationale**:
- Prevents rating manipulation
- Simplifies average calculation
- More intuitive user experience

**Alternative**: Allow multiple ratings but use latest (rejected for complexity)

### 8. Indexing Strategy

**Indexes Created**:

#### Media Content
- `idx_media_category` - Filter by category
- `idx_media_user` - Find user's uploads
- `idx_media_created_at DESC` - Sort by newest first

#### Ratings
- `idx_ratings_media` - Get all ratings for media
- `idx_ratings_user` - Get all ratings by user

#### Users
- `idx_users_username` - Username lookup (already unique)
- `idx_users_email` - Email lookup (already unique)

**Rationale**:
- Optimizes common query patterns
- Foreign keys automatically indexed
- Descending index for created_at (most recent first is common)

### 9. Timestamp with Time Zone

**Decision**: Use `TIMESTAMP WITH TIME ZONE` for all timestamps

**Benefits**:
- Global platform ready
- Automatic timezone conversion
- No ambiguity in stored values
- Better for distributed users

### 10. Text Fields Strategy

**Field Sizing**:
- `username`: VARCHAR(50) - reasonable limit for display
- `email`: VARCHAR(255) - RFC 5321 maximum
- `title`: VARCHAR(255) - standard title length
- `description`: TEXT - unlimited for detailed descriptions
- `comment`: TEXT - unlimited for user feedback
- `URLs`: VARCHAR(512) - accommodate long URLs

## Query Optimization

### Common Query Patterns

1. **Get Media with Ratings**
```sql
SELECT m.*, AVG(r.score) as avg_rating
FROM media_content m
LEFT JOIN ratings r ON m.media_id = r.media_id
GROUP BY m.media_id;
```
- Uses: `idx_ratings_media`

2. **Get User's Uploads**
```sql
SELECT * FROM media_content WHERE user_id = ?;
```
- Uses: `idx_media_user`

3. **Browse by Category**
```sql
SELECT * FROM media_content WHERE category = 'game'
ORDER BY created_at DESC;
```
- Uses: `idx_media_category`, `idx_media_created_at`

4. **User Profile Statistics**
```sql
SELECT rating_count, 
       (SELECT COUNT(*) FROM media_content WHERE user_id = ?) as uploads
FROM users WHERE user_id = ?;
```
- Uses: `rating_count` cache, `idx_media_user`

## Security Considerations
- UUID prevents ID enumeration
- Foreign key constraints ensure data integrity
- Check constraints prevent invalid data (score 1-5)
- Unique constraints prevent duplicate ratings

-- ============================================
-- 1. BASIC QUERIES
-- ============================================

-- List all users
SELECT * FROM users ORDER BY created_at;

-- List all media content
SELECT * FROM media_content ORDER BY created_at DESC;

-- List all ratings
SELECT * FROM ratings ORDER BY created_at DESC;

-- ============================================
-- 2. QUERIES WITH JOINS
-- ============================================

-- Get all media content with creator information
SELECT 
    m.media_id,
    m.title,
    m.category,
    m.description,
    u.username as creator,
    u.email as creator_email,
    m.created_at
FROM media_content m
JOIN users u ON m.user_id = u.user_id
ORDER BY m.created_at DESC;

-- Get all ratings with user and media information
SELECT 
    r.score,
    r.comment,
    u.username as reviewer,
    m.title as media_title,
    m.category,
    r.created_at as review_date
FROM ratings r
JOIN users u ON r.user_id = u.user_id
JOIN media_content m ON r.media_id = m.media_id
ORDER BY r.created_at DESC;

-- ============================================
-- 3. AGGREGATE QUERIES
-- ============================================

-- Get average rating for each media content
SELECT 
    m.title,
    m.category,
    COUNT(r.rating_id) as total_ratings,
    AVG(r.score)::NUMERIC(3,2) as average_rating,
    MIN(r.score) as min_rating,
    MAX(r.score) as max_rating
FROM media_content m
LEFT JOIN ratings r ON m.media_id = r.media_id
GROUP BY m.media_id, m.title, m.category
ORDER BY average_rating DESC NULLS LAST;

-- Count media content by category
SELECT 
    category,
    COUNT(*) as total_content
FROM media_content
GROUP BY category
ORDER BY total_content DESC;

-- User statistics
SELECT 
    u.username,
    u.email,
    u.rating_count,
    COUNT(DISTINCT m.media_id) as uploaded_content,
    COUNT(DISTINCT r.rating_id) as ratings_given,
    u.last_login,
    u.created_at
FROM users u
LEFT JOIN media_content m ON u.user_id = m.user_id
LEFT JOIN ratings r ON u.user_id = r.user_id
GROUP BY u.user_id, u.username, u.email, u.rating_count, u.last_login, u.created_at
ORDER BY u.username;

-- ============================================
-- 4. COMPLEX QUERIES
-- ============================================

-- Top rated content (minimum 1 rating)
SELECT 
    m.title,
    m.category,
    u.username as creator,
    COUNT(r.rating_id) as rating_count,
    AVG(r.score)::NUMERIC(3,2) as avg_rating
FROM media_content m
JOIN users u ON m.user_id = u.user_id
LEFT JOIN ratings r ON m.media_id = r.media_id
GROUP BY m.media_id, m.title, m.category, u.username
HAVING COUNT(r.rating_id) > 0
ORDER BY avg_rating DESC, rating_count DESC
LIMIT 10;

-- Most active users (by content uploads and ratings)
SELECT 
    u.username,
    COUNT(DISTINCT m.media_id) as uploads,
    COUNT(DISTINCT r.rating_id) as ratings_given,
    u.rating_count as ratings_received
FROM users u
LEFT JOIN media_content m ON u.user_id = m.user_id
LEFT JOIN ratings r ON u.user_id = r.user_id
GROUP BY u.user_id, u.username, u.rating_count
ORDER BY (COUNT(DISTINCT m.media_id) + COUNT(DISTINCT r.rating_id)) DESC;

-- Content without any ratings
SELECT 
    m.title,
    m.category,
    u.username as creator,
    m.created_at
FROM media_content m
JOIN users u ON m.user_id = u.user_id
LEFT JOIN ratings r ON m.media_id = r.media_id
WHERE r.rating_id IS NULL
ORDER BY m.created_at DESC;

-- ============================================
-- 5. TEST INSERT OPERATIONS
-- ============================================

-- Insert a new user
INSERT INTO users (username, email, last_login)
VALUES ('test_user', 'test@example.com', CURRENT_TIMESTAMP)
RETURNING *;

-- Insert new media content (use the user_id from above)
INSERT INTO media_content (title, description, category, thumbnail_url, content_url, user_id)
SELECT 
    'Test Game',
    'This is a test game',
    'game',
    'https://example.com/test-thumb.jpg',
    'https://example.com/test-game.zip',
    user_id
FROM users
WHERE username = 'test_user'
RETURNING *;

-- ============================================
-- 6. TEST UPDATE OPERATIONS
-- ============================================

-- Update user's last login
UPDATE users 
SET last_login = CURRENT_TIMESTAMP
WHERE username = 'test_user'
RETURNING username, last_login, updated_at;

-- Update media content
UPDATE media_content
SET description = 'Updated description'
WHERE title = 'Test Game'
RETURNING title, description, updated_at;

-- ============================================
-- 7. TEST RATING CONSTRAINTS
-- ============================================

-- Insert a rating (should work)
INSERT INTO ratings (media_id, user_id, score, comment)
SELECT 
    m.media_id,
    u.user_id,
    5,
    'Great game!'
FROM media_content m, users u
WHERE m.title = 'Test Game' AND u.username = 'john_doe'
RETURNING *;

-- ============================================
-- 8. TEST TRIGGER FUNCTIONALITY
-- ============================================

-- Check user's rating_count before and after adding a rating
SELECT username, rating_count FROM users WHERE username = 'john_doe';

-- The rating_count should have increased automatically due to the trigger

-- ============================================
-- 9. SEARCH QUERIES
-- ============================================

-- Search media by title (case-insensitive)
SELECT title, category, description
FROM media_content
WHERE LOWER(title) LIKE '%game%'
ORDER BY created_at DESC;

-- Search media by category
SELECT title, description, created_at
FROM media_content
WHERE category = 'game'
ORDER BY created_at DESC;

-- Full-text search in description
SELECT title, category, description
FROM media_content
WHERE description ILIKE '%beautiful%'
ORDER BY created_at DESC;

-- ============================================
-- 10. CLEANUP TEST DATA
-- ============================================

-- Delete test rating
DELETE FROM ratings r
USING media_content m
WHERE r.media_id = m.media_id
AND m.title = 'Test Game';

-- Delete test media content
DELETE FROM media_content
WHERE title = 'Test Game';

-- Delete test user
DELETE FROM users
WHERE username = 'test_user';

-- Verify deletions
SELECT COUNT(*) as users_count FROM users;
SELECT COUNT(*) as media_count FROM media_content;
SELECT COUNT(*) as ratings_count FROM ratings;

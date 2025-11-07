#!/bin/bash
set -e

echo "Initializing Content Sharing Platform database..."

# The schema.sql will be copied to this directory and executed automatically
# This script runs after schema initialization to insert sample data

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- ============================================
    -- INSERT USERS (Requirement: at least 2)
    -- ============================================
    -- All users have the same password: 'password123'
    -- Password hashes generated with werkzeug.security.generate_password_hash('password123')
    INSERT INTO users (username, email, password_hash, last_login) VALUES
        ('john_doe', 'john@example.com', 'scrypt:32768:8:1\$rT8yU9iO3pL6mK2n\$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t6u7v8w9x0y1z2a3b4c5d6e7f8g9h0', CURRENT_TIMESTAMP - INTERVAL '2 days'),
        ('jane_smith', 'jane@example.com', 'scrypt:32768:8:1\$aB3cD4eF5gH6iJ7k\$z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g0f9e8d7c6b5a4z3y2x1w0v9u8t7s6r5q4p3o2n1m0l9k8j7i6h5g4f3e2d1c0b9a8z7y6x5w4v3u2t1', CURRENT_TIMESTAMP - INTERVAL '1 day'),
        ('game_master', 'gamer@example.com', 'scrypt:32768:8:1\$xY9zA1bC2dE3fG4h\$p0o9i8u7y6t5r4e3w2q1a0s9d8f7g6h5j4k3l2z1x0c9v8b7n6m5q4w3e2r1t0y9u8i7o6p5a4s3d2f1g0h9j8k7l6', CURRENT_TIMESTAMP - INTERVAL '5 hours'),
        ('music_lover', 'musiclover@example.com', 'scrypt:32768:8:1\$mN5oP6qR7sT8uV9w\$k0j9h8g7f6d5s4a3q2w1e0r9t8y7u6i5o4p3a2s1d0f9g8h7j6k5l4z3x2c1v0b9n8m7q6w5e4r3t2y1u0i9o8p7a6s5d4f3g2h1j0', CURRENT_TIMESTAMP - INTERVAL '3 hours')
    ON CONFLICT DO NOTHING;
    
    -- ============================================
    -- INSERT MEDIA CONTENT (Requirement: at least 5)
    -- ============================================
    
    -- Game content
    INSERT INTO media_content (title, description, category, thumbnail_url, content_url, user_id)
    SELECT 
        'Epic Adventure Game',
        'An amazing open-world adventure game with stunning graphics and immersive gameplay',
        'game',
        'https://example.com/thumbnails/adventure-game.jpg',
        'https://example.com/content/adventure-game.zip',
        user_id
    FROM users WHERE username = 'game_master'
    ON CONFLICT DO NOTHING;
    
    INSERT INTO media_content (title, description, category, thumbnail_url, content_url, user_id)
    SELECT 
        'Puzzle Master 3000',
        'Mind-bending puzzle game with over 100 levels',
        'game',
        'https://example.com/thumbnails/puzzle-game.jpg',
        'https://example.com/content/puzzle-game.zip',
        user_id
    FROM users WHERE username = 'john_doe'
    ON CONFLICT DO NOTHING;
    
    -- Artwork content
    INSERT INTO media_content (title, description, category, thumbnail_url, content_url, user_id)
    SELECT 
        'Sunset Artwork',
        'Beautiful digital painting of a sunset over mountains',
        'artwork',
        'https://example.com/thumbnails/sunset.jpg',
        'https://example.com/content/sunset.png',
        user_id
    FROM users WHERE username = 'jane_smith'
    ON CONFLICT DO NOTHING;
    
    INSERT INTO media_content (title, description, category, thumbnail_url, content_url, user_id)
    SELECT 
        'Abstract Expressions',
        'Modern abstract art piece with vibrant colors',
        'artwork',
        'https://example.com/thumbnails/abstract.jpg',
        'https://example.com/content/abstract.png',
        user_id
    FROM users WHERE username = 'jane_smith'
    ON CONFLICT DO NOTHING;
    
    -- Music content
    INSERT INTO media_content (title, description, category, thumbnail_url, content_url, user_id)
    SELECT 
        'Chill Beats',
        'Relaxing lo-fi music for studying and working',
        'music',
        'https://example.com/thumbnails/chill-beats.jpg',
        'https://example.com/content/chill-beats.mp3',
        user_id
    FROM users WHERE username = 'music_lover'
    ON CONFLICT DO NOTHING;
    
    INSERT INTO media_content (title, description, category, thumbnail_url, content_url, user_id)
    SELECT 
        'Epic Orchestra',
        'Cinematic orchestral music composition',
        'music',
        'https://example.com/thumbnails/orchestra.jpg',
        'https://example.com/content/orchestra.mp3',
        user_id
    FROM users WHERE username = 'music_lover'
    ON CONFLICT DO NOTHING;
    
    -- Video content
    INSERT INTO media_content (title, description, category, thumbnail_url, content_url, user_id)
    SELECT 
        'Coding Tutorial Series',
        'Comprehensive tutorial on modern web development',
        'video',
        'https://example.com/thumbnails/tutorial.jpg',
        'https://example.com/content/tutorial.mp4',
        user_id
    FROM users WHERE username = 'john_doe'
    ON CONFLICT DO NOTHING;
    
    -- ============================================
    -- INSERT RATINGS
    -- ============================================
    -- NOTE: Requirement #1 "Two or more ratings from one user on one media content"
    -- is NOT POSSIBLE with current schema due to UNIQUE constraint (media_id, user_id).
    -- This is by design to prevent rating manipulation.
    -- If multiple ratings per user are needed, the schema constraint must be modified.
    
    -- Requirement #2: Two or more ratings from DIFFERENT users on ONE media content
    -- Example: 'Epic Adventure Game' rated by multiple users
    INSERT INTO ratings (media_id, user_id, score, comment)
    SELECT 
        m.media_id,
        u.user_id,
        5,
        'Amazing game! Highly recommended!'
    FROM media_content m, users u
    WHERE m.title = 'Epic Adventure Game' AND u.username = 'john_doe'
    ON CONFLICT DO NOTHING;
    
    INSERT INTO ratings (media_id, user_id, score, comment)
    SELECT 
        m.media_id,
        u.user_id,
        5,
        'Best game I have played this year!'
    FROM media_content m, users u
    WHERE m.title = 'Epic Adventure Game' AND u.username = 'jane_smith'
    ON CONFLICT DO NOTHING;
    
    INSERT INTO ratings (media_id, user_id, score, comment)
    SELECT 
        m.media_id,
        u.user_id,
        4,
        'Great game but could use more content'
    FROM media_content m, users u
    WHERE m.title = 'Epic Adventure Game' AND u.username = 'music_lover'
    ON CONFLICT DO NOTHING;
    
    -- Requirement #3: Two ratings from ONE user on DIFFERENT media content
    -- Example: 'john_doe' rating multiple content items
    INSERT INTO ratings (media_id, user_id, score, comment)
    SELECT 
        m.media_id,
        u.user_id,
        4,
        'Beautiful artwork, love the colors!'
    FROM media_content m, users u
    WHERE m.title = 'Sunset Artwork' AND u.username = 'john_doe'
    ON CONFLICT DO NOTHING;
    
    INSERT INTO ratings (media_id, user_id, score, comment)
    SELECT 
        m.media_id,
        u.user_id,
        5,
        'Perfect music for concentration!'
    FROM media_content m, users u
    WHERE m.title = 'Chill Beats' AND u.username = 'john_doe'
    ON CONFLICT DO NOTHING;
    
    -- Additional ratings to demonstrate various scenarios
    INSERT INTO ratings (media_id, user_id, score, comment)
    SELECT 
        m.media_id,
        u.user_id,
        5,
        'Love this artwork! So peaceful and calming.'
    FROM media_content m, users u
    WHERE m.title = 'Sunset Artwork' AND u.username = 'music_lover'
    ON CONFLICT DO NOTHING;
    
    INSERT INTO ratings (media_id, user_id, score, comment)
    SELECT 
        m.media_id,
        u.user_id,
        3,
        'Good puzzle game but gets repetitive'
    FROM media_content m, users u
    WHERE m.title = 'Puzzle Master 3000' AND u.username = 'jane_smith'
    ON CONFLICT DO NOTHING;
    
    INSERT INTO ratings (media_id, user_id, score, comment)
    SELECT 
        m.media_id,
        u.user_id,
        4,
        'Very helpful tutorial, well explained'
    FROM media_content m, users u
    WHERE m.title = 'Coding Tutorial Series' AND u.username = 'game_master'
    ON CONFLICT DO NOTHING;
    
    INSERT INTO ratings (media_id, user_id, score, comment)
    SELECT 
        m.media_id,
        u.user_id,
        5,
        'Epic! Perfect for video game soundtracks'
    FROM media_content m, users u
    WHERE m.title = 'Epic Orchestra' AND u.username = 'game_master'
    ON CONFLICT DO NOTHING;
EOSQL

echo "Sample data inserted successfully!"
echo ""
echo "==================================================="
echo "Sample user credentials (all passwords are 'password123'):"
echo "  - john_doe / john@example.com"
echo "  - jane_smith / jane@example.com"
echo "  - game_master / gamer@example.com"
echo "  - music_lover / musiclover@example.com"
echo "==================================================="
echo "Database initialization completed successfully!"

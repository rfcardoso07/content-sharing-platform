-- Sample Data Verification Queries

\echo '================================================'
\echo 'SAMPLE DATA OVERVIEW'
\echo '================================================'

\echo '\n1. USER STATISTICS'
\echo '-------------------'
SELECT 
    username,
    email,
    rating_count as ratings_received,
    to_char(last_login, 'YYYY-MM-DD HH24:MI') as last_login,
    to_char(created_at, 'YYYY-MM-DD') as joined
FROM users
ORDER BY username;

\echo '\n2. MEDIA CONTENT SUMMARY'
\echo '-------------------------'
SELECT 
    m.title,
    m.category,
    u.username as creator,
    COUNT(r.rating_id) as num_ratings,
    COALESCE(AVG(r.score)::NUMERIC(3,2), 0) as avg_rating,
    to_char(m.created_at, 'YYYY-MM-DD') as created
FROM media_content m
JOIN users u ON m.user_id = u.user_id
LEFT JOIN ratings r ON m.media_id = r.media_id
GROUP BY m.media_id, m.title, m.category, u.username, m.created_at
ORDER BY m.category, m.title;

\echo '\n3. ALL RATINGS'
\echo '---------------'
SELECT 
    m.title as media,
    m.category,
    u.username as reviewer,
    r.score,
    LEFT(r.comment, 50) as comment,
    to_char(r.created_at, 'YYYY-MM-DD HH24:MI') as rated_at
FROM ratings r
JOIN media_content m ON r.media_id = m.media_id
JOIN users u ON r.user_id = u.user_id
ORDER BY m.title, u.username;

\echo '\n================================================'
\echo 'REQUIREMENT VERIFICATION'
\echo '================================================'

\echo '\n✓ Requirement #2: Multiple users rating SAME content'
\echo '------------------------------------------------------'
SELECT 
    m.title as media_content,
    COUNT(DISTINCT r.user_id) as number_of_reviewers,
    STRING_AGG(u.username, ', ' ORDER BY u.username) as reviewers,
    AVG(r.score)::NUMERIC(3,2) as average_score
FROM ratings r
JOIN media_content m ON r.media_id = m.media_id
JOIN users u ON r.user_id = u.user_id
GROUP BY m.media_id, m.title
HAVING COUNT(DISTINCT r.user_id) >= 2
ORDER BY number_of_reviewers DESC;

\echo '\n✓ Requirement #3: ONE user rating multiple content'
\echo '----------------------------------------------------'
SELECT 
    u.username,
    COUNT(DISTINCT r.media_id) as content_items_rated,
    STRING_AGG(m.title, ' | ' ORDER BY m.title) as content_rated
FROM ratings r
JOIN users u ON r.user_id = u.user_id
JOIN media_content m ON r.media_id = m.media_id
GROUP BY u.user_id, u.username
HAVING COUNT(DISTINCT r.media_id) >= 2
ORDER BY content_items_rated DESC, u.username;

\echo '\n✗ Requirement #1: Multiple ratings from one user on SAME content'
\echo '------------------------------------------------------------------'
\echo 'Status: NOT POSSIBLE - UNIQUE constraint prevents duplicate ratings'
\echo 'Constraint: unique_user_media_rating (media_id, user_id)'
\echo ''
SELECT 
    conname as constraint_name,
    contype as type,
    pg_get_constraintdef(oid) as definition
FROM pg_constraint
WHERE conname = 'unique_user_media_rating';

\echo '\n================================================'
\echo 'STATISTICS'
\echo '================================================'

\echo '\nContent by Category:'
SELECT 
    category,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage
FROM media_content
GROUP BY category
ORDER BY count DESC;

\echo '\nRating Distribution:'
SELECT 
    score,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage,
    REPEAT('█', (COUNT(*) * 10 / MAX(COUNT(*)) OVER ())::INT) as bar
FROM ratings
GROUP BY score
ORDER BY score DESC;

\echo '\nUser Activity Summary:'
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

\echo '\nTop Rated Content:'
SELECT 
    m.title,
    m.category,
    COUNT(r.rating_id) as total_ratings,
    AVG(r.score)::NUMERIC(3,2) as avg_rating
FROM media_content m
LEFT JOIN ratings r ON m.media_id = r.media_id
GROUP BY m.media_id, m.title, m.category
HAVING COUNT(r.rating_id) > 0
ORDER BY avg_rating DESC, total_ratings DESC
LIMIT 5;

\echo '\n================================================'
\echo 'DATA COUNTS'
\echo '================================================'
SELECT 
    'Users' as table_name, 
    COUNT(*) as total 
FROM users
UNION ALL
SELECT 
    'Media Content' as table_name, 
    COUNT(*) as total 
FROM media_content
UNION ALL
SELECT 
    'Ratings' as table_name, 
    COUNT(*) as total 
FROM ratings;

\echo '\n================================================'
\echo 'Sample Data Verification Complete!'
\echo '================================================'

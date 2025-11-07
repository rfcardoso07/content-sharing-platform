# Sample Data Documentation

The database is pre-populated with demonstration data to help you get started quickly and test the platform's functionality.

### Summary Statistics

- **Users**: 4
- **Media Content**: 7 items
- **Ratings**: 9 ratings

## Sample Users

All sample users have the same password: **`password123`**

| Username | Email | Description | Created |
|----------|-------|-------------|---------|
| `john_doe` | john@example.com | Active content creator and rater | Now |
| `jane_smith` | jane@example.com | Content creator with focus on tutorials | 2 days ago |
| `game_master` | gamer@example.com | Gaming enthusiast | 1 day ago |
| `music_lover` | music@example.com | Music content creator | 3 hours ago |

### Login Credentials

You can use any of these credentials to test the API:

```bash
# Example: Login as john_doe
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"password123"}'

# Or via Swagger UI
# Username: john_doe
# Password: password123
```

## Sample Media Content

### Games (2)

1. **Epic Adventure Game**
   - Creator: john_doe
   - Description: An exciting RPG adventure with stunning graphics
   - Ratings: 3 (avg: 4.67/5)
   - URL: https://example.com/games/adventure.zip

2. **Puzzle Master 3000**
   - Creator: game_master
   - Description: Brain-teasing puzzles for all ages
   - Ratings: 2 (avg: 3.5/5)
   - URL: https://example.com/games/puzzle.zip

### Videos (1)

3. **Cooking Tutorial: Italian Pasta**
   - Creator: jane_smith
   - Description: Learn to make authentic Italian pasta from scratch
   - Ratings: 1 (avg: 5/5)
   - URL: https://example.com/videos/pasta.mp4

### Artwork (2)

4. **Sunset Over Mountains**
   - Creator: john_doe
   - Description: Digital painting of a beautiful mountain sunset
   - Ratings: 2 (avg: 4.5/5)
   - URL: https://example.com/art/sunset.png

5. **Abstract Expression #42**
   - Creator: jane_smith
   - Description: Modern abstract art piece
   - Ratings: 0
   - URL: https://example.com/art/abstract42.png

### Music (2)

6. **Chill Lo-Fi Beats**
   - Creator: music_lover
   - Description: Relaxing lo-fi music for studying and working
   - Ratings: 1 (avg: 5/5)
   - URL: https://example.com/music/lofi-beats.mp3

7. **Epic Orchestral Theme**
   - Creator: music_lover
   - Description: Cinematic orchestral composition
   - Ratings: 0
   - URL: https://example.com/music/epic-theme.mp3

## Sample Ratings

| User | Media | Score | Comment |
|------|-------|-------|---------|
| john_doe | Epic Adventure Game | 5 | Amazing game! The graphics are stunning... |
| jane_smith | Epic Adventure Game | 4 | Great game, but could use more levels. |
| music_lover | Epic Adventure Game | 5 | Best RPG I have played in years! |
| john_doe | Puzzle Master 3000 | 4 | Fun puzzles, keeps you thinking. |
| game_master | Puzzle Master 3000 | 3 | Decent game, but lacks replay value. |
| jane_smith | Cooking Tutorial | 5 | Clear instructions, easy to follow. |
| john_doe | Sunset Over Mountains | 5 | Beautiful artwork, love the colors! |
| music_lover | Sunset Over Mountains | 4 | Nice composition and color palette. |
| music_lover | Chill Lo-Fi Beats | 5 | Perfect for concentration! |

## Statistics

### Content by Category
- Games: 2 (28.6%)
- Videos: 1 (14.3%)
- Artwork: 2 (28.6%)
- Music: 2 (28.6%)

### Rating Distribution
- 5 stars: 5 ratings (55.6%)
- 4 stars: 3 ratings (33.3%)
- 3 stars: 1 rating (11.1%)

### User Activity
- john_doe: 3 ratings (most active)
- jane_smith: 2 ratings
- game_master: 1 rating
- music_lover: 3 ratings

### Content Popularity
- Epic Adventure Game: 3 ratings (most popular)
- Sunset Over Mountains: 2 ratings
- Puzzle Master 3000: 2 ratings

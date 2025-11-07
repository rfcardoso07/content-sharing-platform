# Database Entity Relationship Diagram

## Schema Overview

```
┌─────────────────────────┐
│        USERS            │
├─────────────────────────┤
│ PK user_id (UUID)       │
│    username             │
│    email                │
│    password_hash        │
│    rating_count         │
│    last_login           │
│    created_at           │
│    updated_at           │
└─────────────────────────┘
           │
           │ 1
           │
           │ created_by
           │
           │ N
           ▼
┌─────────────────────────┐
│    MEDIA_CONTENT        │
├─────────────────────────┤
│ PK media_id (UUID)      │
│    title                │
│    description          │
│    category (ENUM)      │
│    thumbnail_url        │
│    content_url          │
│    created_at           │
│    updated_at           │
│ FK user_id              │
└─────────────────────────┘
           │
           │ 1
           │
           │ rated_content
           │
           │ N
           ▼
┌─────────────────────────┐
│       RATINGS           │
├─────────────────────────┤
│ PK rating_id (UUID)     │
│ FK media_id             │
│ FK user_id              │
│    score (1-5)          │
│    comment              │
│    created_at           │
│    updated_at           │
└─────────────────────────┘
           ▲
           │ N
           │
           │ rates
           │
           │ 1
           │
     [USERS table]
```

## Relationships

### 1. Users → Media Content (One-to-Many)
- One user can upload multiple media content items
- Each media content is uploaded by exactly one user
- Cascade delete: If a user is deleted, all their media content is deleted

### 2. Media Content → Ratings (One-to-Many)
- One media content item can have multiple ratings
- Each rating is for exactly one media content item
- Cascade delete: If media content is deleted, all its ratings are deleted

### 3. Users → Ratings (One-to-Many)
- One user can create multiple ratings
- Each rating is created by exactly one user
- Cascade delete: If a user is deleted, all their ratings are deleted
- Unique constraint: A user can rate the same media content only once

## Data Types & Constraints

### Users Table
- **user_id**: UUID, Primary Key, Auto-generated
- **username**: VARCHAR(50), Unique, Not Null
- **email**: VARCHAR(255), Unique, Not Null
- **password_hash**: VARCHAR(255), Not Null, Securely hashed using Werkzeug
- **rating_count**: INTEGER, Default 0, Check >= 0
- **last_login**: TIMESTAMP WITH TIME ZONE, Nullable
- **created_at**: TIMESTAMP WITH TIME ZONE, Auto-generated
- **updated_at**: TIMESTAMP WITH TIME ZONE, Auto-updated via trigger

### Media Content Table
- **media_id**: UUID, Primary Key, Auto-generated
- **title**: VARCHAR(255), Not Null
- **description**: TEXT, Nullable
- **category**: ENUM ('game', 'video', 'artwork', 'music'), Not Null
- **thumbnail_url**: VARCHAR(512), Nullable
- **content_url**: VARCHAR(512), Not Null
- **created_at**: TIMESTAMP WITH TIME ZONE, Auto-generated
- **updated_at**: TIMESTAMP WITH TIME ZONE, Auto-updated via trigger
- **user_id**: UUID, Foreign Key to Users, Not Null

### Ratings Table
- **rating_id**: UUID, Primary Key, Auto-generated
- **media_id**: UUID, Foreign Key to Media Content, Not Null
- **user_id**: UUID, Foreign Key to Users, Not Null
- **score**: INTEGER, Not Null, Check between 1 and 5
- **comment**: TEXT, Nullable
- **created_at**: TIMESTAMP WITH TIME ZONE, Auto-generated
- **updated_at**: TIMESTAMP WITH TIME ZONE, Auto-updated via trigger
- **Unique Constraint**: (media_id, user_id) - prevents duplicate ratings

## Indexes

For optimal query performance, the following indexes are created:

### Media Content
- `idx_media_category` on `category`
- `idx_media_user` on `user_id`
- `idx_media_created_at` on `created_at DESC`

### Ratings
- `idx_ratings_media` on `media_id`
- `idx_ratings_user` on `user_id`

### Users
- `idx_users_username` on `username`
- `idx_users_email` on `email`

## Triggers & Functions

### Auto-update Timestamps
- Function: `update_updated_at_column()`
- Triggers on: users, media_content, ratings tables
- Action: Automatically updates `updated_at` field on any UPDATE operation

### Auto-update Rating Count
- Function: `update_user_rating_count()`
- Trigger on: ratings table
- Action: 
  - Increments user's `rating_count` when a rating is inserted
  - Decrements user's `rating_count` when a rating is deleted

## Category ENUM Values

The `media_category` type accepts only the following values:
- `'game'` - Video games
- `'video'` - Video content
- `'artwork'` - Digital or traditional artwork
- `'music'` - Music files

## Design Decisions

1. **UUID for Primary Keys**: Provides globally unique identifiers, better for distributed systems and prevents enumeration attacks

2. **Timestamps with Time Zone**: Ensures proper handling of different time zones

3. **Auto-incrementing Rating Count**: Improves query performance by avoiding COUNT queries

4. **Cascade Deletes**: Maintains referential integrity automatically

5. **Unique Constraint on Ratings**: Prevents users from rating the same content multiple times

6. **Indexes on Foreign Keys**: Improves JOIN operation performance

7. **ENUM for Categories**: Ensures data integrity and prevents invalid category values

-- Content Sharing Platform Database Schema
-- PostgreSQL Database
-- This file is automatically executed by Docker on first startup

-- Enable UUID extension for generating unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM type for media categories
CREATE TYPE media_category AS ENUM ('game', 'video', 'artwork', 'music');

-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rating_count INTEGER DEFAULT 0 CHECK (rating_count >= 0),
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Media content table
CREATE TABLE media_content (
    media_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category media_category NOT NULL,
    thumbnail_url VARCHAR(512),
    content_url VARCHAR(512) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id UUID NOT NULL,
    CONSTRAINT fk_media_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Ratings table
-- A user can rate media content with a score from 1 to 5
CREATE TABLE ratings (
    rating_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    media_id UUID NOT NULL,
    user_id UUID NOT NULL,
    score INTEGER NOT NULL CHECK (score >= 1 AND score <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rating_media FOREIGN KEY (media_id) REFERENCES media_content(media_id) ON DELETE CASCADE,
    CONSTRAINT fk_rating_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    -- Ensure a user can only rate the same media content once
    CONSTRAINT unique_user_media_rating UNIQUE (media_id, user_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_media_category ON media_content(category);
CREATE INDEX idx_media_user ON media_content(user_id);
CREATE INDEX idx_media_created_at ON media_content(created_at DESC);
CREATE INDEX idx_ratings_media ON ratings(media_id);
CREATE INDEX idx_ratings_user ON ratings(user_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update updated_at column
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_media_content_updated_at
    BEFORE UPDATE ON media_content
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ratings_updated_at
    BEFORE UPDATE ON ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create a function to update user rating_count when a rating is added or deleted
CREATE OR REPLACE FUNCTION update_user_rating_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE users SET rating_count = rating_count + 1 WHERE user_id = NEW.user_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE users SET rating_count = rating_count - 1 WHERE user_id = OLD.user_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update user rating_count
CREATE TRIGGER update_user_rating_count_trigger
    AFTER INSERT OR DELETE ON ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_user_rating_count();

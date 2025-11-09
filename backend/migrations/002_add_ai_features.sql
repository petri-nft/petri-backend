-- Migration: Add AI Personality and Chat Features
-- Supabase PostgreSQL
-- Created: 2025-11-09

-- Create tree_personalities table (1:1 with trees)
CREATE TABLE IF NOT EXISTS tree_personalities (
    id SERIAL PRIMARY KEY,
    tree_id INTEGER NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    tone VARCHAR(50) NOT NULL,
    background TEXT,
    traits JSONB DEFAULT '{}',
    voice_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (tree_id) REFERENCES trees(id) ON DELETE CASCADE
);

-- Create chat_messages table (many:many with trees and users)
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    tree_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    audio_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (tree_id) REFERENCES trees(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_tree_personalities_tree_id ON tree_personalities(tree_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_tree_id ON chat_messages(tree_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at DESC);

-- Add is_public and personality_id columns to trees table if they don't exist
-- NOTE: If trees table is not yet created, this will fail. Run other migrations first.
ALTER TABLE trees ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE;

-- Create trigger to auto-update updated_at on tree_personalities
CREATE OR REPLACE FUNCTION update_tree_personalities_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_tree_personalities_updated_at ON tree_personalities;
CREATE TRIGGER trigger_update_tree_personalities_updated_at
BEFORE UPDATE ON tree_personalities
FOR EACH ROW
EXECUTE FUNCTION update_tree_personalities_updated_at();

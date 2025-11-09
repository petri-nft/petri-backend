-- Add new columns to trees table
-- This migration adds nickname, photo_url, and nft_image_url columns to support:
-- 1. User-given tree names (nicknames)
-- 2. Saving captured photos
-- 3. Saving generated NFT images

ALTER TABLE trees ADD COLUMN IF NOT EXISTS nickname VARCHAR(255);
ALTER TABLE trees ADD COLUMN IF NOT EXISTS photo_url VARCHAR(255);
ALTER TABLE trees ADD COLUMN IF NOT EXISTS nft_image_url VARCHAR(255);

-- Add unique constraint on (user_id, nickname) to ensure no duplicate tree names per user
-- This needs to exclude NULL values, so we'll create a partial unique index
CREATE UNIQUE INDEX IF NOT EXISTS idx_trees_unique_nickname_per_user 
ON trees(user_id, nickname) 
WHERE nickname IS NOT NULL;

-- Add indexes for faster filtering
CREATE INDEX IF NOT EXISTS idx_trees_nickname ON trees(nickname);
CREATE INDEX IF NOT EXISTS idx_trees_photo_url ON trees(photo_url);
CREATE INDEX IF NOT EXISTS idx_trees_nft_image_url ON trees(nft_image_url);

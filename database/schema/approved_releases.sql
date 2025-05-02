-- Schema for the approved_releases table

CREATE TABLE IF NOT EXISTS approved_releases (
    id SERIAL PRIMARY KEY,
    release_id VARCHAR(255) UNIQUE NOT NULL, -- Unique identifier from the workflow (e.g., UUID)
    artist_name VARCHAR(255),
    track_prompt TEXT,                 -- Prompt used for track generation
    video_prompt TEXT,                 -- Prompt used for video generation
    suno_clip_id VARCHAR(255),         -- ID from the Suno API
    track_url TEXT,                    -- URL of the approved track
    video_url TEXT,                    -- URL of the approved video
    approved_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    distribution_status VARCHAR(50) DEFAULT 'pending' -- e.g., pending, scheduled, distributed, error
);

-- Optional: Add index on release_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_approved_releases_release_id ON approved_releases(release_id);

-- Optional: Add index on distribution_status for querying pending releases
CREATE INDEX IF NOT EXISTS idx_approved_releases_distribution_status ON approved_releases(distribution_status);


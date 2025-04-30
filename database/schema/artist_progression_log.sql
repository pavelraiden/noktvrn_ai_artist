-- Schema for tracking artist profile evolution over time

CREATE TABLE IF NOT EXISTS artist_progression_log (
    id SERIAL PRIMARY KEY,                      -- Unique identifier for the log entry
    artist_id INTEGER NOT NULL,                 -- Foreign key linking to the artist (assuming an artists table exists or will exist)
    event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- When the evolution event occurred
    event_description TEXT NOT NULL,            -- Description of the change (e.g., "Added keyword X due to Y")
    performance_summary TEXT,                   -- Optional: Summary of performance data that triggered the change
    profile_snapshot JSONB                      -- Optional: Snapshot of the artist profile *after* the change

    -- Add foreign key constraint if an artists table exists
    -- FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE
);

-- Add indexes separately using standard PostgreSQL syntax
CREATE INDEX IF NOT EXISTS idx_progression_artist_id ON artist_progression_log (artist_id);
CREATE INDEX IF NOT EXISTS idx_progression_timestamp ON artist_progression_log (event_timestamp);


COMMENT ON TABLE artist_progression_log IS 'Stores a log of changes made to artist profiles during the evolution process.';
COMMENT ON COLUMN artist_progression_log.artist_id IS 'Identifier for the artist whose profile was changed.';
COMMENT ON COLUMN artist_progression_log.event_description IS 'Human-readable description of the evolution event and the resulting change.';
COMMENT ON COLUMN artist_progression_log.performance_summary IS 'Brief summary of the performance trend analysis that led to this change.';
COMMENT ON COLUMN artist_progression_log.profile_snapshot IS 'JSON snapshot of the artist profile state after the evolution was applied.';


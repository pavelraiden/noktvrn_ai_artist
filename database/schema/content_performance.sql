-- Schema for tracking content performance metrics

CREATE TABLE IF NOT EXISTS content_performance (
    id SERIAL PRIMARY KEY,                      -- Unique identifier for the performance record
    release_id INTEGER NOT NULL,                -- Foreign key linking to the approved_releases table
    platform VARCHAR(100) NOT NULL,             -- Platform where the content was released (e.g., 'YouTube', 'Spotify', 'TikTok')
    metric_type VARCHAR(50) NOT NULL,           -- Type of metric (e.g., 'views', 'likes', 'shares', 'streams', 'saves')
    metric_value BIGINT NOT NULL,               -- The value of the metric
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- When the metric was recorded
    source_url TEXT,                            -- Optional: URL of the content on the platform
    notes TEXT,                                 -- Optional: Any additional notes

    FOREIGN KEY (release_id) REFERENCES approved_releases(id) ON DELETE CASCADE
    -- UNIQUE constraint removed for simplicity, allowing multiple records over time
);

-- Add indexes separately using standard PostgreSQL syntax
CREATE INDEX IF NOT EXISTS idx_performance_release_id ON content_performance (release_id);
CREATE INDEX IF NOT EXISTS idx_performance_platform ON content_performance (platform);
CREATE INDEX IF NOT EXISTS idx_performance_metric_type ON content_performance (metric_type);
CREATE INDEX IF NOT EXISTS idx_performance_recorded_at ON content_performance (recorded_at);


COMMENT ON TABLE content_performance IS 'Stores performance metrics for released content across different platforms over time.';
COMMENT ON COLUMN content_performance.release_id IS 'Links to the specific release in the approved_releases table.';
COMMENT ON COLUMN content_performance.platform IS 'The distribution platform where the metric was observed (e.g., YouTube, Spotify).';
COMMENT ON COLUMN content_performance.metric_type IS 'The type of performance metric being recorded (e.g., views, likes, streams).';
COMMENT ON COLUMN content_performance.metric_value IS 'The numerical value of the metric recorded.';
COMMENT ON COLUMN content_performance.recorded_at IS 'Timestamp indicating when this metric value was recorded or observed.';
COMMENT ON COLUMN content_performance.source_url IS 'Direct URL to the content on the specified platform, if available.';
COMMENT ON COLUMN content_performance.notes IS 'Optional notes about the metric.'; -- Added comment for notes


-- Schema for the performance_metrics table
-- Stores detailed time-series performance data for tracks

CREATE TABLE IF NOT EXISTS performance_metrics (
    id VARCHAR(255) PRIMARY KEY, -- Unique identifier for the metric entry
    track_id VARCHAR(255) NOT NULL REFERENCES tracks(id) ON DELETE CASCADE,
    artist_id VARCHAR(255) NOT NULL REFERENCES artist_profiles(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL, -- Timestamp for the metric data point
    metric_type VARCHAR(50) NOT NULL, -- Type of metric (e.g., daily_streams, weekly_engagement, monthly_revenue)
    country_code VARCHAR(2), -- Optional: Country context for the metric
    platform VARCHAR(50), -- Optional: Platform context (e.g., spotify, apple_music)
    
    -- Metric value (using JSONB for flexibility in metric structure)
    metric_value JSONB NOT NULL
    -- Example structure:
    -- {"streams": 1000, "listeners": 500}
    -- {"engagement_rate": 0.12}
    -- {"revenue_usd": 5.50}
);

-- Index for faster lookups by track_id and timestamp
CREATE INDEX IF NOT EXISTS idx_performance_metrics_track_time ON performance_metrics(track_id, timestamp DESC);

-- Index for faster lookups by artist_id and timestamp
CREATE INDEX IF NOT EXISTS idx_performance_metrics_artist_time ON performance_metrics(artist_id, timestamp DESC);

-- Index for faster lookups by metric_type and timestamp
CREATE INDEX IF NOT EXISTS idx_performance_metrics_type_time ON performance_metrics(metric_type, timestamp DESC);

-- Index for faster lookups by country_code
CREATE INDEX IF NOT EXISTS idx_performance_metrics_country_code ON performance_metrics(country_code) WHERE country_code IS NOT NULL;

-- Index for faster lookups by platform
CREATE INDEX IF NOT EXISTS idx_performance_metrics_platform ON performance_metrics(platform) WHERE platform IS NOT NULL;

-- Consider using TimescaleDB extension for enhanced time-series capabilities if needed in the future
-- CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
-- SELECT create_hypertable("performance_metrics", "timestamp");

COMMENT ON TABLE performance_metrics IS 'Stores detailed time-series performance metrics for tracks across different dimensions like time, country, and platform.';
COMMENT ON COLUMN performance_metrics.metric_type IS 'Categorizes the type of performance metric being recorded (e.g., daily_streams, weekly_engagement).';
COMMENT ON COLUMN performance_metrics.metric_value IS 'Flexible JSONB field storing the actual value(s) of the recorded metric.';


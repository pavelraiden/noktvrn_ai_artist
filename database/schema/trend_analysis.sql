-- Schema for the trend_analysis table
-- This table stores results from various analysis processes (self-learning, competitor, market)

CREATE TABLE IF NOT EXISTS trend_analysis (
    id VARCHAR(255) PRIMARY KEY, -- Unique identifier for the analysis result
    analysis_type VARCHAR(50) NOT NULL, -- Type of analysis (e.g., self_learning, competitor, market_genre, market_country)
    artist_id VARCHAR(255) REFERENCES artist_profiles(id) ON DELETE CASCADE, -- Optional: Link to artist if analysis is artist-specific
    country_code VARCHAR(2), -- Optional: Link to country if analysis is country-specific
    genre VARCHAR(100), -- Optional: Genre context for the analysis
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Analysis inputs/context (using JSONB)
    analysis_context JSONB, 
    -- Example structure:
    -- {
    --   "time_period_days": 7,
    --   "track_ids_analyzed": ["track1", "track2"],
    --   "competitor_ids_analyzed": ["comp1", "comp2"],
    --   "data_sources": ["spotify_charts", "internal_metrics"]
    -- }

    -- Analysis results (using JSONB)
    analysis_results JSONB NOT NULL
    -- Example structure (self-learning):
    -- {
    --   "positive_correlations": [{"feature": "bpm", "value": 120, "metric": "engagement_rate", "strength": 0.7}],
    --   "negative_correlations": [...],
    --   "key_success_factors": ["high_energy", "minor_key"],
    --   "areas_for_improvement": ["low_danceability"]
    -- }
    -- Example structure (competitor):
    -- {
    --   "trending_features": [{"feature": "bpm", "trend": "increasing", "value": 135}],
    --   "dominant_themes": ["cyberpunk", "racing"],
    --   "emerging_subgenres": ["hyperwave"]
    -- }
);

-- Index for faster lookups by analysis_type and timestamp
CREATE INDEX IF NOT EXISTS idx_trend_analysis_type_time ON trend_analysis(analysis_type, timestamp DESC);

-- Index for faster lookups by artist_id
CREATE INDEX IF NOT EXISTS idx_trend_analysis_artist_id ON trend_analysis(artist_id) WHERE artist_id IS NOT NULL;

-- Index for faster lookups by country_code
CREATE INDEX IF NOT EXISTS idx_trend_analysis_country_code ON trend_analysis(country_code) WHERE country_code IS NOT NULL;

-- Index for faster lookups by genre
CREATE INDEX IF NOT EXISTS idx_trend_analysis_genre ON trend_analysis(genre) WHERE genre IS NOT NULL;

COMMENT ON TABLE trend_analysis IS 'Stores results from various trend analysis processes, including self-learning, competitor analysis, and market trends.';
COMMENT ON COLUMN trend_analysis.analysis_type IS 'Categorizes the type of analysis performed (e.g., self_learning, competitor).';
COMMENT ON COLUMN trend_analysis.analysis_context IS 'Flexible JSONB field storing the context and inputs used for the analysis.';
COMMENT ON COLUMN trend_analysis.analysis_results IS 'Flexible JSONB field storing the detailed results and insights from the analysis.';


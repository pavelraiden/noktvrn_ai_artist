-- Schema for the competitor_analysis table

CREATE TABLE IF NOT EXISTS competitor_analysis (
    id VARCHAR(255) PRIMARY KEY, -- Unique identifier for the analysis entry
    analysis_run_id VARCHAR(255) NOT NULL, -- Groups analyses performed at the same time
    competitor_artist_id VARCHAR(255), -- Identifier for the competitor artist (if known)
    competitor_artist_name VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL, -- Genre context of the analysis
    country_code VARCHAR(2), -- Optional: Country context if analysis is country-specific
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Data source information
    data_source VARCHAR(100), -- e.g., spotify_api, apple_music_api, manual
    
    -- Competitor profile information (using JSONB)
    competitor_profile JSONB, 
    -- Example structure:
    -- {
    --   "platform_url": "https://spotify.com/artist/...",
    --   "follower_count": 100000,
    --   "monthly_listeners": 500000,
    --   "bio_summary": "..."
    -- }

    -- Recent track analysis (using JSONB)
    recent_track_analysis JSONB, 
    -- Example structure:
    -- {
    --   "track_title": "Future Grid",
    --   "release_date": "...",
    --   "audio_features": {"bpm": 130, "energy": 0.85, ...},
    --   "lyrical_themes": ["cyberpunk", "racing"],
    --   "visual_themes": ["neon", "sci-fi"],
    --   "performance_metrics": {"chart_position": 10, "playlist_adds": 500}
    -- }

    -- Overall trend analysis summary (using JSONB)
    trend_summary JSONB 
    -- Example structure:
    -- {
    --   "audio_feature_trends": [{"feature": "bpm", "trend": "increasing"}],
    --   "thematic_trends": ["dystopian", "retro-futurism"],
    --   "visual_style_trends": ["glitch art", "dark neon"]
    -- }
);

-- Index for faster lookups by analysis_run_id
CREATE INDEX IF NOT EXISTS idx_competitor_analysis_run_id ON competitor_analysis(analysis_run_id);

-- Index for faster lookups by competitor_artist_name and genre
CREATE INDEX IF NOT EXISTS idx_competitor_analysis_name_genre ON competitor_analysis(competitor_artist_name, genre);

-- Index for faster lookups by timestamp
CREATE INDEX IF NOT EXISTS idx_competitor_analysis_timestamp ON competitor_analysis(timestamp DESC);

-- Index for faster lookups by country_code
CREATE INDEX IF NOT EXISTS idx_competitor_analysis_country_code ON competitor_analysis(country_code) WHERE country_code IS NOT NULL;

COMMENT ON TABLE competitor_analysis IS 'Stores detailed information about competitor artists, their recent tracks, and associated trends within a specific genre and market.';
COMMENT ON COLUMN competitor_analysis.competitor_profile IS 'Flexible JSONB field storing profile information about the competitor artist.';
COMMENT ON COLUMN competitor_analysis.recent_track_analysis IS 'Flexible JSONB field storing analysis results for the competitor\'s recent tracks.';
COMMENT ON COLUMN competitor_analysis.trend_summary IS 'Flexible JSONB field summarizing observed trends based on the competitor analysis.';


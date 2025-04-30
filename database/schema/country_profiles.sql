-- Schema for the country_profiles table

CREATE TABLE IF NOT EXISTS country_profiles (
    id VARCHAR(255) PRIMARY KEY, -- Unique identifier for the country profile entry (e.g., country_code + timestamp)
    country_code VARCHAR(2) NOT NULL, -- ISO 3166-1 alpha-2 country code (e.g., US, GB, DE)
    country_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Market data (using JSONB for flexibility)
    market_data JSONB, 
    -- Example structure:
    -- {
    --   "streaming_platforms": ["spotify", "apple_music"],
    --   "language": "en",
    --   "timezone": "America/New_York",
    --   "population_estimate": 330000000,
    --   "gdp_per_capita": 65000
    -- }

    -- Genre preferences and trends (using JSONB)
    genre_trends JSONB, 
    -- Example structure:
    -- {
    --   "top_genres": [{"genre": "pop", "rank": 1}, {"genre": "hip-hop", "rank": 2}],
    --   "trending_genres": [{"genre": "hyperpop", "change": 0.15}, {"genre": "synthwave", "change": 0.05}],
    --   "platform_specific_trends": {
    --     "spotify": {"top_genres": [...], "trending_genres": [...]},
    --     "apple_music": {"top_genres": [...], "trending_genres": [...]}
    --   },
    --   "last_updated": "..."
    -- }

    -- Audience demographics (using JSONB)
    audience_demographics JSONB 
    -- Example structure:
    -- {
    --   "age_distribution": {"18-24": 0.3, "25-34": 0.4, ...},
    --   "gender_distribution": {"male": 0.55, "female": 0.45},
    --   "platform_preference": {"spotify": 0.6, "apple_music": 0.3, ...}
    -- }
);

-- Index for faster lookups by country_code
CREATE INDEX IF NOT EXISTS idx_country_profiles_country_code ON country_profiles(country_code);

-- Index for faster lookups by updated_at for time-series analysis
CREATE INDEX IF NOT EXISTS idx_country_profiles_updated_at ON country_profiles(updated_at DESC);

-- Trigger to automatically update updated_at on row update
CREATE TRIGGER update_country_profiles_updated_at
BEFORE UPDATE ON country_profiles
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column(); -- Reuse function from artist_profiles.sql

COMMENT ON TABLE country_profiles IS 'Stores market data, genre trends, and audience demographics for different countries.';
COMMENT ON COLUMN country_profiles.market_data IS 'Flexible JSONB field for general market information like platforms, language, etc.';
COMMENT ON COLUMN country_profiles.genre_trends IS 'Flexible JSONB field storing top and trending genres, potentially platform-specific.';
COMMENT ON COLUMN country_profiles.audience_demographics IS 'Flexible JSONB field for audience demographic information like age and gender distribution.';


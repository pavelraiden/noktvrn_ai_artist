-- Schema for the artist_profiles table

CREATE TABLE IF NOT EXISTS artist_profiles (
    id VARCHAR(255) PRIMARY KEY, -- Unique identifier for the artist
    name VARCHAR(255) NOT NULL, -- Artist's name
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Persona details (using JSONB for flexibility)
    persona JSONB, 
    -- Example structure: 
    -- {
    --   "description": "A retro-futuristic AI...",
    --   "keywords": ["retro", "synthwave"],
    --   "diary": [{"timestamp": "...", "event": "..."}]
    -- }

    -- Music style details (using JSONB)
    music_style JSONB, 
    -- Example structure:
    -- {
    --   "genres": ["synthwave", "electronic"],
    --   "subgenres": ["outrun"],
    --   "moods": ["nostalgic", "energetic"],
    --   "tempo_range": [100, 140],
    --   "instrumentation": ["synthesizer", "drum machine"],
    --   "vocals": {"type": "instrumental"},
    --   "languages": ["en"],
    --   "lyrical_themes": ["nostalgia", "technology"]
    -- }

    -- Visual identity details (using JSONB)
    visual_identity JSONB, 
    -- Example structure:
    -- {
    --   "style": "neon noir",
    --   "color_palette": ["#FF00FF", "#00FFFF"],
    --   "themes": ["retro cars", "neon grids"]
    -- }

    -- Evolution state tracking (using JSONB)
    evolution_state JSONB 
    -- Example structure:
    -- {
    --   "generation": 1,
    --   "last_adaptation_plan_id": "plan_xyz",
    --   "last_country_strategies_id": "strat_abc",
    --   "last_prompt_adaptation_id": "prompt_123",
    --   "last_profile_evolution_id": "prof_456",
    --   "last_self_learning_analysis_id": "self_789",
    --   "last_competitor_analysis_id": "comp_101"
    -- }
);

-- Index for faster lookups by name
CREATE INDEX IF NOT EXISTS idx_artist_profiles_name ON artist_profiles(name);

-- Trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at on row update
CREATE TRIGGER update_artist_profiles_updated_at
BEFORE UPDATE ON artist_profiles
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE artist_profiles IS 'Stores core information about each AI artist, including their persona, style, and evolution state.';
COMMENT ON COLUMN artist_profiles.persona IS 'Flexible JSONB field for artist persona details like description, keywords, and diary entries.';
COMMENT ON COLUMN artist_profiles.music_style IS 'Flexible JSONB field for music style details like genres, moods, tempo, etc.';
COMMENT ON COLUMN artist_profiles.visual_identity IS 'Flexible JSONB field for visual identity details like style, color palette, themes.';
COMMENT ON COLUMN artist_profiles.evolution_state IS 'Flexible JSONB field tracking the artist''s evolution progress and linking to related analysis/plan IDs.';


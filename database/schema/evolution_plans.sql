-- Schema for the evolution_plans table

CREATE TABLE IF NOT EXISTS evolution_plans (
    id VARCHAR(255) PRIMARY KEY, -- Unique identifier for the evolution plan
    artist_id VARCHAR(255) NOT NULL REFERENCES artist_profiles(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    plan_version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'pending', -- e.g., pending, approved, implemented, rejected

    -- Input analysis IDs (links to the analysis that informed this plan)
    self_learning_analysis_id VARCHAR(255) REFERENCES trend_analysis(id),
    competitor_analysis_run_id VARCHAR(255), -- Links to a group of competitor analyses
    country_strategy_id VARCHAR(255), -- Link to relevant country strategies

    -- High-level goals for this evolution cycle (using JSONB)
    evolution_goals JSONB, 
    -- Example structure:
    -- {
    --   "primary_goal": "Increase engagement in US market",
    --   "secondary_goals": ["Explore hyperpop elements", "Improve lyrical complexity"],
    --   "target_metrics": {"engagement_rate_us": 0.20, "streams_hyperpop": 100000}
    -- }

    -- Specific adaptation directives (using JSONB)
    adaptation_directives JSONB NOT NULL
    -- Example structure:
    -- [
    --   {"area": "music_style", "parameter": "tempo_range", "action": "shift", "value": [110, 150], "priority": 1, "constraint": "gradual"},
    --   {"area": "persona", "parameter": "keywords", "action": "add", "value": "hyperpop", "priority": 2},
    --   {"area": "visual_identity", "parameter": "themes", "action": "add", "value": "glitch art", "priority": 3}
    -- ]
);

-- Index for faster lookups by artist_id and timestamp
CREATE INDEX IF NOT EXISTS idx_evolution_plans_artist_time ON evolution_plans(artist_id, timestamp DESC);

-- Index for faster lookups by status
CREATE INDEX IF NOT EXISTS idx_evolution_plans_status ON evolution_plans(status);

COMMENT ON TABLE evolution_plans IS 'Stores the strategic plans generated for artist evolution, including goals and specific adaptation directives.';
COMMENT ON COLUMN evolution_plans.evolution_goals IS 'Flexible JSONB field outlining the high-level objectives for the evolution cycle.';
COMMENT ON COLUMN evolution_plans.adaptation_directives IS 'Flexible JSONB field containing specific, actionable directives for adapting the artist\''s profile, style, or content generation.';


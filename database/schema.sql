-- Drop tables with CASCADE to remove all dependencies
DROP TABLE IF EXISTS fact_player_seasons CASCADE;
DROP TABLE IF EXISTS dim_players CASCADE;

-- Players dimension table
CREATE TABLE dim_players (
    player_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    position TEXT NOT NULL CHECK (position IN ('QB', 'WR')),
    draft_year INTEGER,
    height INTEGER,
    weight INTEGER,
    current_team TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Season stats fact table with correct INTEGER types
CREATE TABLE fact_player_seasons (
    player_id TEXT REFERENCES dim_players(player_id),
    season_year INTEGER,
    team TEXT,
    games INTEGER DEFAULT 0,
    snaps INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    completions INTEGER DEFAULT 0,
    yards INTEGER DEFAULT 0,
    tds INTEGER DEFAULT 0,
    ints INTEGER DEFAULT 0,
    snap_efficiency NUMERIC(6,4),
    yards_per_attempt NUMERIC(5,2),
    weekly_cv NUMERIC(6,4),
    consistency_score NUMERIC(5,2),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (player_id, season_year)
);

-- Indexes for performance
CREATE INDEX idx_players_position ON dim_players(position);
CREATE INDEX idx_seasons_year ON fact_player_seasons(season_year);
CREATE INDEX idx_seasons_player ON fact_player_seasons(player_id);
-- ============================================
-- LEADERBOARD VIEWS FOR STREAMLIT APP
-- ============================================

-- Drop existing views if they exist
DROP VIEW IF EXISTS vw_leaderboard_qb_snap_efficiency_1yr;
DROP VIEW IF EXISTS vw_leaderboard_qb_snap_efficiency_5yr;
DROP VIEW IF EXISTS vw_leaderboard_qb_snap_efficiency_career;
DROP VIEW IF EXISTS vw_leaderboard_qb_consistency_1yr;
DROP VIEW IF EXISTS vw_leaderboard_qb_consistency_5yr;
DROP VIEW IF EXISTS vw_leaderboard_qb_consistency_career;
DROP VIEW IF EXISTS vw_leaderboard_wr_snap_efficiency_1yr;
DROP VIEW IF EXISTS vw_leaderboard_wr_snap_efficiency_5yr;
DROP VIEW IF EXISTS vw_leaderboard_wr_snap_efficiency_career;
DROP VIEW IF EXISTS vw_leaderboard_wr_consistency_1yr;
DROP VIEW IF EXISTS vw_leaderboard_wr_consistency_5yr;
DROP VIEW IF EXISTS vw_leaderboard_wr_consistency_career;

-- ============================================
-- QB SNAP EFFICIENCY LEADERBOARDS
-- ============================================

-- 1 Year (most recent season available)
CREATE VIEW vw_leaderboard_qb_snap_efficiency_1yr AS
SELECT 
    p.player_id,
    p.name,
    s.season_year::text as period,
    ROUND(s.snap_efficiency::numeric, 4) as value,
    RANK() OVER (ORDER BY s.snap_efficiency DESC) as rank
FROM fact_player_seasons s
JOIN dim_players p ON s.player_id = p.player_id
WHERE p.position = 'QB'
AND s.season_year = (SELECT MAX(season_year) FROM fact_player_seasons)
ORDER BY s.snap_efficiency DESC
LIMIT 30;

-- 5 Year (2019-2023)
CREATE VIEW vw_leaderboard_qb_snap_efficiency_5yr AS
SELECT 
    p.player_id,
    p.name,
    '2019-2023' as period,
    ROUND(AVG(s.snap_efficiency)::numeric, 4) as value,
    RANK() OVER (ORDER BY AVG(s.snap_efficiency) DESC) as rank
FROM fact_player_seasons s
JOIN dim_players p ON s.player_id = p.player_id
WHERE p.position = 'QB' 
AND s.season_year BETWEEN 2019 AND 2023
GROUP BY p.player_id, p.name
ORDER BY value DESC
LIMIT 30;

-- Career (all available seasons)
CREATE VIEW vw_leaderboard_qb_snap_efficiency_career AS
SELECT 
    p.player_id,
    p.name,
    'Career' as period,
    ROUND(AVG(s.snap_efficiency)::numeric, 4) as value,
    RANK() OVER (ORDER BY AVG(s.snap_efficiency) DESC) as rank
FROM fact_player_seasons s
JOIN dim_players p ON s.player_id = p.player_id
WHERE p.position = 'QB'
GROUP BY p.player_id, p.name
ORDER BY value DESC
LIMIT 30;

-- ============================================
-- QB CONSISTENCY SCORE LEADERBOARDS
-- ============================================

-- 1 Year
CREATE VIEW vw_leaderboard_qb_consistency_1yr AS
SELECT 
    p.player_id,
    p.name,
    s.season_year::text as period,
    ROUND(s.consistency_score::numeric, 2) as value,
    RANK() OVER (ORDER BY s.consistency_score DESC) as rank
FROM fact_player_seasons s
JOIN dim_players p ON s.player_id = p.player_id
WHERE p.position = 'QB'
AND s.season_year = (SELECT MAX(season_year) FROM fact_player_seasons)
ORDER BY s.consistency_score DESC
LIMIT 30;

-- 5 Year
CREATE VIEW vw_leaderboard_qb_consistency_5yr AS
SELECT 
    p.player_id,
    p.name,
    '2019-2023' as period,
    ROUND(AVG(s.consistency_score)::numeric, 2) as value,
    RANK() OVER (ORDER BY AVG(s.consistency_score) DESC) as rank
FROM fact_player_seasons s
JOIN dim_players p ON s.player_id = p.player_id
WHERE p.position = 'QB' 
AND s.season_year BETWEEN 2019 AND 2023
GROUP BY p.player_id, p.name
ORDER BY value DESC
LIMIT 30;

-- Career
CREATE VIEW vw_leaderboard_qb_consistency_career AS
SELECT 
    p.player_id,
    p.name,
    'Career' as period,
    ROUND(AVG(s.consistency_score)::numeric, 2) as value,
    RANK() OVER (ORDER BY AVG(s.consistency_score) DESC) as rank
FROM fact_player_seasons s
JOIN dim_players p ON s.player_id = p.player_id
WHERE p.position = 'QB'
GROUP BY p.player_id, p.name
ORDER BY value DESC
LIMIT 30;

-- ============================================
-- WR SNAP EFFICIENCY LEADERBOARDS
-- ============================================

-- 1 Year
CREATE VIEW vw_leaderboard_wr_snap_efficiency_1yr AS
SELECT 
    p.player_id,
    p.name,
    s.season_year::text as period,
    ROUND(s.snap_efficiency::numeric, 4) as value,
    RANK() OVER (ORDER BY s.snap_efficiency DESC) as rank
FROM fact_player_seasons s
JOIN dim_players p ON s.player_id = p.player_id
WHERE p.position = 'WR'
AND s.season_year = (SELECT MAX(season_year) FROM fact_player_seasons)
ORDER BY s.snap_efficiency DESC
LIMIT 30;

-- 5 Year
CREATE VIEW vw_leaderboard_wr_snap_efficiency_5yr AS
SELECT 
    p.player_id,
    p.name,
    '2019-2023' as period,
    ROUND(AVG(s.snap_efficiency)::numeric, 4) as value,
    RANK() OVER (ORDER BY AVG(s.snap_efficiency) DESC) as rank
FROM fact_player_seasons s
JOIN dim_players p ON s.player_id = p.player_id
WHERE p.position = 'WR' 
AND s.season_year BETWEEN 2019 AND 2023
GROUP BY p.player_id, p.name
ORDER BY value DESC
LIMIT 30;

-- Career
CREATE VIEW vw_leaderboard_wr_snap_efficiency_career AS
SELECT 
    p.player_id,
    p.name,
    'Career' as period,
    ROUND(AVG(s.snap_efficiency)::numeric, 4) as value,
    RANK() OVER (ORDER BY AVG(s.snap_efficiency) DESC) as rank
FROM fact_player_seasons s
JOIN dim_players p ON s.player_id = p.player_id
WHERE p.position = 'WR'
GROUP BY p.player_id, p.name
ORDER BY value DESC
LIMIT 30;

-- ============================================
-- WR CONSISTENCY SCORE LEADERBOARDS
-- ============================================

-- 1 Year
CREATE VIEW vw_leaderboard_wr_consistency_1yr AS
SELECT 
    p.player_id,
    p.name,
    s.season_year::text as period,
    ROUND(s.consistency_score::numeric, 2) as value,
    RANK() OVER (ORDER BY s.consistency_score DESC) as rank
FROM fact_player_seasons s
JOIN dim_players p ON s.player_id = p.player_id
WHERE p.position = 'WR'
AND s.season_year = (SELECT MAX(season_year) FROM fact_player_seasons)
ORDER BY s.consistency_score DESC
LIMIT 30;

-- 5 Year
CREATE VIEW vw_leaderboard_wr_consistency_5yr AS
SELECT 
    p.player_id,
    p.name,
    '2019-2023' as period,
    ROUND(AVG(s.consistency_score)::numeric, 2) as value,
    RANK() OVER (ORDER BY AVG(s.consistency_score) DESC) as rank
FROM fact_player_seasons s
JOIN dim_players p ON s.player_id = p.player_id
WHERE p.position = 'WR' 
AND s.season_year BETWEEN 2019 AND 2023
GROUP BY p.player_id, p.name
ORDER BY value DESC
LIMIT 30;

-- Career
CREATE VIEW vw_leaderboard_wr_consistency_career AS
SELECT 
    p.player_id,
    p.name,
    'Career' as period,
    ROUND(AVG(s.consistency_score)::numeric, 2) as value,
    RANK() OVER (ORDER BY AVG(s.consistency_score) DESC) as rank
FROM fact_player_seasons s
JOIN dim_players p ON s.player_id = p.player_id
WHERE p.position = 'WR'
GROUP BY p.player_id, p.name
ORDER BY value DESC
LIMIT 30;
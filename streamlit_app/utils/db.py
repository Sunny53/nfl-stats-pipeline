import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from etl.load import get_engine

def get_leaderboard(position: str, metric: str, split: str) -> pd.DataFrame:
    """Query leaderboard view from database."""
    # Map display names to actual view names
    metric_map = {
        "Snap Efficiency": "snap_efficiency",
        "Consistency Score": "consistency"  # Note: no "_score" suffix
    }
    
    metric_clean = metric_map.get(metric, metric.lower().replace(' ', '_'))
    split_clean = split.lower().replace('/', '')
    
    view_name = f"vw_leaderboard_{position.lower()}_{metric_clean}_{split_clean}"
    
    engine = get_engine()
    query = f"SELECT * FROM {view_name} LIMIT 30"
    
    return pd.read_sql(query, engine)

def search_player(player_name: str):
    """Search for player by name."""
    engine = get_engine()
    query = """
        SELECT p.*, 
               s.season_year, s.team, s.games, s.snap_efficiency, s.consistency_score
        FROM dim_players p
        LEFT JOIN fact_player_seasons s ON p.player_id = s.player_id
        WHERE p.name ILIKE %s
        ORDER BY s.season_year DESC
    """
    return pd.read_sql(query, engine, params=(f"%{player_name}%",))

def get_player_career_stats(player_id: str):
    """Get career stats for a player."""
    engine = get_engine()
    query = """
        SELECT season_year, team, games, snaps, yards, tds,
               snap_efficiency, consistency_score
        FROM fact_player_seasons
        WHERE player_id = %s
        ORDER BY season_year
    """
    return pd.read_sql(query, engine, params=(player_id,))
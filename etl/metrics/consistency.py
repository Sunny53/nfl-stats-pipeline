import pandas as pd
import numpy as np

def calculate_consistency(weekly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate consistency score from weekly data.
    """
    # First, standardize weekly data to have 'yards' column
    df = weekly_df.copy()
    
    # Map QB and WR yards to common 'yards' column
    df['yards'] = 0
    qb_mask = df['position'] == 'QB'
    wr_mask = df['position'] == 'WR'
    
    if 'passing_yards' in df.columns:
        df.loc[qb_mask, 'yards'] = df.loc[qb_mask, 'passing_yards']
    if 'receiving_yards' in df.columns:
        df.loc[wr_mask, 'yards'] = df.loc[wr_mask, 'receiving_yards']
    
    # Group by player and season - drop groups to avoid deprecation warning
    grouped = df.groupby(['player_id', 'season'])
    
    results = []
    for (player_id, season), group in grouped:
        result = calculate_player_consistency(group)
        result['player_id'] = player_id
        result['season'] = season
        results.append(result)
    
    consistency = pd.DataFrame(results)
    return consistency

def calculate_player_consistency(player_weeks: pd.DataFrame) -> pd.Series:
    """Calculate consistency metrics for a single player-season."""
    yards = player_weeks['yards'].fillna(0)
    
    if len(yards) < 4:  # Minimum sample size
        return pd.Series({
            'weekly_std': 0,
            'weekly_mean': yards.mean(),
            'weekly_cv': 0,
            'consistency_score': 50
        })
    
    std = yards.std()
    mean = yards.mean()
    cv = std / mean if mean > 0 else 0
    
    # Convert CV to 0-100 score (lower CV = higher score)
    score = max(0, min(100, 100 - (cv * 50)))
    
    return pd.Series({
        'weekly_std': round(std, 4),
        'weekly_mean': round(mean, 4),
        'weekly_cv': round(cv, 4),
        'consistency_score': round(score, 2)
    })
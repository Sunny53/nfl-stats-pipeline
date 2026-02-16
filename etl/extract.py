import nfl_data_py as nfl
import pandas as pd

def extract_all_data():
    """
    Extract NFL weekly data for QB and WR positions.
    Returns weekly game-by-game data.
    """
    seasons = list(range(2015, 2024))
    
    print(f"Downloading {len(seasons)} seasons...")
    weekly = nfl.import_weekly_data(seasons)
    
    # Filter to QB/WR only
    weekly_qb_wr = weekly[weekly['position'].isin(['QB', 'WR'])].copy()
    
    print(f"Total weekly: {len(weekly)}, QB/WR: {len(weekly_qb_wr)}")
    
    return weekly_qb_wr
import pandas as pd

def aggregate_weekly_to_seasonal(weekly_df):
    """
    Aggregate weekly data to season totals by player.
    """
    # Group by player and season, sum volume stats
    seasonal = weekly_df.groupby(['player_id', 'season']).agg({
        'player_name': 'first',
        'position': 'first',
        'recent_team': 'first',
        'week': 'nunique',  # This counts games played
        # QB passing stats
        'attempts': 'sum',
        'completions': 'sum',
        'passing_yards': 'sum',
        'passing_tds': 'sum',
        'interceptions': 'sum',
        # WR receiving stats
        'targets': 'sum',
        'receptions': 'sum',
        'receiving_yards': 'sum',
        'receiving_tds': 'sum',
    }).reset_index()
    
    # Rename week column to games
    seasonal = seasonal.rename(columns={'week': 'games'})
    
    return seasonal

def calculate_metrics(df):
    """
    Calculate efficiency metrics.
    """
    # Estimate snaps based on position
    df['snaps'] = df.apply(
        lambda x: x['games'] * 60 if x['position'] == 'QB' else x['games'] * 50,
        axis=1
    )
    
    # Set yards, tds, ints based on position
    qb_mask = df['position'] == 'QB'
    df.loc[qb_mask, 'yards'] = df.loc[qb_mask, 'passing_yards']
    df.loc[qb_mask, 'tds'] = df.loc[qb_mask, 'passing_tds']
    df.loc[qb_mask, 'ints'] = df.loc[qb_mask, 'interceptions'].fillna(0)
    
    wr_mask = df['position'] == 'WR'
    df.loc[wr_mask, 'yards'] = df.loc[wr_mask, 'receiving_yards']
    df.loc[wr_mask, 'tds'] = df.loc[wr_mask, 'receiving_tds']
    df.loc[wr_mask, 'ints'] = 0
    
    # Calculate efficiency
    df['snap_efficiency'] = (df['yards'] / df['snaps']).round(4)
    df['yards_per_attempt'] = (df['yards'] / df['attempts'].replace(0, pd.NA)).fillna(0).round(2)
    
    # Placeholder for consistency
    df['consistency_score'] = 50.0
    df['weekly_cv'] = 0.0
    
    return df

def apply_thresholds(df):
    """
    Filter to qualified players only.
    QB: 200+ pass attempts, WR: 40+ targets
    """
    qb_qualified = (df['position'] == 'QB') & (df['attempts'] >= 200)
    wr_qualified = (df['position'] == 'WR') & (df['targets'] >= 40)
    
    qualified = df[qb_qualified | wr_qualified].copy()
    
    qb_count = (qualified['position'] == 'QB').sum()
    wr_count = (qualified['position'] == 'WR').sum()
    print(f"Qualified: {len(qualified)} (QB: {qb_count}, WR: {wr_count})")
    
    return qualified

def transform_data(weekly_df):
    """
    Main transform: weekly -> seasonal -> metrics -> thresholds
    """
    print("Aggregating to seasonal...")
    seasonal = aggregate_weekly_to_seasonal(weekly_df)
    
    print("Calculating metrics...")
    with_metrics = calculate_metrics(seasonal)
    
    print("Applying thresholds...")
    qualified = apply_thresholds(with_metrics)
    
    # Drop records with missing player names
    qualified = qualified[qualified['player_name'].notna()].copy()
    
    if len(qualified) == 0:
        print("WARNING: No qualified players with valid names!")
        return pd.DataFrame(), pd.DataFrame()
    
    # Format for database - ensure correct types
    result = pd.DataFrame({
        'player_id': qualified['player_id'],
        'season_year': qualified['season'].astype(int),
        'team': qualified['recent_team'],
        'games': qualified['games'].astype(int),
        'snaps': qualified['snaps'].astype(int),
        'attempts': qualified['attempts'].astype(int),
        'completions': qualified['completions'].astype(int),
        'yards': qualified['yards'].astype(int),  # Integer now
        'tds': qualified['tds'].astype(int),
        'ints': qualified['ints'].astype(int),
        'snap_efficiency': qualified['snap_efficiency'].astype(float),
        'yards_per_attempt': qualified['yards_per_attempt'].astype(float),
        'weekly_cv': qualified['weekly_cv'].astype(float),
        'consistency_score': qualified['consistency_score'].astype(float)
    })
    
    # Player dimension table
    players = qualified[['player_id', 'player_name', 'position']].drop_duplicates()
    players = players.rename(columns={'player_name': 'name'})
    players['draft_year'] = None
    players['height'] = None
    players['weight'] = None
    players['current_team'] = None
    
    print(f"\nFinal: {len(result)} records, {len(players)} players")
    
    print(f"\nData types:\n{result.dtypes}")
    print(f"\nSnaps max: {result['snaps'].max()}")
    print(f"Yards max: {result['yards'].max()}")

    return players, result
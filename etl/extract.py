import nflreadpy as nfl
import pandas as pd
import datetime


def _to_pandas(data):
    if hasattr(data, "to_pandas"):
        return data.to_pandas()
    return data


def extract_all_data():
    """
    Extract NFL weekly data for QB and WR positions with real snap counts.
    - Regular season only
    - Dynamic season range (2015 → last completed season)
    - Real snap counts via pfr_id crosswalk
    - Players with no snap data are dropped
    """
    current_season = getattr(nfl, "get_current_season", lambda: datetime.datetime.now().year)()
    last_completed_season = current_season - 1
    seasons = list(range(2015, last_completed_season + 1))

    print(f"Downloading {len(seasons)} seasons ({seasons[0]}-{seasons[-1]})...")

    # --- Weekly data (regular season only) ---
    weekly = _to_pandas(nfl.load_player_stats(seasons))
    if 'season_type' not in weekly.columns:
        raise KeyError("nflreadpy player stats are missing the 'season_type' column")
    weekly = weekly[weekly['season_type'] == 'REG']
    for column in ['attempts', 'targets', 'offense_snaps']:
        if column not in weekly.columns:
            if column == 'offense_snaps':
                continue
            raise KeyError(f"nflreadpy player stats are missing the '{column}' column")
    weekly_qb_wr = weekly[weekly['position'].isin(['QB', 'WR'])].copy()
    print(f"Weekly (REG, QB/WR): {len(weekly_qb_wr)} rows")

    # --- Snap counts (regular season only) ---
    print("Downloading snap counts...")
    snaps = _to_pandas(nfl.load_snap_counts(seasons))
    if 'game_type' not in snaps.columns:
        raise KeyError("nflreadpy snap counts are missing the 'game_type' column")
    snaps = snaps[snaps['game_type'] == 'REG']
    snaps = snaps[['pfr_player_id', 'season', 'week', 'offense_snaps']].copy()
    print(f"Snap counts (REG): {len(snaps)} rows")

    # --- ID crosswalk: pfr_id -> gsis_id ---
    print("Downloading ID crosswalk...")
    ids = _to_pandas(nfl.load_ff_playerids())
    if 'pfr_id' not in ids.columns or 'gsis_id' not in ids.columns:
        raise KeyError("nflreadpy player IDs are missing 'pfr_id' or 'gsis_id'")
    crosswalk = ids[['pfr_id', 'gsis_id']].dropna(subset=['pfr_id', 'gsis_id'])
    crosswalk = crosswalk.drop_duplicates(subset='pfr_id')

    # Map pfr_player_id -> gsis_id on snap counts
    snaps = snaps.merge(crosswalk, left_on='pfr_player_id', right_on='pfr_id', how='left')
    snaps = snaps.dropna(subset=['gsis_id'])
    snaps = snaps[['gsis_id', 'season', 'week', 'offense_snaps']]
    print(f"Snap counts after ID mapping: {len(snaps)} rows")

    # --- Merge snap counts onto weekly data ---
    weekly_qb_wr = weekly_qb_wr.merge(
        snaps,
        left_on=['player_id', 'season', 'week'],
        right_on=['gsis_id', 'season', 'week'],
        how='inner'  # inner = drop players with no snap data
    )
    print(f"Weekly after snap merge (inner): {len(weekly_qb_wr)} rows")

    return weekly_qb_wr
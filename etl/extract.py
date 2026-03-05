import nfl_data_py as nfl
import pandas as pd
import datetime


def extract_all_data():
    """
    Extract NFL weekly data for QB and WR positions with real snap counts.
    - Regular season only
    - Dynamic season range (2015 → last completed season)
    - Real snap counts via pfr_id crosswalk
    - Players with no snap data are dropped
    """
    current_year = datetime.datetime.now().year
    seasons = list(range(2015, current_year-1))

    print(f"Downloading {len(seasons)} seasons ({seasons[0]}-{seasons[-1]})...")

    # --- Weekly data (regular season only) ---
    weekly = nfl.import_weekly_data(seasons)
    weekly = weekly[weekly['season_type'] == 'REG']
    weekly_qb_wr = weekly[weekly['position'].isin(['QB', 'WR'])].copy()
    print(f"Weekly (REG, QB/WR): {len(weekly_qb_wr)} rows")

    # --- Snap counts (regular season only) ---
    print("Downloading snap counts...")
    snaps = nfl.import_snap_counts(seasons)
    snaps = snaps[snaps['game_type'] == 'REG']
    snaps = snaps[['pfr_player_id', 'season', 'week', 'offense_snaps']].copy()
    print(f"Snap counts (REG): {len(snaps)} rows")

    # --- ID crosswalk: pfr_id -> gsis_id ---
    print("Downloading ID crosswalk...")
    ids = nfl.import_ids()
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
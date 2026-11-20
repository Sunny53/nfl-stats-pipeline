import logging

import nflreadpy as nfl
import pandas as pd


logger = logging.getLogger(__name__)


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
    current_season = nfl.get_current_season()
    last_completed_season = current_season - 1
    seasons = list(range(2015, last_completed_season + 1))

    logger.info(
        "Downloading %d seasons (%d-%d)...",
        len(seasons),
        seasons[0],
        seasons[-1],
    )

    # --- Weekly data (regular season only) ---
    weekly = _to_pandas(nfl.load_player_stats(seasons, summary_level="week"))
    weekly = weekly.rename(
        columns={
            "team": "recent_team",
            "passing_interceptions": "interceptions",
        }
    )
    required_weekly_columns = {
        "season_type", "player_id", "player_name", "position", "season", "week",
        "recent_team", "attempts", "completions", "passing_yards", "passing_tds",
        "interceptions", "targets", "receptions", "receiving_yards",
        "receiving_tds",
    }
    missing_weekly_columns = required_weekly_columns.difference(weekly.columns)
    if missing_weekly_columns:
        missing = ", ".join(sorted(missing_weekly_columns))
        raise KeyError(
            f"nflreadpy player stats are missing required columns: {missing}"
        )
    weekly = weekly[weekly['season_type'] == 'REG']
    weekly_qb_wr = weekly[weekly['position'].isin(['QB', 'WR'])].copy()
    logger.info("Weekly (REG, QB/WR): %d rows", len(weekly_qb_wr))

    # --- Snap counts (regular season only) ---
    logger.info("Downloading snap counts...")
    snaps = _to_pandas(nfl.load_snap_counts(seasons))
    required_snap_columns = {
        "game_type", "pfr_player_id", "season", "week", "offense_snaps",
    }
    missing_snap_columns = required_snap_columns.difference(snaps.columns)
    if missing_snap_columns:
        missing = ", ".join(sorted(missing_snap_columns))
        raise KeyError(
            f"nflreadpy snap counts are missing required columns: {missing}"
        )
    snaps = snaps[snaps['game_type'] == 'REG']
    snaps = snaps[['pfr_player_id', 'season', 'week', 'offense_snaps']].copy()
    logger.info("Snap counts (REG): %d rows", len(snaps))

    # --- ID crosswalk: pfr_id -> gsis_id ---
    logger.info("Downloading ID crosswalk...")
    ids = _to_pandas(nfl.load_ff_playerids())
    if 'pfr_id' not in ids.columns or 'gsis_id' not in ids.columns:
        raise KeyError("nflreadpy player IDs are missing 'pfr_id' or 'gsis_id'")
    crosswalk = ids[['pfr_id', 'gsis_id']].dropna(subset=['pfr_id', 'gsis_id'])
    crosswalk = crosswalk.drop_duplicates(subset='pfr_id')

    # Map pfr_player_id -> gsis_id on snap counts
    snaps = snaps.merge(crosswalk, left_on='pfr_player_id', right_on='pfr_id', how='left')
    crosswalk_misses = int(snaps['gsis_id'].isna().sum())
    logger.info(
        "Crosswalk misses: dropped %d snap-count rows without a GSIS ID",
        crosswalk_misses,
    )
    snaps = snaps.dropna(subset=['gsis_id'])
    snaps = snaps[['gsis_id', 'season', 'week', 'offense_snaps']]
    logger.info("Snap counts after ID mapping: %d rows", len(snaps))

    # --- Merge snap counts onto weekly data ---
    snap_match_status = weekly_qb_wr[['player_id', 'season', 'week']].merge(
        snaps[['gsis_id', 'season', 'week']].drop_duplicates(),
        left_on=['player_id', 'season', 'week'],
        right_on=['gsis_id', 'season', 'week'],
        how='left',
        indicator=True,
    )
    snap_merge_misses = int(snap_match_status['_merge'].eq('left_only').sum())
    logger.info(
        "Snap-merge misses: dropped %d weekly rows without a snap-count match",
        snap_merge_misses,
    )
    weekly_qb_wr = weekly_qb_wr.merge(
        snaps,
        left_on=['player_id', 'season', 'week'],
        right_on=['gsis_id', 'season', 'week'],
        how='inner'  # inner = drop players with no snap data
    )
    logger.info("Weekly after snap merge (inner): %d rows", len(weekly_qb_wr))

    if weekly_qb_wr.empty:
        raise ValueError("No weekly QB/WR rows matched snap counts")

    return weekly_qb_wr
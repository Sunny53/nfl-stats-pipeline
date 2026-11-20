"""Unit tests for etl/transform.py.

These run offline on small hand-built DataFrames (no network, no database),
so they are fast and safe to run in CI.
"""
import pandas as pd
import pytest

from etl.transform import (
    aggregate_weekly_to_seasonal,
    apply_thresholds,
    calculate_consistency,
    calculate_metrics,
    transform_data,
)

WEEKLY_COLUMNS = [
    "player_id", "player_name", "position", "recent_team", "season", "week",
    "attempts", "completions", "passing_yards", "passing_tds", "interceptions",
    "targets", "receptions", "receiving_yards", "receiving_tds", "offense_snaps",
]


def make_weekly(rows):
    """Build a weekly DataFrame; any column not given defaults to 0."""
    df = pd.DataFrame(rows)
    for col in WEEKLY_COLUMNS:
        if col not in df.columns:
            df[col] = 0
    base = {"player_name": "Test Player", "recent_team": "SAV"}
    for col, val in base.items():
        df[col] = df[col].replace(0, val)
    return df[WEEKLY_COLUMNS]


def qb_rows(yards_by_week, player_id="QB1", season=2023, attempts=30, snaps=65):
    return [
        {"player_id": player_id, "position": "QB", "season": season,
         "week": week, "passing_yards": yds, "attempts": attempts,
         "completions": attempts // 2, "offense_snaps": snaps}
        for week, yds in enumerate(yards_by_week, start=1)
    ]


# ---------- consistency score ----------

def test_consistency_identical_weeks_scores_100():
    weekly = make_weekly(qb_rows([250, 250, 250, 250]))
    out = calculate_consistency(weekly).iloc[0]
    assert out["consistency_score"] == 100.0
    assert out["weekly_cv"] == 0.0


def test_consistency_matches_formula_for_known_values():
    # yards 100, 200, 300 -> mean 200, sample std 100 -> CV 0.5 -> score 50
    weekly = make_weekly(qb_rows([100, 200, 300]))
    out = calculate_consistency(weekly).iloc[0]
    assert out["weekly_cv"] == pytest.approx(0.5)
    assert out["consistency_score"] == pytest.approx(50.0)


def test_consistency_single_game_is_neutral_50():
    weekly = make_weekly(qb_rows([300]))
    out = calculate_consistency(weekly).iloc[0]
    assert out["consistency_score"] == 50.0


def test_consistency_zero_production_scores_0():
    weekly = make_weekly(qb_rows([0, 0, 0]))
    out = calculate_consistency(weekly).iloc[0]
    assert out["consistency_score"] == 0.0


def test_consistency_is_floored_at_zero_for_extreme_volatility():
    # one huge game, rest near zero -> CV far above 1 -> clamp at 0, never negative
    weekly = make_weekly(qb_rows([0, 0, 0, 0, 0, 0, 0, 500]))
    out = calculate_consistency(weekly).iloc[0]
    assert out["consistency_score"] == 0.0


def test_consistency_treats_null_yards_as_zero():
    rows = qb_rows([200, None, 200])
    weekly = make_weekly(rows)
    out = calculate_consistency(weekly).iloc[0]
    assert 0.0 <= out["consistency_score"] <= 100.0


def test_consistency_uses_receiving_yards_for_wr():
    rows = [
        {"player_id": "WR1", "position": "WR", "season": 2023, "week": w,
         "receiving_yards": 80, "targets": 8, "offense_snaps": 60}
        for w in range(1, 5)
    ]
    out = calculate_consistency(make_weekly(rows)).iloc[0]
    assert out["consistency_score"] == 100.0


def test_consistency_skips_other_positions():
    rows = [{"player_id": "RB1", "position": "RB", "season": 2023, "week": 1}]
    assert calculate_consistency(make_weekly(rows)).empty


# ---------- seasonal aggregation ----------

def test_aggregate_sums_volume_and_counts_games():
    weekly = make_weekly(qb_rows([200, 300, 250], attempts=30, snaps=60))
    seasonal = aggregate_weekly_to_seasonal(weekly).iloc[0]
    assert seasonal["games"] == 3
    assert seasonal["passing_yards"] == 750
    assert seasonal["attempts"] == 90
    assert seasonal["offense_snaps"] == 180


def test_aggregate_keeps_seasons_separate():
    rows = qb_rows([200, 200], season=2022) + qb_rows([300, 300], season=2023)
    seasonal = aggregate_weekly_to_seasonal(make_weekly(rows))
    assert len(seasonal) == 2
    assert set(seasonal["season"]) == {2022, 2023}


# ---------- metrics ----------

def test_snap_efficiency_is_yards_per_offensive_snap():
    weekly = make_weekly(qb_rows([200, 300], attempts=30, snaps=50))
    seasonal = aggregate_weekly_to_seasonal(weekly)
    out = calculate_metrics(seasonal, weekly).iloc[0]
    # 500 yards / 100 snaps
    assert out["snap_efficiency"] == pytest.approx(5.0)


def test_qb_yards_per_attempt():
    weekly = make_weekly(qb_rows([200, 300], attempts=25, snaps=50))
    seasonal = aggregate_weekly_to_seasonal(weekly)
    out = calculate_metrics(seasonal, weekly).iloc[0]
    # 500 yards / 50 attempts
    assert out["yards_per_attempt"] == pytest.approx(10.0)


# ---------- thresholds ----------

def test_thresholds_filter_unqualified_players():
    df = pd.DataFrame([
        {"position": "QB", "attempts": 250, "targets": 0},   # qualifies
        {"position": "QB", "attempts": 199, "targets": 0},   # just under
        {"position": "WR", "attempts": 0, "targets": 40},    # qualifies
        {"position": "WR", "attempts": 0, "targets": 39},    # just under
        {"position": "TE", "attempts": 0, "targets": 90},    # wrong position
    ])
    qualified = apply_thresholds(df)
    assert len(qualified) == 2
    assert set(qualified["position"]) == {"QB", "WR"}


# ---------- end to end ----------

def test_transform_data_returns_expected_schema_and_one_row_per_player_season():
    rows = []
    for season in (2022, 2023):
        rows += qb_rows([250] * 17, player_id="QB1", season=season, attempts=30, snaps=65)
    rows += [
        {"player_id": "WR1", "position": "WR", "season": 2023, "week": w,
         "receiving_yards": 70, "targets": 8, "offense_snaps": 60}
        for w in range(1, 18)
    ]
    players, seasons = transform_data(make_weekly(rows))

    assert set(players["position"]) == {"QB", "WR"}
    assert players["player_id"].is_unique
    assert not seasons.duplicated(subset=["player_id", "season_year"]).any()
    expected_cols = {
        "player_id", "season_year", "team", "games", "snaps", "attempts",
        "completions", "yards", "tds", "ints", "snap_efficiency",
        "yards_per_attempt", "weekly_cv", "consistency_score",
    }
    assert expected_cols == set(seasons.columns)
    assert seasons["consistency_score"].between(0, 100).all()


def test_transform_data_with_no_qualified_players_returns_empty_frames():
    weekly = make_weekly(qb_rows([100, 100], attempts=5))  # far below 200 attempts
    players, seasons = transform_data(weekly)
    assert players.empty and seasons.empty


def test_player_dimension_keeps_latest_name_for_player_id():
    rows = (
        qb_rows([250] * 7, player_id="QB1", season=2022)
        + qb_rows([260] * 7, player_id="QB1", season=2023)
    )
    for row in rows:
        row["player_name"] = "Older Name" if row["season"] == 2022 else "Latest Name"

    players, _ = transform_data(make_weekly(rows))

    assert players.loc[players["player_id"] == "QB1", "name"].tolist() == [
        "Latest Name"
    ]


def test_player_dimension_keeps_latest_position_for_player_id():
    rows = qb_rows([250] * 7, player_id="PLAYER1", season=2022)
    rows.extend([
        {
            "player_id": "PLAYER1",
            "player_name": "Test Player",
            "position": "WR",
            "season": 2023,
            "week": week,
            "receiving_yards": 80,
            "targets": 8,
            "receptions": 6,
            "offense_snaps": 60,
        }
        for week in range(1, 6)
    ])

    players, _ = transform_data(make_weekly(rows))

    assert players.loc[players["player_id"] == "PLAYER1", "position"].tolist() == [
        "WR"
    ]


def test_player_dimension_has_unique_player_ids():
    rows = (
        qb_rows([250] * 7, player_id="QB1", season=2022)
        + qb_rows([260] * 7, player_id="QB1", season=2023)
        + qb_rows([240] * 7, player_id="QB2", season=2023)
    )
    for row in rows:
        row["player_name"] = f"{row['player_id']} {row['season']}"

    players, _ = transform_data(make_weekly(rows))

    assert players["player_id"].is_unique


# ---------- WR yards per target ----------

def test_wr_yards_per_target_uses_targets_not_attempts():
    rows = [
        {"player_id": "WR1", "position": "WR", "season": 2023, "week": w,
         "receiving_yards": 80, "targets": 8, "receptions": 6, "offense_snaps": 60}
        for w in range(1, 18)
    ]
    weekly = make_weekly(rows)
    seasonal = aggregate_weekly_to_seasonal(weekly)
    out = calculate_metrics(seasonal, weekly).iloc[0]
    # 1360 yards / 136 targets
    assert out["yards_per_attempt"] == pytest.approx(10.0)

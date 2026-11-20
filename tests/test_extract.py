import logging
import sys
from types import ModuleType
from unittest.mock import patch

import pandas as pd
import pytest

with patch.dict(sys.modules, {"nflreadpy": ModuleType("nflreadpy")}):
    from etl import extract


def _mock_nfl_data(monkeypatch, weekly, snaps, crosswalk):
    calls = {}

    monkeypatch.setattr(
        extract.nfl, "get_current_season", lambda: 2026, raising=False
    )

    def load_player_stats(seasons, summary_level):
        calls["player_stats"] = (seasons, summary_level)
        return _PolarsFrame(weekly)

    def load_snap_counts(seasons):
        calls["snap_counts"] = seasons
        return _PolarsFrame(snaps)

    def load_ff_playerids():
        return _PolarsFrame(crosswalk)

    monkeypatch.setattr(
        extract.nfl, "load_player_stats", load_player_stats, raising=False
    )
    monkeypatch.setattr(
        extract.nfl, "load_snap_counts", load_snap_counts, raising=False
    )
    monkeypatch.setattr(
        extract.nfl, "load_ff_playerids", load_ff_playerids, raising=False
    )
    return calls


class _PolarsFrame:
    def __init__(self, pandas_frame):
        self.pandas_frame = pandas_frame

    def to_pandas(self):
        return self.pandas_frame.copy()


def _weekly_rows(player_ids):
    return pd.DataFrame({
        "season_type": ["REG"] * len(player_ids),
        "position": ["QB"] * len(player_ids),
        "player_id": player_ids,
        "season": [2023] * len(player_ids),
        "week": [1] * len(player_ids),
        "player_name": ["Test Player"] * len(player_ids),
        "player_display_name": ["Canonical Test Player"] * len(player_ids),
        "team": ["NYJ"] * len(player_ids),
        "attempts": [20] * len(player_ids),
        "completions": [10] * len(player_ids),
        "passing_yards": [100] * len(player_ids),
        "passing_tds": [1] * len(player_ids),
        "passing_interceptions": [0] * len(player_ids),
        "targets": [0] * len(player_ids),
        "receptions": [0] * len(player_ids),
        "receiving_yards": [0] * len(player_ids),
        "receiving_tds": [0] * len(player_ids),
    })


def _snap_rows():
    return pd.DataFrame([
        {
            "game_type": "REG",
            "pfr_player_id": "pfr-1",
            "season": 2023,
            "week": 1,
            "offense_snaps": 50,
        },
        {
            "game_type": "REG",
            "pfr_player_id": "pfr-unmapped",
            "season": 2023,
            "week": 1,
            "offense_snaps": 25,
        },
    ])


def test_extract_logs_crosswalk_and_snap_merge_misses(monkeypatch, caplog):
    calls = _mock_nfl_data(
        monkeypatch,
        _weekly_rows(["gsis-1", "gsis-2"]),
        _snap_rows(),
        pd.DataFrame([{"pfr_id": "pfr-1", "gsis_id": "gsis-1"}]),
    )

    with caplog.at_level(logging.INFO, logger="etl.extract"):
        result = extract.extract_all_data()

    assert result["player_id"].tolist() == ["gsis-1"]
    assert result["player_name"].tolist() == ["Canonical Test Player"]
    assert result["recent_team"].tolist() == ["NYJ"]
    assert result["interceptions"].tolist() == [0]
    assert result["offense_snaps"].tolist() == [50]
    expected_seasons = list(range(2015, 2026))
    assert calls["player_stats"] == (expected_seasons, "week")
    assert calls["snap_counts"] == expected_seasons
    assert "Crosswalk misses: dropped 1" in caplog.text
    assert "Snap-merge misses: dropped 1" in caplog.text


def test_extract_raises_when_no_weekly_rows_match_snaps(monkeypatch):
    _mock_nfl_data(
        monkeypatch,
        _weekly_rows(["gsis-2"]),
        _snap_rows(),
        pd.DataFrame([{"pfr_id": "pfr-1", "gsis_id": "gsis-1"}]),
    )

    with pytest.raises(ValueError, match="No weekly QB/WR rows matched snap counts"):
        extract.extract_all_data()
